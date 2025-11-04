from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from jinja2 import TemplateSyntaxError
try:
    from docxtpl.exceptions import TemplateError as DocxTplTemplateError
except Exception:
    DocxTplTemplateError = None
import os
import tempfile
# import pandas as pd  # 延迟导入以避免启动时超时
from datetime import datetime
import logging
import threading
import time
from pathlib import Path
import re
import json
from werkzeug.utils import secure_filename

# 全局变量用于延迟导入
pd = None

def ensure_pandas_imported():
    """确保pandas已导入"""
    global pd
    if pd is None:
        logger.info("开始导入pandas...")
        import pandas as pandas_module
        pd = pandas_module
        logger.info("pandas导入完成")
    return pd

# 导入Flask相关模块
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# 设置日志记录器
logger = logging.getLogger(__name__)

# 延迟导入OCR相关模块，避免启动时失败
template_handler = None
ocr_service = None

# 导入状态管理器
try:
    from stage_manager import StageManager
    STAGE_MANAGER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"状态管理器导入失败: {str(e)}")
    STAGE_MANAGER_AVAILABLE = False

# 导入优化的OCR服务
try:
    from ocr_service_optimized import OptimizedOCRService as OCRService
    OCR_SERVICE_AVAILABLE = True
    logger.info("优化OCR服务导入成功")
except ImportError as e:
    logger.warning(f"OCR服务导入失败: {str(e)}")
    OCR_SERVICE_AVAILABLE = False

# 尝试导入模板处理器
try:
    from template_handler import TemplateHandler
    TEMPLATE_HANDLER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"模板处理器导入失败: {str(e)}")
    TEMPLATE_HANDLER_AVAILABLE = False

# 创建Flask应用
app = Flask(__name__)

# 简化配置
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 设置日志记录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# 生产环境使用不同的日志配置
env = os.environ.get('FLASK_ENV', 'development')
if env == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )
else:
    # 开发环境输出到控制台，方便调试
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

# 初始化OCR服务（容错处理）
try:
    if OCR_SERVICE_AVAILABLE:
        ocr_service = OCRService()
        logger.info("OCR服务初始化成功")
    else:
        logger.warning("OCR服务不可用：导入失败")
        ocr_service = None
except Exception as e:
    logger.warning(f"OCR服务初始化失败: {str(e)}")
    ocr_service = None

# 模板处理器将在需要时初始化
template_handler = None
if TEMPLATE_HANDLER_AVAILABLE:
    logger.info("模板处理器类可用")
else:
    logger.warning("模板处理器不可用：导入失败")

# 存储最后导入时间
last_import_time = None

# 初始化状态管理器（按请求动态选择数据文件，不在启动时绑定固定Excel）
stage_manager = None
if STAGE_MANAGER_AVAILABLE:
    try:
        # 不在此处绑定具体Excel，避免不同用户互相影响
        logger.info("状态管理器类已加载，实例按请求动态创建")
    except Exception as e:
        logger.warning(f"状态管理器初始化提示: {str(e)}")
        stage_manager = None

# 根据当前登录用户选择对应的数据源Excel
def get_user_excel_path():
    """返回当前用户应使用的Excel数据文件路径。
    - Giko 使用 giko.xlsx
    - 其他用户（含 Esther）使用 六大战区简道云客户.xlsx
    若目标文件不存在，记录日志并回退到六大战区简道云客户.xlsx。
    """
    try:
        user = (session.get('user') or '').strip().lower()
    except Exception:
        user = ''
    filename = 'giko.xlsx' if user == 'giko' else '六大战区简道云客户.xlsx'
    path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(path):
        fallback = os.path.join(os.getcwd(), '六大战区简道云客户.xlsx')
        logger.warning(f"数据文件不存在: {path}，回退到 {fallback}")
        return fallback
    return path

# 自动监控相关变量
auto_monitor_enabled = False
monitor_thread = None
monitor_lock = threading.Lock()
last_monitor_check = None
monitor_results = {'recent_contracts': [], 'updated_contracts': [], 'last_check': None}
# 已处理文件记录（文件路径 -> 处理时间戳）
processed_files = {}

# 销售代表姓名标准化函数
def normalize_sales_name(sales_name):
    """
    标准化销售代表姓名，解决大小写不一致问题
    例如：Esther.zhu 和 Esther.Zhu 都标准化为 Esther.Zhu
    """
    if not sales_name or str(sales_name).lower() == 'nan':
        return ''
    
    # 检查是否为pandas的NaN值
    try:
        pd = ensure_pandas_imported()
        if pd.isna(sales_name):
            return ''
    except:
        # 如果pandas不可用，使用简单的检查
        if sales_name is None or (hasattr(sales_name, '__len__') and len(str(sales_name).strip()) == 0):
            return ''
    
    name = str(sales_name).strip()
    if not name:
        return ''
    
    # 特殊处理已知的销售代表姓名
    name_lower = name.lower()
    if name_lower == 'esther.zhu':
        return 'Esther.Zhu'
    elif name_lower == 'mia.mi':
        return 'Mia.Mi'
    
    # 对于其他姓名，保持原有格式但确保首字母大写
    return name

def get_normalized_sales_person(row):
    """
    从数据行中获取标准化的销售代表姓名
    优先使用续费责任销售，如果为空则使用责任销售中英文
    """
    sales_raw = row.get('续费责任销售', '')
    
    # 检查是否为空值
    is_empty = False
    if not sales_raw or sales_raw == '' or str(sales_raw).lower() == 'nan':
        is_empty = True
    else:
        # 检查是否为pandas的NaN值
        try:
            pd = ensure_pandas_imported()
            if pd.isna(sales_raw):
                is_empty = True
        except:
            pass
    
    if is_empty:
        sales_person = str(row.get('责任销售中英文', ''))
    else:
        sales_person = str(sales_raw)
    
    return normalize_sales_name(sales_person)

