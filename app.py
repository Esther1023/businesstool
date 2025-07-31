from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
import os
import tempfile
import pandas as pd
from datetime import datetime
import logging

# 延迟导入OCR相关模块，避免启动时失败
template_handler = None
ocr_service = None

# 尝试导入OCR服务
try:
    from ocr_service import OCRService
    OCR_SERVICE_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"OCR服务导入失败: {str(e)}")
    OCR_SERVICE_AVAILABLE = False

# 尝试导入模板处理器
try:
    from template_handler import TemplateHandler
    TEMPLATE_HANDLER_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
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
    log_file = os.path.join(log_dir, 'app.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

logger = logging.getLogger(__name__)

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

# 初始化模板处理器（容错处理）
try:
    if TEMPLATE_HANDLER_AVAILABLE:
        template_handler = TemplateHandler()
        logger.info("模板处理器初始化成功")
    else:
        logger.warning("模板处理器不可用：导入失败")
        template_handler = None
except Exception as e:
    logger.warning(f"模板处理器初始化失败: {str(e)}")
    template_handler = None

# 存储最后导入时间
last_import_time = None

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
                'template_handler': 'available'
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
        if (username == 'Esther' and password == '967420') or (username == 'Mia' and password == '123456'):  # 简单的用户名密码验证
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

# 登出功能
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
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
    excel_path = '六大战区简道云客户.xlsx'
    try:
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return None
        df = pd.read_excel(excel_path)
        return df
    except Exception as e:
        logger.error(f"Excel加载错误: {str(e)}")
        return None

@app.route('/')
@login_required
def index():
    return render_template('index.html', last_import_time=last_import_time)

@app.route('/test', methods=['GET'])
def test():
    return 'Hello, World!'
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

        # 保存文件
        file.save('六大战区简道云客户.xlsx')
        
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

@app.route('/get_future_expiring_customers')
@login_required
def get_future_expiring_customers():
    try:
        # 检查文件是否存在
        excel_path = os.path.join(os.getcwd(), '六大战区简道云客户.xlsx')
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        if '到期日期' not in df.columns or '用户ID' not in df.columns or '账号-企业名称' not in df.columns or '续费责任销售' not in df.columns:
            logger.error("Excel文件中缺少必要列")
            return jsonify({'error': '数据格式错误：缺少必要列'}), 500
        
        # 获取当前日期
        now = datetime.now()
        
        # 计算23天后和30天后的日期
        days_23_later = now + pd.Timedelta(days=23)
        days_30_later = now + pd.Timedelta(days=30)
        
        # 筛选出23-30天内将要过期的客户
        esther_customers = []
        other_customers = []
        
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期'])
                    # 如果过期时间在23天后和30天后之间
                    if days_23_later <= expiry_date <= days_30_later:
                        # 处理责任销售字段 - 优先使用续费责任销售，如果为空则使用责任销售中英文
                        sales_raw = row.get('续费责任销售', '')
                        if pd.isna(sales_raw) or sales_raw == '' or str(sales_raw).lower() == 'nan':
                            sales_person = str(row.get('责任销售中英文', ''))
                        else:
                            sales_person = str(sales_raw)
                        
                        customer_info = {
                            'id': str(row.get('用户ID', '')),
                            'expiry_date': expiry_date.strftime('%Y年%m月%d日'),
                            'jdy_account': str(row.get('用户ID', '')),
                            'company_name': str(row.get('账号-企业名称', '')),
                            'sales_person': sales_person
                        }
                        
                        # 根据续费责任销售分类（使用处理后的sales_person）
                        if '朱晓琳' in sales_person or 'Esther' in sales_person:
                            esther_customers.append(customer_info)
                        else:
                            other_customers.append(customer_info)
                            
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按过期日期排序
        esther_customers.sort(key=lambda x: x['expiry_date'])
        other_customers.sort(key=lambda x: x['expiry_date'])
        
        logger.info(f"找到{len(esther_customers)}个Esther负责的即将过期客户和{len(other_customers)}个其他销售负责的即将过期客户")
        return jsonify({
            'esther_customers': esther_customers,
            'other_customers': other_customers
        })

    except Exception as e:
        logger.error(f"获取未来即将过期客户失败: {str(e)}")
        return jsonify({'error': f'获取未来即将过期客户失败: {str(e)}'}), 500

@app.route('/get_expiring_customers')
@login_required
def get_expiring_customers():
    try:
        # 获取当前日期
        now = datetime.now()
        today = now.date()
        
        # 检查文件是否存在
        excel_path = os.path.join(os.getcwd(), '六大战区简道云客户.xlsx')
        logger.info(f"尝试读取文件: {excel_path}")
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'expiring_customers': [], 'error': '数据文件不存在', 'today_date': today.strftime('%Y年%m月%d日')})

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'expiring_customers': [], 'error': '数据文件读取失败', 'today_date': today.strftime('%Y年%m月%d日')})

        if '到期日期' not in df.columns or '用户ID' not in df.columns or '账号-企业名称' not in df.columns:
            logger.error("Excel文件中缺少必要列")
            return jsonify({'expiring_customers': [], 'error': '数据格式错误：缺少必要列', 'today_date': today.strftime('%Y年%m月%d日')})
        
        # 定义节假日（可以根据需要扩展）
        holidays = [
            # 2024年节假日
            '2024-01-01', '2024-02-10', '2024-02-11', '2024-02-12', '2024-02-13', '2024-02-14', '2024-02-15', '2024-02-16', '2024-02-17',
            '2024-04-04', '2024-04-05', '2024-04-06',
            '2024-05-01', '2024-05-02', '2024-05-03',
            '2024-06-10',
            '2024-09-15', '2024-09-16', '2024-09-17',
            '2024-10-01', '2024-10-02', '2024-10-03', '2024-10-04', '2024-10-05', '2024-10-06', '2024-10-07',
            # 2025年节假日
            '2025-01-01', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-01', '2025-02-02', '2025-02-03',
            '2025-04-05', '2025-04-06', '2025-04-07',
            '2025-05-01', '2025-05-02', '2025-05-03',
            '2025-06-09',
            '2025-09-06', '2025-09-07', '2025-09-08',
            '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05', '2025-10-06', '2025-10-07'
        ]
        
        holiday_dates = [datetime.strptime(h, '%Y-%m-%d').date() for h in holidays]
        
        # 判断提醒逻辑
        weekday = today.weekday()  # 0=周一, 1=周二, ..., 6=周日
        target_dates = []
        reminder_type = ""
        
        # 检查是否是节假日前一天
        is_before_holiday = False
        holiday_period = []
        
        for holiday in holiday_dates:
            if holiday == today + pd.Timedelta(days=1):  # 明天是节假日
                is_before_holiday = True
                # 找到连续的节假日期间
                current_date = holiday
                while current_date in holiday_dates:
                    holiday_period.append(current_date)
                    current_date += pd.Timedelta(days=1)
                break
        
        if is_before_holiday:
            # 节假日前一天：提醒节假日期间到期的客户
            target_dates = holiday_period
            reminder_type = f"节假日期间到期提醒（{holiday_period[0].strftime('%m月%d日')}至{holiday_period[-1].strftime('%m月%d日')}）"
            logger.info(f"节假日前一天，提醒节假日期间到期的客户: {target_dates}")
        elif weekday == 4:  # 周五
            # 周五：提醒周六和周日到期的客户
            saturday = today + pd.Timedelta(days=1)
            sunday = today + pd.Timedelta(days=2)
            target_dates = [saturday, sunday]
            reminder_type = "周末到期提醒"
            logger.info("周五，提醒周末到期的客户")
        elif weekday < 4:  # 周一到周四
            # 平时：提醒明天到期的客户
            tomorrow = today + pd.Timedelta(days=1)
            target_dates = [tomorrow]
            reminder_type = "明天到期提醒"
            logger.info("工作日，提醒明天到期的客户")
        else:  # 周六、周日
            # 周末不提醒
            logger.info("今天是周末，不显示到期客户提醒")
            return jsonify({
                'expiring_customers': [], 
                'message': '周末愉快，暂不显示到期提醒',
                'today_date': today.strftime('%Y年%m月%d日'),
                'reminder_type': '周末休息'
            })
        
        # 筛选出目标日期到期的客户
        expiring_customers = []
        for _, row in df.iterrows():
            if pd.notna(row['到期日期']):
                try:
                    expiry_date = pd.to_datetime(row['到期日期']).date()
                    if expiry_date in target_dates:
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
                        
                        expiring_customers.append({
                            'expiry_date': f"{date_label} ({expiry_date.strftime('%Y年%m月%d日')})",
                            'jdy_account': str(row.get('用户ID', '')),
                            'company_name': str(row.get('账号-企业名称', '')),
                            'sales_person': sales_person,
                            'days_until_expiry': days_until_expiry
                        })
                except Exception as e:
                    logger.warning(f"日期转换错误: {str(e)}")
                    continue
        
        # 按到期日期排序
        expiring_customers.sort(key=lambda x: x['days_until_expiry'])
        
        if len(expiring_customers) == 0:
            message = f"未来几天没有到期的客户"
            logger.info(message)
            return jsonify({
                'expiring_customers': [], 
                'message': message,
                'today_date': today.strftime('%Y年%m月%d日'),
                'reminder_type': reminder_type
            })
        else:
            logger.info(f"找到{len(expiring_customers)}个即将过期的客户")
            return jsonify({
                'expiring_customers': expiring_customers,
                'today_date': today.strftime('%Y年%m月%d日'),
                'reminder_type': reminder_type
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
        excel_path = '六大战区简道云客户.xlsx'
        if not os.path.exists(excel_path):
            logger.error(f"文件不存在: {excel_path}")
            return jsonify({'error': '数据文件不存在'}), 500

        try:
            df = pd.read_excel(excel_path)
            logger.info(f"成功读取Excel文件，共{len(df)}行数据")
        except Exception as e:
            logger.error(f"Excel读取错误: {str(e)}")
            return jsonify({'error': '数据文件读取失败'}), 500

        # 检查必要的列是否存在
        required_columns = ['用户ID', '账号-企业名称']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Excel文件中缺少'{col}'列")
                return jsonify({'error': f'数据格式错误：缺少{col}列'}), 500
        
        # 根据查询条件进行模糊匹配
        if jdy_id:
            matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        else:
            matching_rows = df[df['账号-企业名称'].astype(str).str.contains(str(company_name), case=False, na=False)]
            
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

@app.route('/docx_templates/<template_name>')
def get_template(template_name):
    if not template_name.endswith('.docx'):
        return '不支持的文件类型', 400

    try:
        # 从docx_templates目录加载模板文件
        template_path = os.path.join(os.getcwd(), 'templates', 'docx_templates', template_name)
        if not os.path.exists(template_path):
            logger.error(f"模板文件不存在: {template_path}")
            return '模板文件不存在', 404

        logger.info(f"正在加载模板文件: {template_path}")
        return send_file(
            template_path,
            as_attachment=False,  # 不作为附件发送，这样浏览器不会下载而是直接传给前端
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

        # 处理模板
        handler = TemplateHandler(temp_template.name)
        output_path = handler.process_template(form_data, temp_output.name)
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
        return f'生成合同时发生错误: {str(e)}', 500

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

if __name__ == '__main__':
    # 环境配置
    port = int(os.environ.get('PORT', 8080))
    # 生产环境使用0.0.0.0，开发环境使用localhost
    if os.environ.get('FLASK_ENV') == 'production':
        host = '0.0.0.0'
    else:
        host = os.environ.get('HOST', 'localhost')
    debug = os.environ.get('FLASK_ENV') != 'production'

    app.run(debug=debug, port=port, host=host)
