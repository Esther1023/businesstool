import os
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

# pandas延迟导入
pd = None

def ensure_pandas_imported():
    """确保pandas已导入"""
    global pd
    if pd is None:
        import pandas as pandas_module
        pd = pandas_module
        logging.getLogger(__name__).info("pandas已延迟导入到stage_manager")
    return pd

class StageType(Enum):
    """状态类型枚举"""
    NA = "NA"
    CONTRACT = "合同"
    ADVANCE_INVOICE = "提前开"
    INVOICE = "开票"
    PAID = "回款"
    CUSTOM = "自定义"

class StageValidationError(Exception):
    """状态校验异常"""
    pass

class StageConflictError(Exception):
    """状态冲突异常"""
    pass

class StageManager:
    """优化的状态管理器"""
    
    def __init__(self, excel_path: str, log_file: str = None):
        self.excel_path = excel_path
        self.log_file = log_file or os.path.join(os.getcwd(), 'logs', 'stage_changes.log')
        self._lock = threading.Lock()
        self._setup_logging()
        
        # 状态变更规则定义
        self.stage_rules = {
            StageType.NA.value: [StageType.CONTRACT.value, "增购", "无效", "失联"],
            StageType.CONTRACT.value: [StageType.ADVANCE_INVOICE.value, StageType.INVOICE.value],
            StageType.ADVANCE_INVOICE.value: [StageType.INVOICE.value],
            StageType.INVOICE.value: [StageType.PAID.value],
            StageType.PAID.value: []  # 已回款状态不能再推进
        }
        
        # 状态优先级（数字越大优先级越高）
        self.stage_priority = {
            StageType.NA.value: 0,
            StageType.CONTRACT.value: 1,
            "增购": 1,
            "无效": 1,
            "失联": 1,
            StageType.ADVANCE_INVOICE.value: 2,
            StageType.INVOICE.value: 3,
            StageType.PAID.value: 4
        }
    
    def _setup_logging(self):
        """设置日志记录"""
        # 确保日志目录存在
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 创建专门的状态变更日志记录器
        self.stage_logger = logging.getLogger('stage_manager')
        self.stage_logger.setLevel(logging.INFO)
        
        # 避免重复添加处理器
        if not self.stage_logger.handlers:
            handler = logging.FileHandler(self.log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.stage_logger.addHandler(handler)
    
    def _validate_stage_transition(self, current_stage: str, target_stage: str) -> Tuple[bool, str]:
        """校验状态转换是否合法"""
        # 标准化状态名称
        current_normalized = self._normalize_stage(current_stage)
        target_normalized = self._normalize_stage(target_stage)
        
        # 检查是否为重复推进
        if current_normalized == target_normalized:
            return False, f"状态重复推进：当前已是'{target_normalized}'状态"
        
        # 检查状态优先级（不允许倒退）
        current_priority = self.stage_priority.get(current_normalized, -1)
        target_priority = self.stage_priority.get(target_normalized, -1)
        
        if current_priority >= target_priority and current_priority != -1:
            return False, f"状态倒退：不能从'{current_normalized}'倒退到'{target_normalized}'"
        
        # 检查状态转换规则
        allowed_transitions = self.stage_rules.get(current_normalized, [])
        if target_normalized not in allowed_transitions and current_normalized != StageType.NA.value:
            # 对于自定义状态，允许更灵活的转换
            if target_normalized not in [s.value for s in StageType]:
                return True, "自定义状态转换"
            return False, f"非法状态转换：'{current_normalized}'不能直接转换到'{target_normalized}'"
        
        return True, "状态转换合法"
    
    def _normalize_stage(self, stage: str) -> str:
        """标准化状态名称"""
        if not stage or str(stage).strip() == '':
            return StageType.NA.value
        
        # 检查pandas NaN值
        try:
            pd = ensure_pandas_imported()
            if pd.isna(stage):
                return StageType.NA.value
        except:
            pass
        
        stage_str = str(stage).strip()
        
        # 标准化已知状态
        if '合同' in stage_str:
            return StageType.CONTRACT.value
        elif '提前开' in stage_str:
            return StageType.ADVANCE_INVOICE.value
        elif '开票' in stage_str:
            return StageType.INVOICE.value
        elif '回款' in stage_str or '已付' in stage_str:
            return StageType.PAID.value
        elif stage_str.upper() == 'NA':
            return StageType.NA.value
        
        return stage_str  # 保持自定义状态
    
    def _log_stage_change(self, jdy_id: str, old_stage: str, new_stage: str, 
                         success: bool, error_msg: str = None, metadata: Dict = None):
        """记录状态变更日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'jdy_id': jdy_id,
            'old_stage': old_stage,
            'new_stage': new_stage,
            'success': success,
            'error_msg': error_msg,
            'metadata': metadata or {}
        }
        
        log_message = json.dumps(log_entry, ensure_ascii=False)
        
        if success:
            self.stage_logger.info(f"状态变更成功: {log_message}")
        else:
            self.stage_logger.error(f"状态变更失败: {log_message}")
    
    def _detect_conflicts(self, df, jdy_id: str) -> List[Dict]:
        """检测状态冲突"""
        conflicts = []
        
        # 查找所有匹配的记录
        matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
        
        if len(matching_rows) > 1:
            # 检查是否有不同的状态
            stages = matching_rows['客户阶段'].dropna().unique()
            if len(stages) > 1:
                conflicts.append({
                    'type': 'multiple_stages',
                    'message': f"客户{jdy_id}存在多个不同状态: {list(stages)}",
                    'affected_rows': matching_rows.index.tolist()
                })
        
        return conflicts
    
    def update_stage(self, jdy_id: str, target_stage: str, 
                    force: bool = False, metadata: Dict = None) -> Dict:
        """更新客户阶段状态（原子性操作）"""
        with self._lock:  # 确保操作的原子性
            try:
                # 1. 参数校验
                if not jdy_id or not target_stage:
                    error_msg = "缺少必要参数：jdy_id和target_stage不能为空"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'validation'}
                
                # 2. 文件存在性检查
                if not os.path.exists(self.excel_path):
                    error_msg = f"Excel文件不存在: {self.excel_path}"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'file_not_found'}
                
                # 3. 读取Excel文件
                try:
                    pd = ensure_pandas_imported()
                    df = pd.read_excel(self.excel_path)
                except Exception as e:
                    error_msg = f"读取Excel文件失败: {str(e)}"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'file_read_error'}
                
                # 4. 检查必要列
                if '用户ID' not in df.columns:
                    error_msg = "Excel文件格式错误：缺少用户ID列"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'column_missing'}
                
                # 5. 查找匹配记录
                matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
                
                if matching_rows.empty:
                    error_msg = f"未找到客户记录: {jdy_id}"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'customer_not_found'}
                
                # 6. 检查或创建阶段列
                stage_column = '客户阶段'
                if stage_column not in df.columns:
                    df[stage_column] = ''
                
                # 7. 冲突检测
                conflicts = self._detect_conflicts(df, jdy_id)
                if conflicts and not force:
                    error_msg = f"检测到状态冲突: {conflicts[0]['message']}"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {
                        'success': False, 
                        'error': error_msg, 
                        'error_type': 'conflict',
                        'conflicts': conflicts
                    }
                
                # 8. 状态校验
                updated_records = []
                validation_errors = []
                
                for index in matching_rows.index:
                    stage_value = df.loc[index, stage_column]
                    current_stage = stage_value if (pd.notna(stage_value) if pd else stage_value is not None) else ''
                    current_normalized = self._normalize_stage(current_stage)
                    
                    # 状态转换校验
                    if not force:
                        is_valid, validation_msg = self._validate_stage_transition(current_normalized, target_stage)
                        if not is_valid:
                            validation_errors.append({
                                'index': index,
                                'current_stage': current_normalized,
                                'error': validation_msg
                            })
                            continue
                    
                    updated_records.append({
                        'index': index,
                        'old_stage': current_normalized,
                        'new_stage': target_stage
                    })
                
                # 9. 如果有校验错误且非强制模式，返回错误
                if validation_errors and not force:
                    error_msg = f"状态校验失败: {validation_errors[0]['error']}"
                    self._log_stage_change(jdy_id, validation_errors[0]['current_stage'], 
                                         target_stage, False, error_msg, metadata)
                    return {
                        'success': False, 
                        'error': error_msg, 
                        'error_type': 'validation_failed',
                        'validation_errors': validation_errors
                    }
                
                # 10. 执行状态更新
                if not updated_records:
                    error_msg = "没有记录需要更新"
                    self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'no_updates'}
                
                # 更新记录
                for record in updated_records:
                    df.loc[record['index'], stage_column] = target_stage
                
                # 11. 保存文件
                try:
                    df.to_excel(self.excel_path, index=False)
                except Exception as e:
                    error_msg = f"保存Excel文件失败: {str(e)}"
                    self._log_stage_change(jdy_id, updated_records[0]['old_stage'], 
                                         target_stage, False, error_msg, metadata)
                    return {'success': False, 'error': error_msg, 'error_type': 'file_save_error'}
                
                # 12. 记录成功日志
                for record in updated_records:
                    self._log_stage_change(jdy_id, record['old_stage'], target_stage, True, None, metadata)
                
                return {
                    'success': True,
                    'message': f'客户 {jdy_id} 已成功推进到 {target_stage} 阶段',
                    'updated_count': len(updated_records),
                    'updated_records': updated_records,
                    'conflicts_resolved': len(conflicts) if force else 0
                }
                
            except Exception as e:
                error_msg = f"状态更新异常: {str(e)}"
                self._log_stage_change(jdy_id, '', target_stage, False, error_msg, metadata)
                return {'success': False, 'error': error_msg, 'error_type': 'system_error'}
    
    def get_stage_history(self, jdy_id: str = None, limit: int = 100) -> List[Dict]:
        """获取状态变更历史"""
        try:
            if not os.path.exists(self.log_file):
                return []
            
            history = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 倒序读取最近的记录
            for line in reversed(lines[-limit:]):
                try:
                    # 提取JSON部分
                    if '状态变更成功:' in line or '状态变更失败:' in line:
                        json_start = line.find('{')
                        if json_start != -1:
                            json_str = line[json_start:].strip()
                            log_entry = json.loads(json_str)
                            
                            # 如果指定了jdy_id，则过滤
                            if jdy_id is None or log_entry.get('jdy_id') == jdy_id:
                                history.append(log_entry)
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return history
            
        except Exception as e:
            logging.error(f"获取状态历史失败: {str(e)}")
            return []
    
    def validate_stage_batch(self, updates: List[Dict]) -> Dict:
        """批量状态校验"""
        results = {
            'valid': [],
            'invalid': [],
            'conflicts': []
        }
        
        try:
            pd = ensure_pandas_imported()
            df = pd.read_excel(self.excel_path)
            
            for update in updates:
                jdy_id = update.get('jdy_id')
                target_stage = update.get('target_stage')
                
                if not jdy_id or not target_stage:
                    results['invalid'].append({
                        'update': update,
                        'error': '缺少必要参数'
                    })
                    continue
                
                # 查找记录
                matching_rows = df[df['用户ID'].astype(str).str.contains(str(jdy_id), case=False, na=False)]
                
                if matching_rows.empty:
                    results['invalid'].append({
                        'update': update,
                        'error': f'未找到客户记录: {jdy_id}'
                    })
                    continue
                
                # 检查冲突
                conflicts = self._detect_conflicts(df, jdy_id)
                if conflicts:
                    results['conflicts'].append({
                        'update': update,
                        'conflicts': conflicts
                    })
                    continue
                
                # 状态校验
                stage_column = '客户阶段'
                current_stage = ''
                if stage_column in df.columns:
                    current_stage = df.loc[matching_rows.index[0], stage_column]
                    current_stage = current_stage if (pd.notna(current_stage) if pd else current_stage is not None) else ''
                
                is_valid, validation_msg = self._validate_stage_transition(current_stage, target_stage)
                
                if is_valid:
                    results['valid'].append(update)
                else:
                    results['invalid'].append({
                        'update': update,
                        'error': validation_msg
                    })
        
        except Exception as e:
            results['error'] = f'批量校验失败: {str(e)}'
        
        return results