# 健康检查端点
@app.route('/health')
def health_check():
    """健康检查端点，用于监控服务状态"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'development'),
            'services': {
                'flask': 'available',
                'template_handler': 'available' if TEMPLATE_HANDLER_AVAILABLE else 'unavailable',
                'ocr_service': 'available' if ocr_service else 'unavailable'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# 添加安全头
@app.after_request
def add_security_headers(response):
    if app.config.get('DEBUG'):
        # 开发环境使用宽松的CSP
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"
    else:
        # 生产环境使用更严格的安全头
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if (username == 'Esther' and password == '967420') or (username == 'Giko' and password == '549030'):  # 简单的用户名密码验证
            session['logged_in'] = True
            session['user'] = username
            # 简单角色划分：Esther 管理/运营，Giko 销售
            session['role'] = 'admin' if username == 'Esther' else 'sales'
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

# 登出功能
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('login'))

# 登录保护装饰器
def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# 加载Excel数据
def load_customer_data():
    global last_import_time
    excel_path = get_user_excel_path()
    try:
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return None
        pd = ensure_pandas_imported()
        df = pd.read_excel(excel_path)
        # 统一常见列名别名，兼容不同数据来源
        try:
            if '用户ID' not in df.columns and '简道云ID' in df.columns:
                df.rename(columns={'简道云ID': '用户ID'}, inplace=True)
            if '到期日期' not in df.columns and '到期时间' in df.columns:
                df.rename(columns={'到期时间': '到期日期'}, inplace=True)
            if '到期日期' not in df.columns and '试用到期时间' in df.columns:
                df.rename(columns={'试用到期时间': '到期日期'}, inplace=True)
            if '公司名称' not in df.columns and '账号-企业名称' in df.columns:
                df.rename(columns={'账号-企业名称': '公司名称'}, inplace=True)
        except Exception:
            pass
        return df
    except Exception as e:
        logger.error(f"Excel加载错误: {str(e)}")
        return None

@app.route('/')
@login_required
def index():
    role = session.get('role', 'admin')
    if role == 'sales':
        return render_template('sales_dashboard.html', last_import_time=last_import_time)
    return render_template('index.html', last_import_time=last_import_time)

# 销售跟进日记：支持GET/POST，采用JSONL追加，不覆盖
@app.route('/sales_diary', methods=['GET', 'POST'])
@login_required
def sales_diary():
    diary_path = os.path.join(os.getcwd(), 'uploads', 'sales_diary.jsonl')
    os.makedirs(os.path.dirname(diary_path), exist_ok=True)
    if request.method == 'POST':
        try:
            data = request.get_json(silent=True) or {}
            entry = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'author': session.get('username') or 'unknown',
                'jdy_account': (data.get('jdy_account') or '').strip(),
                'customer_name': (data.get('customer_name') or '').strip(),
                'note': (data.get('note') or '').strip()
            }
            if not entry['jdy_account'] or not entry['note']:
                return jsonify({'success': False, 'error': '缺少必填项'}), 400
            with open(diary_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            return jsonify({'success': True, 'entry': entry})
        except Exception as e:
            logger.error(f"保存日记失败: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    # GET: 返回最近100条，按时间倒序；支持可选账号过滤
    entries = []
    if os.path.exists(diary_path):
        try:
            with open(diary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"读取日记失败: {str(e)}")
            entries = []
    # 可选过滤
    jdy_param = (request.args.get('jdy_account') or '').strip()
    if jdy_param:
        entries = [e for e in entries if str(e.get('jdy_account','')).strip() == jdy_param]
    entries = entries[-100:][::-1]
    return jsonify({'success': True, 'entries': entries, 'filtered_by': jdy_param or None})

@app.route('/test', methods=['GET'])
def test():
    return 'Hello, World!'

# 账号验证：检查Excel中是否存在该简道云账号，并返回基础信息
@app.route('/verify_jdy_account', methods=['POST'])
@login_required
def verify_jdy_account():
    try:
        data = request.get_json(silent=True) or {}
        jdy_account = str(data.get('jdy_account', '')).strip()
        if not jdy_account:
            return jsonify({'success': False, 'error': '请提供简道云账号'}), 400

        excel_path = get_user_excel_path()
        if not os.path.exists(excel_path):
            return jsonify({'success': False, 'error': '数据文件不存在'}), 500

        pd = ensure_pandas_imported()
        try:
            df = pd.read_excel(excel_path)
        except Exception as e:
            logger.error(f"读取Excel失败: {str(e)}")
            return jsonify({'success': False, 'error': '数据文件读取失败'}), 500

        # 统一为字符串进行匹配（包含匹配，兼容完整或部分输入）
        matches = df[df['用户ID'].astype(str).str.contains(jdy_account, case=False, na=False)]
        exists = not matches.empty
        info = None
        if exists:
            row = matches.iloc[0]
            info = {
                'jdy_account': str(row.get('用户ID', '')),
                'company_name': str(row.get('公司名称', '')) or str(row.get('账号-企业名称', '')),
                'tax_number': str(row.get('纳税人识别号', '')) or str(row.get('账号-纳税人识别号', '')),
                'integration_mode': str(row.get('集成模式', '')),
                'customer_classification': str(row.get('客户分类', ''))
            }
        return jsonify({'success': True, 'exists': exists, 'matched_count': int(len(matches)), 'info': info})
    except Exception as e:
        logger.error(f"账号验证失败: {str(e)}")
        return jsonify({'success': False, 'error': '账号验证服务异常'}), 500

# 单账号历史跟进记录查询：返回该账号的所有历史记录（完整信息）
@app.route('/sales_diary_query', methods=['GET'])
@login_required
def sales_diary_query():
    try:
        jdy_account = str(request.args.get('jdy_account', '')).strip()
        if not jdy_account:
            return jsonify({'success': False, 'error': '请提供简道云账号'}), 400
        diary_path = os.path.join(os.getcwd(), 'uploads', 'sales_diary.jsonl')
        entries = []

        # 1) 读取 JSONL 追加的跟进日记
        if os.path.exists(diary_path):
            try:
                with open(diary_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            obj = json.loads(line)
                            if str(obj.get('jdy_account', '')).strip() == jdy_account:
                                entries.append(obj)
                        except Exception:
                            continue
            except Exception:
                pass

        # 2) 兼容从 Excel 中读取“跟进记录/跟进日期”并合并（只读，不写）
        try:
            excel_path = get_user_excel_path()
            if os.path.exists(excel_path):
                pd = ensure_pandas_imported()
                df = pd.read_excel(excel_path)
                # 列名归一化
                try:
                    if '用户ID' not in df.columns and '简道云ID' in df.columns:
                        df.rename(columns={'简道云ID': '用户ID'}, inplace=True)
                    if '公司名称' not in df.columns and '账号-企业名称' in df.columns:
                        df.rename(columns={'账号-企业名称': '公司名称'}, inplace=True)
                    if '跟进日期' not in df.columns and '跟进时间' in df.columns:
                        df.rename(columns={'跟进时间': '跟进日期'}, inplace=True)
                    if '跟进记录' not in df.columns and '跟进日记' in df.columns:
                        df.rename(columns={'跟进日记': '跟进记录'}, inplace=True)
                except Exception:
                    pass

                if '用户ID' in df.columns:
                    matches = df[df['用户ID'].astype(str).str.contains(jdy_account, case=False, na=False)]
                    for _, row in matches.iterrows():
                        note = row.get('跟进记录', '')
                        date_val = row.get('跟进日期', '')
                        if note is not None and str(note).strip() and str(note).lower() != 'nan':
                            # 尝试格式化日期
                            ts = ''
                            try:
                                if pd.notna(date_val) and str(date_val).strip() and str(date_val).lower() != 'nan':
                                    ts = pd.to_datetime(date_val).strftime('%Y-%m-%d')
                            except Exception:
                                ts = ''
                            entries.append({
                                'timestamp': ts or datetime.now().strftime('%Y-%m-%d'),
                                'author': 'excel',
                                'jdy_account': str(row.get('用户ID', '')),
                                'customer_name': str(row.get('公司名称', '')),
                                'note': str(note)
                            })
        except Exception as e:
            logger.warning(f"从Excel合并日记失败: {str(e)}")

        # 合并后按时间升序
        entries.sort(key=lambda x: x.get('timestamp', ''))
        return jsonify({'success': True, 'entries': entries, 'total': len(entries)})
    except Exception as e:
        logger.error(f"查询跟进记录失败: {str(e)}")
        return jsonify({'success': False, 'error': '查询服务异常'}), 500
@app.route('/upload_excel', methods=['POST'])
@login_required
def upload_excel():
    global last_import_time
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
            
        file = request.files['file']
        if not file or not file.filename:
            return jsonify({'error': '没有选择文件'}), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': '请上传Excel文件(.xlsx)'}), 400

        # 原子写入保存文件：临时文件 + os.replace
        target_path = get_user_excel_path()
        tmp_fd, tmp_path = tempfile.mkstemp(prefix='upload_', suffix='.xlsx', dir=os.path.dirname(target_path))
        os.close(tmp_fd)
        try:
            file.save(tmp_path)
            os.replace(tmp_path, target_path)
        except Exception as save_err:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass
            logger.error(f"保存文件失败: {str(save_err)}")
            return jsonify({'error': f'文件保存失败: {str(save_err)}'}), 500
        
        # 更新导入时间
        last_import_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'message': '文件上传成功',
            'last_import_time': last_import_time
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/get_last_import_time')
def get_last_import_time():
    return jsonify({'last_import_time': last_import_time})

# 前端错误日志接收接口（无需登录）
@app.route('/log_client_error', methods=['POST'])
def log_client_error():
    try:
        data = request.get_json(silent=True) or {}
        errs = data.get('errors') or []
        ua = data.get('ua') or request.headers.get('User-Agent', '')
        page = data.get('page') or request.path
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        count = 0
        if isinstance(errs, list) and errs:
            for e in errs:
                try:
                    endpoint = e.get('endpoint')
                    msg = e.get('error')
                    ts = e.get('time')
                    logger.warning(f"前端错误: endpoint={endpoint} error={msg} time={ts} ua={ua} page={page} ip={ip}")
                    count += 1
                except Exception:
                    continue
        else:
            # 单条错误或格式不标准
            logger.warning(f"前端错误: {errs} ua={ua} page={page} ip={ip}")
            count = 1
        return jsonify({'success': True, 'logged': count}), 200
    except Exception as exc:
        logger.error(f"记录前端错误失败: {str(exc)}")
        return jsonify({'success': False, 'error': '日志记录失败'}), 500

@app.route('/get_monthly_revenue')
@login_required
def get_monthly_revenue():
    """获取本月收款总金额"""
    try:
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'revenue': 0, 'error': '数据文件不存在'}), 500

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'revenue': 0, 'error': '数据文件读取失败'}), 500

        # 获取当前月份
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # 计算本月收款总金额
        monthly_revenue = 0
        
        # 检查是否有收款相关的列
        revenue_columns = ['收款金额', '回款金额', '本月收款', '收款', '回款']
        found_column = None
        
        for col in revenue_columns:
            if col in df.columns:
                found_column = col
                break
        
        if found_column:
            # 如果有收款日期列，按月份筛选
            if '收款日期' in df.columns or '回款日期' in df.columns:
                date_col = '收款日期' if '收款日期' in df.columns else '回款日期'
                for _, row in df.iterrows():
                    if pd.notna(row[date_col]) and pd.notna(row[found_column]):
                        try:
                            payment_date = pd.to_datetime(row[date_col])
                            if payment_date.month == current_month and payment_date.year == current_year:
                                amount = float(str(row[found_column]).replace(',', '').replace('元', ''))
                                monthly_revenue += amount
                        except Exception as e:
                            continue
            else:
                # 如果没有日期列，使用所有有效的收款金额
                for _, row in df.iterrows():
                    if pd.notna(row[found_column]):
                        try:
                            amount = float(str(row[found_column]).replace(',', '').replace('元', ''))
                            monthly_revenue += amount
                        except Exception as e:
                            continue
        
        logger.info(f"本月收款总金额: {monthly_revenue}元")
        return jsonify({'revenue': monthly_revenue})

    except Exception as e:
        logger.error(f"获取收款数据失败: {str(e)}")
        return jsonify({'revenue': 0, 'error': f'获取收款数据失败: {str(e)}'}), 500

@app.route('/get_future_expiring_customers')
@login_required
def get_future_expiring_customers():
    try:
        # 获取筛选参数：支持销售筛选（兼容旧参数）与战区多选筛选
        sales_filter = request.args.get('sales_filter', 'all')
        # 可选：支持自定义天数范围，默认显示未来第8天到第33天
        try:
            min_days = int(request.args.get('min_days', 8))
        except Exception:
            min_days = 8
        try:
            max_days = int(request.args.get('max_days', 33))
        except Exception:
            max_days = 33
        if max_days < min_days:
            max_days = min_days
        # 既支持多次传入 ?zones=A&zones=B，也支持一次传入 CSV ?zones=A,B
        zones_list = request.args.getlist('zones')
        if zones_list:
            # 如果只有一个值且是逗号分隔的CSV，则进行拆分
            if len(zones_list) == 1 and isinstance(zones_list[0], str) and (',' in zones_list[0]):
                zones_list = [s.strip() for s in zones_list[0].split(',') if s.strip()]
            else:
                # 常规多值参数：统一做去空格处理
                zones_list = [str(s).strip() for s in zones_list if str(s).strip()]
        else:
            zones_csv = request.args.get('zones')
            if zones_csv:
                zones_list = [s.strip() for s in str(zones_csv).split(',') if s.strip()]
        apply_zone_filter = bool(zones_list) and not (len(zones_list) == 1 and str(zones_list[0]).lower() == 'all')
        logger.info(f"获取未来到期客户（{min_days}-{max_days}天），销售筛选: {sales_filter}，战区筛选: {zones_list if apply_zone_filter else 'all'}")
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
            # 列别名兼容：到期时间 -> 到期日期
            if '到期日期' not in df.columns and '到期时间' in df.columns:
                try:
                    df.rename(columns={'到期时间': '到期日期'}, inplace=True)
                    logger.info("兼容列名：将'到期时间'重命名为'到期日期'")
                except Exception as alias_err:
                    logger.warning(f"列名兼容失败: {str(alias_err)}")
            # 战区列兼容：支持'战区'、'所属战区'或'归属战区'
            zone_col = None
            if '战区' in df.columns:
                zone_col = '战区'
            elif '所属战区' in df.columns:
                zone_col = '所属战区'
            elif '归属战区' in df.columns:
                zone_col = '归属战区'
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        # 检查必要列并返回具体缺失项（销售列不再强制要求）
        required_columns = ['到期日期', '用户ID', '账号-企业名称']
        # 如果启用战区筛选，则需要战区列
        if apply_zone_filter and not zone_col:
            # 明确提示缺失战区列
            missing_columns = ['战区/所属战区/归属战区']
            logger.error(f"Excel文件中缺少必要列: {missing_columns}")
            return jsonify({'error': f"数据格式错误：缺少必要列 {missing_columns}"}), 500
        # 常规缺列检查
        missing_columns = [col for col in required_columns if col not in df.columns]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Excel文件中缺少必要列: {missing_columns}")
            return jsonify({'error': f'数据格式错误：缺少必要列 {missing_columns}'}), 500
        
        # 获取当前日期并计算窗口：默认未来第8天到第33天
        now = datetime.now()
        today = now.date()
        window_start = pd.Timestamp(today) + pd.Timedelta(days=min_days)
        window_end = pd.Timestamp(today) + pd.Timedelta(days=max_days)
        
        # 筛选出指定天数范围内（min_days-max_days）将要过期的客户
        future_customers = []

        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期']).normalize()
                    # 如果过期时间在min_days-max_days窗口内
                    if window_start <= expiry_date <= window_end:
                        # 使用标准化函数获取销售代表姓名
                        sales_person = get_normalized_sales_person(row)
                        # 战区筛选
                        if apply_zone_filter:
                            # 如果战区列缺失（未在前面返回错误），则跳过筛选
                            if zone_col:
                                zone_value = row.get(zone_col, '')
                                # 兼容NaN与字符串空白
                                try:
                                    is_nan = pd.isna(zone_value)
                                except Exception:
                                    is_nan = False
                                zone_value_str = '' if (zone_value is None or is_nan) else str(zone_value).strip()
                                if zone_value_str not in zones_list:
                                    continue
                        else:
                            # 兼容旧的销售筛选参数（未启用战区筛选时）
                            if sales_filter != 'all' and sales_filter != sales_person:
                                continue
                        
                        customer_info = {
                            'id': str(row.get('用户ID', '')),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'jdy_account': str(row.get('用户ID', '')),
                            'company_name': str(row.get('账号-企业名称', '')),
                            'sales_person': sales_person,
                            'zone': str(row.get(zone_col, '')) if zone_col else ''
                        }
                        
                        future_customers.append(customer_info)
                            
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按过期日期排序
        future_customers.sort(key=lambda x: x['expiry_date'])
        
        logger.info(f"找到{len(future_customers)}个即将过期的客户（销售筛选：{sales_filter}，战区筛选：{zones_list if apply_zone_filter else 'all'}）")
        return jsonify({
            'future_customers': future_customers
        })

    except Exception as e:
        logger.error(f"获取未来即将过期客户失败: {str(e)}")
        return jsonify({'error': f'获取未来即将过期客户失败: {str(e)}'}), 500

@app.route('/get_sales_representatives')
@login_required
def get_sales_representatives():
    try:
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件获取销售代表列表: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        # 收集所有销售代表姓名
        sales_representatives = set()
        
        for _, row in df.iterrows():
            # 使用标准化函数获取销售代表姓名
            sales_person = get_normalized_sales_person(row)
            
            # 添加到集合中（自动去重）
            if sales_person:
                sales_representatives.add(sales_person)
        
        # 转换为排序列表
        sales_list = sorted(list(sales_representatives))
        
        logger.info(f"找到{len(sales_list)}个销售代表")
        return jsonify({
            'sales_representatives': sales_list
        })

    except Exception as e:
        logger.error(f"获取销售代表列表失败: {str(e)}")
        return jsonify({'error': f'获取销售代表列表失败: {str(e)}'}), 500

@app.route('/get_zones')
@login_required
def get_zones():
    try:
        # 默认战区列表（按业务常用顺序），排除“简道云大区”
        default_zones_order = [
            '上海大区', '东北大区', '北京大区', '华中大区', '华北大区', '华南大区',
            '浙闵大区', '苏皖大区', '西北大区', '西南大区'
        ]

        # 优先从Excel收集战区，如果不可用则回退到默认列表
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件获取战区列表: {excel_path}")

        zones_from_excel = set()
        if os.path.exists(excel_path):
            try:
                ensure_pandas_imported()
                df = pd.read_excel(excel_path)
                logger.info(f"成功读取Excel文件，共{len(df)}行数据")

                # 战区列兼容：支持'战区'、'所属战区'或'归属战区'
                zone_col = None
                if '战区' in df.columns:
                    zone_col = '战区'
                elif '所属战区' in df.columns:
                    zone_col = '所属战区'
                elif '归属战区' in df.columns:
                    zone_col = '归属战区'

                if zone_col:
                    for _, row in df.iterrows():
                        zone_val = row.get(zone_col, '')
                        try:
                            is_nan = pd.isna(zone_val)
                        except Exception:
                            is_nan = False
                        if zone_val is None or is_nan:
                            continue
                        zone_str = str(zone_val).strip()
                        if zone_str and zone_str != '简道云大区':
                            zones_from_excel.add(zone_str)
                else:
                    logger.warning("Excel文件中缺少战区列 ['战区'、'所属战区'、'归属战区']，将仅使用默认战区列表")
            except Exception as e:
                logger.warning(f"Excel读取或解析战区失败，将使用默认战区列表: {str(e)}")
        else:
            logger.warning(f"数据文件不存在: {excel_path}，将使用默认战区列表")

        # 合并默认战区与Excel战区，保持默认顺序，其余追加在后
        merged_zones = []
        seen = set()
        for z in default_zones_order:
            if z not in seen:
                merged_zones.append(z)
                seen.add(z)
        for z in sorted(zones_from_excel):
            if z not in seen:
                merged_zones.append(z)
                seen.add(z)

        logger.info(f"返回{len(merged_zones)}个战区（含默认与Excel提取，已排除简道云大区）")
        return jsonify({'zones': merged_zones})

    except Exception as e:
        logger.error(f"获取战区列表失败: {str(e)}")
        return jsonify({'error': f'获取战区列表失败: {str(e)}'}), 500

@app.route('/get_unsigned_customers')
@login_required
def get_unsigned_customers():
    """获取未来8-33天内客户数据，支持状态筛选"""
    try:
        # 获取筛选参数
        status_filter = request.args.get('status', 'all')  # all, na, contract, invoice, paid
        # 可选：支持自定义天数范围，默认未来第8天到第33天
        try:
            min_days = int(request.args.get('min_days', 8))
        except Exception:
            min_days = 8
        try:
            max_days = int(request.args.get('max_days', 33))
        except Exception:
            max_days = 33
        if max_days < min_days:
            max_days = min_days
        
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'customers': [], 'error': '数据文件不存在'}), 500

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
            # 列别名兼容：部分数据使用“到期时间”，统一重命名为“到期日期”
            if '到期日期' not in df.columns and '到期时间' in df.columns:
                try:
                    df.rename(columns={'到期时间': '到期日期'}, inplace=True)
                    logger.info("兼容列名：将'到期时间'重命名为'到期日期'")
                except Exception as alias_err:
                    logger.warning(f"列名兼容失败: {str(alias_err)}")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'customers': [], 'error': '数据文件读取失败'}), 500

        # 检查必要的列是否存在（到期日期已在上方做过别名兼容）
        required_columns = ['用户ID', '账号-企业名称', '到期日期', '客户阶段']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Excel文件中缺少必要列: {missing_columns}")
            return jsonify({'customers': [], 'error': f'数据格式错误：缺少必要列 {missing_columns}'}), 500
        
        # 获取当前日期
        now = datetime.now()
        today = now.date()
        eight_days_later = today + pd.Timedelta(days=min_days)
        thirty_three_days_later = today + pd.Timedelta(days=max_days)
        
        # 筛选出未来30天内到期的客户
        filtered_customers = []
        for _, row in df.iterrows():
            # 检查到期日期是否在未来8-33天内
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期']).date()
                    # 如果到期日期在未来8-33天内
                    if eight_days_later <= expiry_date <= thirty_three_days_later:
                        # 获取客户阶段
                        customer_stage = row.get('客户阶段', '')
                        stage_normalized = ''
                        if pd.notna(customer_stage) and str(customer_stage).strip() != '' and str(customer_stage).lower() != 'nan':
                            stage_normalized = str(customer_stage).strip()
                        
                        # 根据状态筛选
                        should_include = False
                        if status_filter == 'all':
                            should_include = True
                        # NA 兼容：空值或显式字符串 "NA"
                        elif status_filter == 'na' and (stage_normalized == '' or str(stage_normalized).strip().upper() == 'NA'):
                            should_include = True
                        elif status_filter == 'contract' and '合同' in stage_normalized:
                            should_include = True
                        elif status_filter == 'invoice' and '开票' in stage_normalized:
                            should_include = True
                        elif status_filter == 'advance_invoice' and '提前开' in stage_normalized:
                            should_include = True
                        elif status_filter == 'paid' and ('回款' in stage_normalized or '已付' in stage_normalized):
                            should_include = True
                        elif status_filter == 'upsell' and '增购' in stage_normalized:
                            should_include = True
                        elif status_filter == 'invalid' and '无效' in stage_normalized:
                            should_include = True
                        elif status_filter == 'lost' and '失联' in stage_normalized:
                            should_include = True
                        
                        if should_include:
                            # 处理责任销售字段
                            sales_raw = row.get('续费责任销售', '')
                            if pd.isna(sales_raw) or sales_raw == '' or str(sales_raw).lower() == 'nan':
                                sales_person = str(row.get('责任销售中英文', ''))
                            else:
                                sales_person = str(sales_raw)
                            
                            # 计算距离到期的天数
                            days_until_expiry = (expiry_date - today).days
                            if days_until_expiry == 0:
                                date_label = "今天到期"
                            elif days_until_expiry == 1:
                                date_label = "明天到期"
                            else:
                                date_label = f"{days_until_expiry}天后到期"
                            
                            filtered_customers.append({
                                'expiry_date': f"{date_label} ({expiry_date.strftime('%Y年%m月%d日')})",
                                'jdy_account': str(row.get('用户ID', '')),
                                'company_name': str(row.get('账号-企业名称', '')),
                                'sales_person': sales_person,
                                'customer_stage': stage_normalized if stage_normalized else 'NA',
                                'days_until_expiry': days_until_expiry
                            })
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按到期日期排序（最近到期的在前）
        filtered_customers.sort(key=lambda x: x['days_until_expiry'])
        
        # 获取所有未来8-33天内的客户（不考虑状态筛选）用于计算各状态的数量
        all_customers_30days = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期']).date()
                    if eight_days_later <= expiry_date <= thirty_three_days_later:
                        customer_stage = row.get('客户阶段', '')
                        stage_normalized = ''
                        if pd.notna(customer_stage) and str(customer_stage).strip() != '' and str(customer_stage).lower() != 'nan':
                            stage_normalized = str(customer_stage).strip()
                        
                        all_customers_30days.append({
                            'customer_stage': stage_normalized if stage_normalized else 'NA'
                        })
                except Exception:
                    continue
        
        # 计算各状态计数（稳定返回所有已知状态，即使为0）
        count_all = len(all_customers_30days)
        count_na = len([c for c in all_customers_30days if str(c['customer_stage']).strip().upper() == 'NA'])
        count_contract = len([c for c in all_customers_30days if '合同' in c['customer_stage']])
        count_invoice = len([c for c in all_customers_30days if '开票' in c['customer_stage']])
        count_advance_invoice = len([c for c in all_customers_30days if '提前开' in c['customer_stage']])
        count_paid = len([c for c in all_customers_30days if ('回款' in c['customer_stage'] or '已付' in c['customer_stage'])])
        count_upsell = len([c for c in all_customers_30days if '增购' in c['customer_stage']])
        count_invalid = len([c for c in all_customers_30days if '无效' in c['customer_stage']])
        count_lost = len([c for c in all_customers_30days if '失联' in c['customer_stage']])

        # 固定顺序返回，避免前端芯片缺失
        unique_statuses = [
            {'value': 'all', 'label': '全部状态', 'count': count_all},
            {'value': 'na', 'label': 'NA状态', 'count': count_na},
            {'value': 'contract', 'label': '合同状态', 'count': count_contract},
            {'value': 'invoice', 'label': '开票状态', 'count': count_invoice},
            {'value': 'advance_invoice', 'label': '提前开状态', 'count': count_advance_invoice},
            {'value': 'paid', 'label': '回款状态', 'count': count_paid},
            {'value': 'upsell', 'label': '增购状态', 'count': count_upsell},
            {'value': 'invalid', 'label': '无效状态', 'count': count_invalid},
            {'value': 'lost', 'label': '失联状态', 'count': count_lost},
        ]
        
        logger.info(f"找到{len(filtered_customers)}个未来{min_days}-{max_days}天内的客户（筛选条件: {status_filter}）")
        return jsonify({
            'customers': filtered_customers,
            'total_count': len(filtered_customers),
            'query_date': today.strftime('%Y年%m月%d日'),
            'current_filter': status_filter,
            'available_statuses': unique_statuses
        })

    except Exception as e:
        logger.error(f"获取客户数据失败: {str(e)}")
        return jsonify({
            'customers': [], 
            'error': f'获取客户信息时出现问题',
            'query_date': datetime.now().strftime('%Y年%m月%d日')
        }), 500

@app.route('/export_unsigned_customers')
@login_required
def export_unsigned_customers():
    """导出所有客户数据，包含全部3606行"""
    try:
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        # 检查必要的列是否存在
        required_columns = ['用户ID', '账号-企业名称', '到期日期', '客户阶段']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Excel文件中缺少必要列: {missing_columns}")
            return jsonify({'error': f'数据格式错误：缺少必要列 {missing_columns}'}), 500
        
        # 获取当前日期
        now = datetime.now()
        today = now.date()
        
        # 创建导出的DataFrame，直接使用原始数据
        export_df = df.copy()
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        
        # 保存为Excel文件
        export_df.to_excel(temp_file.name, index=False)
        
        logger.info(f"导出了{len(export_df)}个客户数据到临时文件")
        
        # 返回文件下载
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=f"六大战区全部客户_{today.strftime('%Y%m%d')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"导出客户数据失败: {str(e)}")
        return jsonify({'error': f'导出客户数据时出现问题: {str(e)}'}), 500
    finally:
        # 确保临时文件被清理
        try:
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
        except Exception as e:
            logger.error(f"清理临时文件时发生错误: {str(e)}")

@app.route('/get_expiring_customers')
@login_required
def get_expiring_customers():
    try:
        # 获取筛选参数
        sales_filter = request.args.get('sales_filter', 'all')
        test_mode = request.args.get('test_mode', 'false').lower() == 'true'
        # 战区筛选参数（支持CSV和重复参数两种形式）
        raw_zones = request.args.getlist('zones')
        zones_list = []
        for val in raw_zones:
            if not val:
                continue
            if ',' in val:
                for z in val.split(','):
                    z_clean = z.strip()
                    if z_clean:
                        zones_list.append(z_clean)
            else:
                v = val.strip()
                if v:
                    zones_list.append(v)
        # 去重并保留顺序
        zones_list = list(dict.fromkeys(zones_list))
        logger.info(f"=== API调用开始 ===")
        logger.info(f"请求参数 - sales_filter: {sales_filter}, test_mode: {test_mode}, zones: {zones_list}")
        logger.info(f"原始参数 - sales_filter: {request.args.get('sales_filter')}, test_mode: {request.args.get('test_mode')}, zones(raw): {raw_zones}")
        logger.info(f"获取到期客户，销售筛选: {sales_filter}, 战区筛选: {zones_list}, 测试模式: {test_mode}")
        
        # 获取当前日期
        now = datetime.now()
        today = now.date()
        
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'expiring_customers': [], 'error': '数据文件不存在', 'today_date': today.strftime('%Y年%m月%d日')})

        try:
            ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
            # 列别名兼容：到期时间 -> 到期日期
            if '到期日期' not in df.columns and '到期时间' in df.columns:
                try:
                    df.rename(columns={'到期时间': '到期日期'}, inplace=True)
                    logger.info("兼容列名：将'到期时间'重命名为'到期日期'")
                except Exception as alias_err:
                    logger.warning(f"列名兼容失败: {str(alias_err)}")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'expiring_customers': [], 'error': '数据文件读取失败', 'today_date': today.strftime('%Y年%m月%d日')})

        # 检查必要的列并返回具体缺失项
        required_columns = ['到期日期', '用户ID', '账号-企业名称']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Excel文件中缺少必要列: {missing_columns}")
            return jsonify({
                'expiring_customers': [],
                'error': f'数据格式错误：缺少必要列 {missing_columns}',
                'today_date': today.strftime('%Y年%m月%d日')
            })
        
        # 战区列识别
        zone_col = None
        for candidate in ['战区', '所属战区', '归属战区']:
            if candidate in df.columns:
                zone_col = candidate
                break
        apply_zone_filter = len(zones_list) > 0 and zone_col is not None
        if len(zones_list) > 0 and zone_col is None:
            logger.warning("Excel中未找到战区相关列，忽略战区筛选")
        
        # 按需求：显示从今天开始，向后推延7天内到期
        start_date = today
        end_date = today + pd.Timedelta(days=7)
        reminder_type = "未来7天到期提醒"
        logger.info(f"到期提醒窗口：{start_date} 至 {end_date}，战区列: {zone_col}")
        
        # 筛选出目标日期到期的客户
        expiring_customers = []
        total_expiring = 0
        filtered_out = 0
        
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期']).date()
                    if start_date <= expiry_date <= end_date:
                        total_expiring += 1
                        # 使用标准化函数获取销售代表姓名
                        sales_person = get_normalized_sales_person(row)
                        
                        # 应用销售代表筛选
                        if sales_filter != 'all' and sales_filter != sales_person:
                            filtered_out += 1
                            continue
                        
                        # 读取战区用于展示/筛选
                        zone_val = ''
                        if zone_col is not None:
                            raw_zone_val = row.get(zone_col, None)
                            try:
                                is_nan_zone = pd.isna(raw_zone_val)
                            except Exception:
                                is_nan_zone = False
                            zone_val = '' if (raw_zone_val is None or is_nan_zone) else str(raw_zone_val).strip()
                        
                        # 应用战区筛选（如有）
                        if apply_zone_filter:
                            if zone_val == '' or zone_val not in zones_list:
                                filtered_out += 1
                                continue
                        
                        # 计算距离到期的天数
                        days_until_expiry = (expiry_date - today).days
                        if days_until_expiry == 0:
                            date_label = "今天到期"
                        elif days_until_expiry == 1:
                            date_label = "明天到期"
                        else:
                            date_label = f"{days_until_expiry}天后到期"
                        # 追加客户阶段到日期标签（如有），格式示例：3天后到期-回款 (2025年10月31日)
                        stage_val = row.get('客户阶段', None)
                        try:
                            stage_is_nan = pd.isna(stage_val)
                        except Exception:
                            stage_is_nan = False
                        stage_label = '' if (stage_val is None or stage_is_nan) else str(stage_val).strip()
                        if stage_label:
                            expiry_text = f"{date_label}-{stage_label} ({expiry_date.strftime('%Y年%m月%d日')})"
                        else:
                            expiry_text = f"{date_label} ({expiry_date.strftime('%Y年%m月%d日')})"

                        expiring_customers.append({
                            'expiry_date': expiry_text,
                            'jdy_account': str(row.get('用户ID', '')),
                            'company_name': str(row.get('账号-企业名称', '')),
                            'sales_person': sales_person,
                            'customer_classification': str(row.get('客户分类', '')),
                            'days_until_expiry': days_until_expiry,
                            'zone': zone_val,
                            'customer_stage': stage_label if stage_label else 'NA'
                        })
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按到期日期排序
        expiring_customers.sort(key=lambda x: x['days_until_expiry'])
        
        # 记录筛选统计信息
        logger.info(f"筛选统计 - 总到期客户: {total_expiring}, 筛选掉: {filtered_out}, 最终结果: {len(expiring_customers)}, 筛选条件: {sales_filter}")
        
        if len(expiring_customers) == 0:
            # 未来7天窗口的提示信息（根据是否有战区筛选）
            if apply_zone_filter and len(zones_list) > 0:
                zones_str = '，'.join(zones_list)
                message = f"😊 {zones_str}在未来7天内没有客户到期"
            else:
                message = "😊 未来7天内没有客户到期"
            logger.info(message)
            return jsonify({
                'expiring_customers': [], 
                'message': message,
                'today_date': today.strftime('%Y年%m月%d日'),
                'reminder_type': reminder_type,
                'selected_zones': zones_list
            })
        else:
            logger.info(f"找到{len(expiring_customers)}个即将过期的客户")
            return jsonify({
                'expiring_customers': expiring_customers,
                'today_date': today.strftime('%Y年%m月%d日'),
                'reminder_type': reminder_type,
                'selected_zones': zones_list
            })

    except Exception as e:
        logger.error(f"获取即将过期客户失败: {str(e)}")
        return jsonify({
            'expiring_customers': [], 
            'error': f'获取客户信息时出现问题',
            'today_date': datetime.now().strftime('%Y年%m月%d日'),
            'reminder_type': '系统错误'
        })

@app.route('/query_customer', methods=['POST'])
@login_required
def query_customer():
    try:
        if not request.json or ('jdy_id' not in request.json and 'company_name' not in request.json):
            logger.warning("请求中缺少查询参数")
            return jsonify({'error': '请提供简道云账号或公司名称'}), 400
            
        # 获取查询参数
        jdy_id = request.json.get('jdy_id', '')
        company_name = request.json.get('company_name', '')
        
        # 记录查询参数
        if jdy_id:
            logger.info(f"开始通过简道云账号查询: {jdy_id}")
        if company_name:
            logger.info(f"开始通过公司名称查询: {company_name}")
        
        # 检查文件是否存在
        excel_path = get_user_excel_path()
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            # 确保pandas已延迟导入
            pd = ensure_pandas_imported()
            df = pd.read_excel(excel_path)
            # 列名归一化：兼容“简道云ID”、“账号-企业名称”
            try:
                if '用户ID' not in df.columns and '简道云ID' in df.columns:
                    df.rename(columns={'简道云ID': '用户ID'}, inplace=True)
                if '公司名称' not in df.columns and '账号-企业名称' in df.columns:
                    df.rename(columns={'账号-企业名称': '公司名称'}, inplace=True)
            except Exception:
                pass
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        # 检查必要的列是否存在（公司列允许两种：公司名称 或 账号-企业名称）
        if '用户ID' not in df.columns:
            logger.error("Excel文件中缺少'用户ID'列")
            return jsonify({'error': '数据格式错误：缺少用户ID列'}), 500
        has_company = ('公司名称' in df.columns) or ('账号-企业名称' in df.columns)
        if not has_company:
            logger.error("Excel文件中缺少公司名称相关列：公司名称/账号-企业名称")
            return jsonify({'error': '数据格式错误：缺少公司名称或账号-企业名称列'}), 500
        
        # 根据查询条件进行模糊匹配
        if jdy_id:
            matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        else:
            # 优化：同时在"公司名称"和"账号-企业名称"列中进行搜索
            company_name_lower = str(company_name).lower()
            # 使用OR条件进行多列搜索
            matching_rows = df[
                (df['公司名称'].astype(str).str.lower().str.contains(company_name_lower, na=False)) |
                (df['账号-企业名称'].astype(str).str.lower().str.contains(company_name_lower, na=False))
            ]
            
        if matching_rows.empty:
            query_type = "简道云账号" if jdy_id else "公司名称"
            query_value = jdy_id if jdy_id else company_name
            logger.info(f"未找到匹配的客户信息，查询{query_type}: {query_value}")
            return jsonify({'error': '未找到客户信息'}), 404

        # 处理多条匹配记录
        results = []
        for _, customer_data in matching_rows.iterrows():
            # 处理新字段映射
            account_enterprise_name = str(customer_data.get('账号-企业名称', ''))
            integration_mode = str(customer_data.get('集成模式', ''))
            customer_classification = str(customer_data.get('客户分类', ''))
            
            # 处理责任销售字段 - 优先使用续费责任销售，如果为空则使用责任销售中英文
            sales_raw = customer_data.get('续费责任销售', '')
            if pd.isna(sales_raw) or sales_raw == '' or str(sales_raw).lower() == 'nan':
                sales = str(customer_data.get('责任销售中英文', ''))
            else:
                sales = str(sales_raw)
            
            sales_cn_en = str(customer_data.get('责任销售中英文', ''))
            jdy_sales = str(customer_data.get('简道云销售', ''))
            
            logger.info(f"处理客户数据: {customer_data['用户ID']}, 账号-企业名称: {account_enterprise_name}, "
                      f"集成模式: {integration_mode}, 客户分类: {customer_classification}, "
                      f"续费责任销售: {sales}, 责任销售中英文: {sales_cn_en}, 简道云销售: {jdy_sales}")
            
            # 处理到期日期
            expiry_date = ''
            if '到期日期' in customer_data and pd.notna(customer_data['到期日期']):
                try:
                    expiry_date = pd.to_datetime(customer_data['到期日期']).strftime('%Y年%m月%d日')
                    logger.info(f"到期日期: {expiry_date}")
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    expiry_date = ''
            
            # 处理ARR
            try:
                arr_value = customer_data.get('应续ARR', 0)
                if pd.isna(arr_value) or arr_value == '' or float(str(arr_value).replace(',', '')) == 0:
                    arr_display = '0元'
                else:
                    arr_display = f"{float(str(arr_value).replace(',', ''))}元"
                logger.info(f"应续ARR: {arr_display}")
            except Exception as e:
                logger.warning(f"ARR处理错误: {str(e)}")
                arr_display = '0元'
            
            results.append({
                'account_enterprise_name': account_enterprise_name,  # 账号-企业名称
                'company_name': str(customer_data.get('公司名称', '')),  # 公司名称
                'tax_number': str(customer_data.get('税号', '')),  # 税号
                'integration_mode': integration_mode,  # 集成模式
                'expiry_date': expiry_date,  # 到期日期
                'uid_arr': arr_display,  # 应续ARR
                'customer_classification': customer_classification,  # 客户分类
                'sales': sales,  # 续费责任销售
                'sales_cn_en': sales_cn_en,  # 责任销售中英文
                'jdy_sales': jdy_sales,  # 简道云销售
                'user_id': str(customer_data.get('用户ID', ''))  # 保留用户ID用于兼容
            })

        logger.info(f"查询成功，找到{len(results)}条匹配记录")
        return jsonify({'results': results})

    except Exception as e:
        logger.error(f"查询出错: {str(e)}")
        return jsonify({'error': f'查询出错: {str(e)}'}), 500

@app.route('/update_stage', methods=['POST'])
@login_required
def update_stage():
    """更新客户阶段状态（使用优化的状态管理器）"""
    try:
        data = request.get_json()
        if not data or 'jdy_id' not in data or 'stage' not in data:
            return jsonify({'success': False, 'error': '缺少必要参数', 'error_type': 'validation'}), 400
        
        jdy_id = data['jdy_id']
        stage = data['stage']
        force = data.get('force', False)  # 是否强制更新
        
        logger.info(f"更新客户阶段: {jdy_id} -> {stage} (force={force})")
        
        # 使用新的状态管理器（按用户数据源实例化）
        mgr = None
        if STAGE_MANAGER_AVAILABLE:
            try:
                mgr = StageManager(get_user_excel_path())
            except Exception as e:
                logger.warning(f"状态管理器实例化失败: {str(e)}")
                mgr = None

        if mgr:
            result = mgr.update_stage(
                jdy_id=jdy_id,
                target_stage=stage,
                force=force,
                metadata={
                    'source': 'web_interface',
                    'user_agent': request.headers.get('User-Agent', ''),
                    'ip': request.remote_addr,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # 根据结果返回适当的HTTP状态码
            if result['success']:
                return jsonify(result), 200
            else:
                error_type = result.get('error_type', 'unknown')
                if error_type == 'validation':
                    return jsonify(result), 400
                elif error_type == 'customer_not_found':
                    return jsonify(result), 404
                elif error_type == 'conflict':
                    return jsonify(result), 409
                else:
                    return jsonify(result), 500
        else:
            # 降级到原有逻辑
            logger.warning("状态管理器不可用或初始化失败，使用原有逻辑")
            return _legacy_update_stage(jdy_id, stage)
        
    except Exception as e:
        logger.error(f"更新阶段失败: {str(e)}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'error_type': 'system_error'
        }), 500

def _legacy_update_stage(jdy_id, stage):
    """原有的状态更新逻辑（降级方案）"""
    try:
        # 读取Excel文件
        excel_path = get_user_excel_path()
        if not os.path.exists(excel_path):
            logger.error(f"Excel文件不存在: {excel_path}")
            return jsonify({'success': False, 'error': 'Excel文件不存在', 'error_type': 'file_not_found'}), 500
        
        # 读取Excel文件
        ensure_pandas_imported()
        df = pd.read_excel(excel_path)
        logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        
        # 检查必要的列是否存在
        if '用户ID' not in df.columns:
            logger.error("Excel文件中缺少'用户ID'列")
            return jsonify({'success': False, 'error': 'Excel文件格式错误：缺少用户ID列', 'error_type': 'column_missing'}), 500
        
        # 查找匹配的客户记录
        matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        
        if matching_rows.empty:
            logger.warning(f"未找到匹配的客户记录: {jdy_id}")
            return jsonify({'success': False, 'error': f'未找到客户记录: {jdy_id}', 'error_type': 'customer_not_found'}), 404
        
        # 检查是否有阶段列，如果没有则创建
        stage_column = '客户阶段'
        if stage_column not in df.columns:
            df[stage_column] = ''
            logger.info(f"创建新列: {stage_column}")
        
        # 更新匹配记录的阶段
        updated_count = 0
        for index in matching_rows.index:
            old_stage = df.loc[index, stage_column] if pd.notna(df.loc[index, stage_column]) else '未设置'
            df.loc[index, stage_column] = stage
            updated_count += 1
            logger.info(f"更新记录 {index}: {old_stage} -> {stage}")
        
        # 保存更新后的Excel文件
        df.to_excel(excel_path, index=False)
        logger.info(f"Excel文件已更新，共更新 {updated_count} 条记录")
        
        return jsonify({
            'success': True,
            'message': f'客户 {jdy_id} 已成功推进到 {stage} 阶段（更新了 {updated_count} 条记录）',
            'updated_count': updated_count
        })
        
    except Exception as e:
         logger.error(f"Excel文件操作失败: {str(e)}")
         return jsonify({'success': False, 'error': f'Excel文件操作失败: {str(e)}', 'error_type': 'file_operation_error'}), 500

@app.route('/stage_history', methods=['GET'])
@login_required
def get_stage_history():
    """获取状态变更历史"""
    try:
        jdy_id = request.args.get('jdy_id')
        limit = int(request.args.get('limit', 100))
        
        mgr = None
        if STAGE_MANAGER_AVAILABLE:
            try:
                mgr = StageManager(get_user_excel_path())
            except Exception as e:
                logger.warning(f"状态管理器实例化失败: {str(e)}")
                mgr = None

        if mgr:
            history = mgr.get_stage_history(jdy_id, limit)
            return jsonify({
                'success': True,
                'history': history,
                'count': len(history)
            })
        else:
            return jsonify({
                'success': False,
                'error': '状态管理器不可用',
                'error_type': 'service_unavailable'
            }), 503
            
    except Exception as e:
        logger.error(f"获取状态历史失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/validate_stage_batch', methods=['POST'])
@login_required
def validate_stage_batch():
    """批量状态校验"""
    try:
        data = request.get_json()
        if not data or 'updates' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数：updates',
                'error_type': 'validation'
            }), 400
        
        updates = data['updates']
        if not isinstance(updates, list):
            return jsonify({
                'success': False,
                'error': 'updates必须是数组',
                'error_type': 'validation'
            }), 400
        
        mgr = None
        if STAGE_MANAGER_AVAILABLE:
            try:
                mgr = StageManager(get_user_excel_path())
            except Exception as e:
                logger.warning(f"状态管理器实例化失败: {str(e)}")
                mgr = None

        if mgr:
            results = mgr.validate_stage_batch(updates)
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            return jsonify({
                'success': False,
                'error': '状态管理器不可用',
                'error_type': 'service_unavailable'
            }), 503
            
    except Exception as e:
        logger.error(f"批量状态校验失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/stage_rules', methods=['GET'])
@login_required
def get_stage_rules():
    """获取状态转换规则"""
    try:
        mgr = None
        if STAGE_MANAGER_AVAILABLE:
            try:
                mgr = StageManager(get_user_excel_path())
            except Exception as e:
                logger.warning(f"状态管理器实例化失败: {str(e)}")
                mgr = None

        if mgr:
            return jsonify({
                'success': True,
                'stage_rules': mgr.stage_rules,
                'stage_priority': mgr.stage_priority
            })
        else:
            return jsonify({
                'success': False,
                'error': '状态管理器不可用',
                'error_type': 'service_unavailable'
            }), 503
            
    except Exception as e:
        logger.error(f"获取状态规则失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': 'system_error'
        }), 500

@app.route('/docx_templates/<template_name>')
def get_template(template_name):
    if not template_name.endswith('.docx'):
        return '不支持的文件类型', 400

    try:
        # 使用应用根路径定位模板目录，避免工作目录差异
        template_dir = os.path.join(app.root_path, 'templates', 'docx_templates')
        # 防止路径穿越攻击：规范化并检查前缀
        candidate = os.path.normpath(os.path.join(template_dir, template_name))
        template_dir_abs = os.path.abspath(template_dir)
        if not candidate.startswith(template_dir_abs + os.sep):
            logger.error(f"非法模板路径: {candidate}")
            return '非法模板路径', 400

        template_path = candidate

        if not os.path.exists(template_path):
            logger.error(f"模板文件不存在: {template_path}")
            return '模板文件不存在', 404

        logger.info(f"正在加载模板文件: {template_path}")
        return send_file(
            template_path,
            as_attachment=False,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        logger.error(f"模板文件访问错误: {str(e)}")
        return '模板文件访问错误', 500

@app.route('/generate', methods=['POST'])
@login_required
def generate():
    temp_template = None
    temp_output = None
    
    try:
        logger.info("开始处理文件上传请求")
        
        # 检查是否有文件上传
        if 'template' not in request.files:
            logger.error("请求中没有找到文件")
            return '请选择合同模板文件', 400
            
        template_file = request.files['template']
        if not template_file or not template_file.filename:
            logger.error("没有选择文件")
            return '请选择合同模板文件', 400
            
        if not template_file.filename.endswith('.docx'):
            logger.error("文件格式不正确")
            return '请选择.docx格式的文件', 400

        logger.info(f"接收到文件: {template_file.filename}")

        # 创建临时文件保存上传的模板
        temp_template = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        template_file.save(temp_template.name)
        logger.info(f"模板文件已保存到临时文件: {temp_template.name}")
        
        # 获取表单数据
        form_data = request.form.to_dict()
        
        # 处理多选值
        contract_types = request.form.getlist('contract_type')
        if contract_types:
            form_data['contract_types'] = ', '.join(contract_types)
        
        logger.info(f"接收到的表单数据: {form_data}")
        
        # 创建临时文件用于保存生成的合同
        temp_output = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        logger.info(f"创建输出临时文件: {temp_output.name}")

        # 检查模板处理器是否可用
        if not TEMPLATE_HANDLER_AVAILABLE:
            logger.error("模板处理器不可用")
            return '模板处理器不可用，请检查依赖包是否正确安装', 500
            
        # 处理模板（扩大异常捕获范围，覆盖初始化与渲染阶段）
        try:
            handler = TemplateHandler(temp_template.name)
            output_path = handler.process_template(form_data, temp_output.name)
        except TemplateSyntaxError as e:
            # 针对Jinja模板语法错误进行更友好的提示
            logger.error(f"模板语法错误: {str(e)}")
            hint = (
                "模板语法错误（可能存在多余或不匹配的花括号）。请检查模板中的 Jinja 变量/块是否成对："
                "'{{ ... }}'、'{% ... %}'、'{# ... #}'；避免出现额外的 '}'。如需在正文中使用花括号，"
                "请改用全角 '｛｝' 或使用原始块 '{% raw %}...{% endraw %}'."
            )
            # 返回结构化错误，前端会优先解析JSON错误
            return jsonify({
                'error': f"生成合同时发生错误: {getattr(e, 'message', str(e))}",
                'hint': hint,
                'lineno': getattr(e, 'lineno', None)
            }), 400
        except Exception as e:
            # docxtpl 可能包装 Jinja 异常或仅返回错误信息
            msg = str(e)
            if (
                "unexpected '}'" in msg
                or 'jinja2' in msg.lower()
                or (DocxTplTemplateError and isinstance(e, DocxTplTemplateError))
            ):
                logger.error(f"模板语法错误(兼容抓取): {msg}")
                hint = (
                    "模板语法错误（可能存在多余或不匹配的花括号）。请检查模板中的 Jinja 变量/块是否成对："
                    "'{{ ... }}'、'{% ... %}'、'{# ... #}'；避免出现额外的 '}'。如需在正文中使用花括号，"
                    "请改用全角 '｛｝' 或使用原始块 '{% raw %}...{% endraw %}'."
                )
                return jsonify({
                    'error': f"生成合同时发生错误: {msg}",
                    'hint': hint,
                    'lineno': getattr(e, 'lineno', None)
                }), 400
            # 其他错误按服务器错误处理
            logger.error(f"模板处理失败: {msg}")
            return jsonify({'error': f'生成合同时发生错误: {msg}'}), 500

        logger.info(f"合同生成完成，输出文件: {output_path}")

        # 返回生成的文件
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{form_data['start_year']}-{form_data['end_year']}+{form_data['company_name']}+帆软简道云续费合同+{datetime.now().strftime('%Y%m%d')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
        return jsonify({'error': f'生成合同时发生错误: {str(e)}'}), 500

    finally:
        # 清理临时文件
        try:
            if temp_template:
                os.unlink(temp_template.name)
                logger.info(f"清理临时模板文件: {temp_template.name}")
            if temp_output:
                os.unlink(temp_output.name)
                logger.info(f"清理临时输出文件: {temp_output.name}")
        except Exception as e:
            logger.error(f"清理临时文件时发生错误: {str(e)}")

@app.route('/generate_quote', methods=['POST'])
@login_required
def generate_quote():
    """生成报价单功能 - 直接使用固定模板"""
    temp_output = None
    
    try:
        logger.info("开始处理报价单生成请求")
        
        # 获取表单数据
        form_data = request.form.to_dict()
        logger.info(f"接收到的表单数据: {form_data}")
        
        # 验证必填字段（结构化错误返回）
        required_map = {
            'company_name': '公司名称',
            'tax_number': '税号',
            'jdy_account': '简道云账号',
            'total_amount': '服务费用金额',
            'user_count': '使用人数'
        }
        errors = {}
        for field, label in required_map.items():
            value = (form_data.get(field) or '').strip()
            if not value:
                logger.error(f"缺少必填字段: {field}")
                errors[field] = f"{label}为必填项"
        if errors:
            return jsonify({'success': False, 'error': '必填字段缺失', 'errors': errors}), 400
        
        # 检查模板处理器是否可用
        if not TEMPLATE_HANDLER_AVAILABLE:
            logger.error("模板处理器不可用")
            return jsonify({'success': False, 'error': '模板处理器不可用，请检查依赖包是否正确安装'}), 500
        
        # 使用固定的报价单模板
        quote_template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'docx_templates', '【2025年续费】 报价单-带变量.docx')
        if not os.path.exists(quote_template_path):
            logger.error(f"报价单模板文件不存在: {quote_template_path}")
            return jsonify({'success': False, 'error': '报价单模板文件不存在'}), 500
        
        logger.info(f"使用报价单模板: {quote_template_path}")
        
        # 创建临时文件用于保存生成的报价单
        temp_output = tempfile.NamedTemporaryFile(suffix='.docx', delete=False)
        logger.info(f"创建输出临时文件: {temp_output.name}")
        
        # 处理模板
        handler = TemplateHandler(quote_template_path)
        output_path = handler.process_template(form_data, temp_output.name)
        logger.info(f"报价单生成完成，输出文件: {output_path}")

        # 返回生成的文件
        return send_file(
            output_path,
            as_attachment=True,
            download_name=f"{form_data['company_name']}_报价单_{datetime.now().strftime('%Y%m%d')}.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    except Exception as e:
        logger.error(f"生成报价单时发生错误: {str(e)}")
        return jsonify({'success': False, 'error': f'生成报价单时发生错误: {str(e)}'}), 500
    finally:
        # 清理临时文件
        try:
            if temp_output:
                os.unlink(temp_output.name)
                logger.info(f"清理临时输出文件: {temp_output.name}")
        except Exception as e:
            logger.error(f"清理临时文件时发生错误: {str(e)}")

@app.route('/parse_text', methods=['POST'])
@login_required
def parse_text():
    """解析粘贴板文本内容"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': '没有提供文本内容'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'success': False, 'error': '文本内容为空'}), 400
        
        logger.info(f"开始解析文本，长度: {len(text)} 字符")
        logger.info(f"实际文本内容: {repr(text)}")  # 添加详细日志
        
        # 使用OCR服务的文本解析功能
        if ocr_service:
            parsed_fields = ocr_service.parse_text_to_fields(text)
            
            # 检测O/0混淆警告
            warnings = []
            if 'tax_number' in parsed_fields:
                tax_number = parsed_fields['tax_number']
                # 检测税号中是否包含字母O或数字0（任意一个都提醒）
                if 'O' in tax_number or '0' in tax_number:
                    warnings.append({
                        'type': 'ocr_confusion',
                        'field': 'tax_number',
                        'message': '税号包含0/O,请注意检查🧐',
                        'suggestion': ''
                    })
            
            logger.info(f"文本解析成功，识别到 {len(parsed_fields)} 个字段，{len(warnings)} 个警告")
            return jsonify({
                'success': True,
                'fields': parsed_fields,
                'field_count': len(parsed_fields),
                'warnings': warnings
            })
        else:
            # 如果OCR服务不可用，使用简单的文本解析
            parsed_fields = simple_text_parse(text)
            logger.info(f"简单文本解析完成，识别到 {len(parsed_fields)} 个字段")
            return jsonify({
                'success': True,
                'fields': parsed_fields,
                'field_count': len(parsed_fields)
            })
    
    except Exception as e:
        logger.error(f"文本解析异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'文本解析失败: {str(e)}',
            'fields': {},
            'field_count': 0
        }), 500

