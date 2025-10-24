#!/usr/bin/env python3
"""
修复app.py中所有pandas使用的脚本
将所有pd.xxx调用替换为延迟导入的版本
"""

import re

def fix_pandas_usage():
    # 读取app.py文件
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义需要替换的pandas函数
    pandas_functions = [
        'pd.read_excel',
        'pd.DataFrame', 
        'pd.isna',
        'pd.notna',
        'pd.to_datetime',
        'pd.Timedelta'
    ]
    
    # 为每个函数创建替换规则
    for func in pandas_functions:
        # 查找所有使用该函数的地方
        pattern = re.escape(func) + r'\('
        matches = list(re.finditer(pattern, content))
        
        if matches:
            print(f"找到 {len(matches)} 个 {func} 的使用")
            
            # 从后往前替换，避免位置偏移
            for match in reversed(matches):
                start = match.start()
                # 在使用前添加ensure_pandas_imported()调用
                # 找到该行的开始
                line_start = content.rfind('\n', 0, start) + 1
                indent = ''
                for char in content[line_start:start]:
                    if char in ' \t':
                        indent += char
                    else:
                        break
                
                # 插入pd = ensure_pandas_imported()
                insert_text = f"{indent}pd = ensure_pandas_imported()\n"
                content = content[:line_start] + insert_text + content[line_start:]
    
    # 写回文件
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成！")

if __name__ == '__main__':
    fix_pandas_usage()