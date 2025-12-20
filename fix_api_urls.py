#!/usr/bin/env python3
"""
批量替换前端JavaScript文件中的硬编码API地址
将 http://localhost:8000 替换为使用配置文件的方式
"""

import os
import re
from pathlib import Path

def fix_js_file(file_path):
    """修复单个JS文件中的API地址"""
    print(f"处理文件: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 替换模式
    replacements = [
        # 基本的localhost:8000替换
        (r"'http://localhost:8000/api/([^']*)'", r"buildApiUrl('/api/\1')"),
        (r'"http://localhost:8000/api/([^"]*)"', r'buildApiUrl("/api/\1")'),
        (r"`http://localhost:8000/api/([^`]*)`", r'buildApiUrl(`/api/\1`)'),
        
        # 模板字符串中的替换
        (r"`http://localhost:8000/api/\$\{([^}]*)\}`", r'buildApiUrl(`/api/${\\1}`)'),
        
        # 特殊情况：直接的http://localhost:8000（不带/api）
        (r"'http://localhost:8000'", r"buildApiUrl('')"),
        (r'"http://localhost:8000"', r'buildApiUrl("")'),
        
        # API_CONFIG.BASE_URL的情况
        (r"'http://localhost:8000',", r"getApiBaseUrl(),"),
        (r'"http://localhost:8000",', r'getApiBaseUrl(),'),
    ]
    
    # 应用替换
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ 已更新")
        return True
    else:
        print(f"  ⏭️  无需更新")
        return False

def main():
    """主函数"""
    frontend_js_dir = Path("frontend/js")
    
    if not frontend_js_dir.exists():
        print("错误: frontend/js 目录不存在")
        return
    
    updated_files = []
    
    # 遍历所有JS文件
    for js_file in frontend_js_dir.glob("*.js"):
        if js_file.name == "config.js":  # 跳过配置文件本身
            continue
            
        if fix_js_file(js_file):
            updated_files.append(js_file.name)
    
    print(f"\n处理完成!")
    print(f"更新了 {len(updated_files)} 个文件:")
    for file_name in updated_files:
        print(f"  - {file_name}")
    
    if updated_files:
        print("\n注意事项:")
        print("1. 请确保所有HTML文件都引入了 js/config.js")
        print("2. 部署时只需要修改 js/config.js 中的 getApiBaseUrl() 函数")
        print("3. 建议测试所有功能确保API调用正常")

if __name__ == "__main__":
    main()