@app.route('/ocr_image', methods=['POST'])
@login_required
def ocr_image():
    """处理OCR图片识别请求（base64格式）"""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': '没有提供图片数据'}), 400
        
        image_data = data['image']
        if not image_data:
            return jsonify({'success': False, 'error': '图片数据为空'}), 400
        
        # 处理base64图片数据
        if image_data.startswith('data:image'):
            # 移除data:image/xxx;base64,前缀
            image_data = image_data.split(',')[1]
        
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({'success': False, 'error': '图片数据格式错误'}), 400
        
        # 检查文件大小（限制为10MB）
        if len(image_bytes) > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': '图片大小超过限制（10MB）'}), 400
        
        logger.info(f"开始处理OCR请求，图片大小: {len(image_bytes)} bytes")
        
        # 使用OCR服务处理图片
        if ocr_service:
            # 使用process_image方法而不是extract_text_from_image
            result = ocr_service.process_image(image_bytes)
            if result['success']:
                # 检测O/0混淆警告
                warnings = []
                parsed_fields = result.get('parsed_fields', {})
                if 'tax_number' in parsed_fields:
                    tax_number = parsed_fields['tax_number']
                    # 检测税号中是否包含字母O或数字0（任意一个都提醒）
                    if 'O' in tax_number or '0' in tax_number:
                        warnings.append({
                            'type': 'ocr_confusion',
                            'field': 'tax_number',
                            'message': '税号包含0/O,请注意检查🧐',
                            'suggestion': ''
                        })
                
                logger.info(f"OCR处理成功，提取文本长度: {len(result.get('extracted_text', ''))}")
                return jsonify({
                    'success': True,
                    'text': result.get('extracted_text', ''),
                    'confidence': 0.8,  # 默认置信度
                    'fields': result.get('parsed_fields', {}),
                    'field_count': result.get('field_count', 0),
                    'warnings': warnings
                })
            else:
                logger.error(f"OCR处理失败: {result.get('error', '未知错误')}")
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'OCR识别失败'),
                    'text': ''
                })
        else:
            return jsonify({
                'success': False,
                'error': 'OCR服务暂时不可用，请使用粘贴板功能',
                'text': ''
            })
    
    except Exception as e:
        logger.error(f"OCR图片处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'图片处理失败: {str(e)}',
            'text': ''
        }), 500

def simple_text_parse(text):
    """简单的文本解析功能，当OCR服务不可用时使用"""
    import re
    
    fields = {}
    
    # 定义字段匹配规则
    patterns = {
        'company_name': [
            r'公司名称[：:]\s*(.+?)(?:\n|$)',
            r'企业名称[：:]\s*(.+?)(?:\n|$)',
            r'名\s*称[：:]\s*(.+?)(?:\n|$)',
            r'单位名称[：:]\s*(.+?)(?:\n|$)'
        ],
        'tax_number': [
            r'税号[：:]\s*([A-Z0-9]{15,20})(?:\n|$)',
            r'纳税人识别号[：:]\s*([A-Z0-9]{15,20})(?:\n|$)',
            r'统一社会信用代码[：:]\s*([A-Z0-9]{15,20})(?:\n|$)'
        ],
        'reg_address': [
            r'注册地址[：:]\s*(.+?)(?:\n|$)',
            r'地\s*址[：:]\s*(.+?)(?:\n|$)',
            r'注册地[：:]\s*(.+?)(?:\n|$)'
        ],
        'reg_phone': [
            r'注册电话[：:]\s*([0-9\-\s]+)(?:\n|$)',
            r'电\s*话[：:]\s*([0-9\-\s]+)(?:\n|$)',
            r'联系电话[：:]\s*([0-9\-\s]+)(?:\n|$)'
        ],
        'bank_name': [
            r'开户行[：:]\s*(.+?)(?:\n|$)',
            r'开户银行[：:]\s*(.+?)(?:\n|$)',
            r'银行名称[：:]\s*(.+?)(?:\n|$)'
        ],
        'bank_account': [
            r'账号[：:]\s*([0-9\s]+)(?:\n|$)',
            r'银行账号[：:]\s*([0-9\s]+)(?:\n|$)',
            r'账户[：:]\s*([0-9\s]+)(?:\n|$)'
        ],
        'contact_name': [
            r'联系人[：:]\s*(.+?)(?:\n|$)',
            r'负责人[：:]\s*(.+?)(?:\n|$)',
            r'经办人[：:]\s*(.+?)(?:\n|$)'
        ],
        'contact_phone': [
            r'联系人电话[：:]\s*([0-9\-\s]+)(?:\n|$)',
            r'手机[：:]\s*([0-9\-\s]+)(?:\n|$)',
            r'移动电话[：:]\s*([0-9\-\s]+)(?:\n|$)'
        ],
        'mail_address': [
            r'邮寄地址[：:]\s*(.+?)(?:\n|$)',
            r'通讯地址[：:]\s*(.+?)(?:\n|$)',
            r'收件地址[：:]\s*(.+?)(?:\n|$)'
        ]
    }
    
    # 对每个字段进行匹配
    for field_name, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if value and len(value) > 0:
                    fields[field_name] = value
                    break
    
    return fields

@app.route('/ocr_process', methods=['POST'])
def ocr_process():
    """处理OCR图片识别请求"""
    try:
        # 检查OCR服务是否可用
        if ocr_service is None:
            return jsonify({
                'success': False,
                'error': 'OCR服务暂时不可用，请稍后再试'
            }), 503

        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': '没有上传图片文件'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': '没有选择文件'}), 400

        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400

        # 读取图片数据
        image_data = file.read()

        # 检查文件大小（限制为10MB）
        if len(image_data) > 10 * 1024 * 1024:
            return jsonify({'success': False, 'error': '文件大小超过限制（10MB）'}), 400

        logger.info(f"开始处理OCR请求，文件大小: {len(image_data)} bytes")

        # 使用OCR服务处理图片
        result = ocr_service.process_image(image_data)

        if result['success']:
            logger.info(f"OCR处理成功，识别到 {result['field_count']} 个字段")
            return jsonify(result)
        else:
            logger.error(f"OCR处理失败: {result.get('error', '未知错误')}")
            # 对于OCR不可用的情况，返回200状态码但success=False
            # 这样前端可以正确处理错误信息
            return jsonify(result), 200

    except Exception as e:
        logger.error(f"OCR处理异常: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'服务器处理错误: {str(e)}',
            'extracted_text': '',
            'parsed_fields': {},
            'field_count': 0
        }), 500

@app.route('/monitor_downloads', methods=['POST'])
@login_required
def monitor_downloads():
    """监控下载文件夹中的合同文件并自动更新客户状态"""
    try:
        import os
        from pathlib import Path
        import time
        import re
        
        # 获取用户的下载文件夹路径
        downloads_path = str(Path.home() / "Downloads")
        
        # 检查下载文件夹是否存在
        if not os.path.exists(downloads_path):
            return jsonify({
                'success': False, 
                'error': '无法访问下载文件夹',
                'path': downloads_path
            }), 400
        
        # 获取最近30分钟内的合同文件
        current_time = time.time()
        recent_contracts = []
        
        try:
            for file_path in Path(downloads_path).glob("*.docx"):
                # 检查文件修改时间（最近30分钟内）
                file_mtime = file_path.stat().st_mtime
                if current_time - file_mtime <= 1800:  # 30分钟 = 1800秒
                    # 检查文件名是否包含合同相关关键词
                    filename = file_path.name
                    if any(keyword in filename for keyword in ['合同', '续费', '帆软', '简道云']):
                        # 尝试从文件名中提取简道云账号
                        jdy_account = extract_jdy_account_from_filename(filename)
                        recent_contracts.append({
                            'filename': filename,
                            'path': str(file_path),
                            'mtime': file_mtime,
                            'jdy_account': jdy_account
                        })
        except Exception as e:
            logger.error(f"扫描下载文件夹失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'扫描文件夹失败: {str(e)}'
            }), 500
        
        # 自动推进找到简道云账号的合同到"合同"阶段
        updated_contracts = []
        for contract in recent_contracts:
            if contract['jdy_account']:
                try:
                    # 调用更新阶段的逻辑
                    result = update_customer_stage(contract['jdy_account'], '合同')
                    if result['success']:
                        updated_contracts.append({
                            'filename': contract['filename'],
                            'jdy_account': contract['jdy_account'],
                            'status': 'updated'
                        })
                        # 记录已处理的文件
                        processed_files[contract['path']] = current_time
                        logger.info(f"自动推进合同成功: {contract['jdy_account']} -> 合同阶段")
                    else:
                        updated_contracts.append({
                            'filename': contract['filename'],
                            'jdy_account': contract['jdy_account'],
                            'status': 'failed',
                            'error': result.get('error', '未知错误')
                        })
                        # 即使失败也记录，避免重复尝试
                        processed_files[contract['path']] = current_time
                except Exception as e:
                    logger.error(f"自动推进合同失败: {str(e)}")
                    updated_contracts.append({
                        'filename': contract['filename'],
                        'jdy_account': contract['jdy_account'],
                        'status': 'error',
                        'error': str(e)
                    })
                    # 即使出错也记录，避免重复尝试
                    processed_files[contract['path']] = current_time
            else:
                # 没有找到简道云账号的文件也记录，避免重复扫描
                processed_files[contract['path']] = current_time
        
        return jsonify({
            'success': True,
            'downloads_path': downloads_path,
            'recent_contracts': recent_contracts,
            'updated_contracts': updated_contracts,
            'total_found': len(recent_contracts),
            'total_updated': len([c for c in updated_contracts if c['status'] == 'updated'])
        })
        
    except Exception as e:
        logger.error(f"监控下载文件夹失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'监控功能异常: {str(e)}'
        }), 500

def extract_jdy_account_from_filename(filename):
    """从文件名中提取简道云账号"""
    import re
    
    # 尝试多种模式匹配简道云账号
    patterns = [
        r'([a-f0-9]{24,})',  # 24位以上的十六进制字符串
        r'([a-zA-Z0-9]{20,})',  # 20位以上的字母数字组合
        r'jdy[_-]?([a-zA-Z0-9]+)',  # jdy前缀
        r'账号[_-]?([a-zA-Z0-9]+)',  # 账号前缀
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            account = match.group(1)
            # 验证账号长度和格式
            if len(account) >= 15 and len(account) <= 50:
                return account
    
    return None

def update_customer_stage(jdy_id, stage):
    """更新客户阶段的内部函数"""
    try:
        # 读取Excel文件
        excel_path = get_user_excel_path()
        if not os.path.exists(excel_path):
            return {'success': False, 'error': 'Excel文件不存在'}
        
        ensure_pandas_imported()
        df = pd.read_excel(excel_path)
        
        # 检查必要的列是否存在
        if '用户ID' not in df.columns:
            return {'success': False, 'error': 'Excel文件格式错误：缺少用户ID列'}
        
        # 查找匹配的客户记录
        matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        
        if matching_rows.empty:
            return {'success': False, 'error': f'未找到客户记录: {jdy_id}'}
        
        # 检查是否有阶段列，如果没有则创建
        stage_column = '客户阶段'
        if stage_column not in df.columns:
            df[stage_column] = ''
        
        # 更新匹配记录的阶段
        updated_count = 0
        for index in matching_rows.index:
            df.loc[index, stage_column] = stage
            updated_count += 1
        
        # 保存更新后的Excel文件
        df.to_excel(excel_path, index=False)
        
        return {
            'success': True,
            'message': f'客户 {jdy_id} 已成功推进到 {stage} 阶段',
            'updated_count': updated_count
        }
        
    except Exception as e:
        return {'success': False, 'error': f'更新失败: {str(e)}'}

def background_monitor_worker():
    """后台监控工作线程"""
    global auto_monitor_enabled, monitor_results, last_monitor_check
    
    while auto_monitor_enabled:
        try:
            with monitor_lock:
                if not auto_monitor_enabled:
                    break
                    
                # 执行监控检查
                result = perform_monitor_check()
                if result:
                    monitor_results = result
                    last_monitor_check = datetime.now()
                    
                    # 如果发现新合同，记录日志
                    if result.get('total_found', 0) > 0:
                        logger.info(f"自动监控发现 {result['total_found']} 个合同文件，成功推进 {result.get('total_updated', 0)} 个")
                        
        except Exception as e:
            logger.error(f"后台监控异常: {str(e)}")
            
        # 等待30秒后继续下一次检查
        time.sleep(30)
    
    logger.info("后台监控线程已停止")

def perform_monitor_check():
    """执行监控检查的核心逻辑"""
    global processed_files
    try:
        # 获取用户的下载文件夹路径
        downloads_path = str(Path.home() / "Downloads")
        
        # 检查下载文件夹是否存在
        if not os.path.exists(downloads_path):
            return None
        
        # 获取最近30分钟内的合同文件
        current_time = time.time()
        recent_contracts = []
        
        # 清理超过24小时的已处理文件记录
        files_to_remove = []
        for file_path, process_time in processed_files.items():
            if current_time - process_time > 86400:  # 24小时 = 86400秒
                files_to_remove.append(file_path)
        for file_path in files_to_remove:
            del processed_files[file_path]
        
        for file_path in Path(downloads_path).glob("*.docx"):
            # 检查文件修改时间（最近30分钟内）
            file_mtime = file_path.stat().st_mtime
            if current_time - file_mtime <= 1800:  # 30分钟 = 1800秒
                # 检查文件名是否包含合同相关关键词
                filename = file_path.name
                if any(keyword in filename for keyword in ['合同', '续费', '帆软', '简道云']):
                    # 检查是否已经处理过这个文件
                    file_path_str = str(file_path)
                    if file_path_str in processed_files:
                        continue  # 跳过已处理的文件
                    
                    # 尝试从文件名中提取简道云账号
                    jdy_account = extract_jdy_account_from_filename(filename)
                    recent_contracts.append({
                        'filename': filename,
                        'path': file_path_str,
                        'mtime': file_mtime,
                        'jdy_account': jdy_account
                    })
        
        # 自动推进找到简道云账号的合同到"合同"阶段
        updated_contracts = []
        for contract in recent_contracts:
            # 处理完成后立即记录文件，避免重复处理
            processed_files[contract['path']] = current_time
            
            if contract['jdy_account']:
                try:
                    # 调用更新阶段的逻辑
                    result = update_customer_stage(contract['jdy_account'], '合同')
                    if result['success']:
                        updated_contracts.append({
                            'filename': contract['filename'],
                            'jdy_account': contract['jdy_account'],
                            'status': 'updated'
                        })
                        logger.info(f"自动推进合同成功: {contract['jdy_account']} -> 合同阶段")
                    else:
                        updated_contracts.append({
                            'filename': contract['filename'],
                            'jdy_account': contract['jdy_account'],
                            'status': 'failed',
                            'error': result.get('error', '未知错误')
                        })
                except Exception as e:
                    logger.error(f"自动推进合同失败: {str(e)}")
                    updated_contracts.append({
                        'filename': contract['filename'],
                        'jdy_account': contract['jdy_account'],
                        'status': 'error',
                        'error': str(e)
                    })
            else:
                # 没有找到简道云账号的文件也记录，避免重复扫描
                logger.debug(f"文件 {contract['filename']} 未找到简道云账号，已记录跳过")
        
        return {
            'downloads_path': downloads_path,
            'recent_contracts': recent_contracts,
            'updated_contracts': updated_contracts,
            'total_found': len(recent_contracts),
            'total_updated': len([c for c in updated_contracts if c['status'] == 'updated']),
            'last_check': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"监控检查失败: {str(e)}")
        return None

@app.route('/start_auto_monitor', methods=['POST'])
@login_required
def start_auto_monitor():
    """启动自动监控功能"""
    global auto_monitor_enabled, monitor_thread
    
    try:
        with monitor_lock:
            if auto_monitor_enabled:
                return jsonify({
                    'success': False,
                    'error': '自动监控已在运行中'
                }), 400
            
            # 启动后台监控
            auto_monitor_enabled = True
            monitor_thread = threading.Thread(target=background_monitor_worker, daemon=True)
            monitor_thread.start()
            
            logger.info("后台自动监控已启动")
            
            return jsonify({
                'success': True,
                'message': '后台自动监控已启动',
                'status': 'running'
            })
        
    except Exception as e:
        logger.error(f"启动自动监控失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'启动监控失败: {str(e)}'
        }), 500

@app.route('/stop_auto_monitor', methods=['POST'])
@login_required
def stop_auto_monitor():
    """停止自动监控功能"""
    global auto_monitor_enabled, monitor_thread, processed_files
    
    try:
        with monitor_lock:
            if not auto_monitor_enabled:
                return jsonify({
                    'success': False,
                    'error': '自动监控未在运行'
                }), 400
            
            # 停止后台监控
            auto_monitor_enabled = False
            
            # 等待线程结束
            if monitor_thread and monitor_thread.is_alive():
                monitor_thread.join(timeout=5)
            
            monitor_thread = None
            
            # 清理已处理文件记录
            processed_files.clear()
            
            logger.info("后台自动监控已停止，已清理处理记录")
            
            return jsonify({
                'success': True,
                'message': '后台自动监控已停止',
                'status': 'stopped'
            })
        
    except Exception as e:
        logger.error(f"停止自动监控失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'停止监控失败: {str(e)}'
        }), 500

@app.route('/get_monitor_status', methods=['GET'])
@login_required
def get_monitor_status():
    """获取监控状态和结果"""
    global auto_monitor_enabled, monitor_results, last_monitor_check
    
    try:
        with monitor_lock:
            return jsonify({
                'success': True,
                'enabled': auto_monitor_enabled,
                'last_check': last_monitor_check.isoformat() if last_monitor_check else None,
                'results': monitor_results
            })
        
    except Exception as e:
        logger.error(f"获取监控状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'获取状态失败: {str(e)}'
        }), 500


def auto_start_monitor():
    """应用启动时自动启动监控功能"""
    global auto_monitor_enabled, monitor_thread
    
    try:
        with monitor_lock:
            if not auto_monitor_enabled:
                # 启动后台监控
                auto_monitor_enabled = True
                monitor_thread = threading.Thread(target=background_monitor_worker, daemon=True)
                monitor_thread.start()
                logger.info("应用启动时自动启动后台监控成功")
            else:
                logger.info("后台监控已在运行中")
    except Exception as e:
        logger.error(f"自动启动监控失败: {str(e)}")

if __name__ == '__main__':
    # 环境配置
    port = int(os.environ.get('PORT', 8080))
    # 生产环境使用0.0.0.0，开发环境使用localhost
    if os.environ.get('FLASK_ENV') == 'production':
        host = '0.0.0.0'
    else:
        host = os.environ.get('HOST', 'localhost')
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"正在启动Flask应用...")
    print(f"端口: {port}")
    print(f"主机: {host}")
    print(f"调试模式: {debug}")
    print(f"环境: {os.environ.get('FLASK_ENV', 'development')}")
    
    # 应用启动时自动启动监控 - 临时禁用用于调试
    # try:
    #     auto_start_monitor()
    #     print("自动监控启动完成")
    # except Exception as e:
    #     print(f"自动监控启动失败: {str(e)}")
    print("自动监控已临时禁用用于调试")

    print("开始启动Flask服务器...")
    app.run(debug=debug, port=port, host=host)