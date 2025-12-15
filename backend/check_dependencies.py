#!/usr/bin/env python3
"""
检查所有依赖包是否正确安装
"""

import sys

def check_package(package_name, import_name=None):
    """检查单个包是否可以导入"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: {e}")
        return False

def main():
    """检查所有依赖包"""
    print("🔍 检查项目依赖包...")
    print("=" * 40)
    
    # 定义需要检查的包
    packages = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("sqlalchemy", "sqlalchemy"),
        ("python-multipart", "multipart"),
        ("python-jose", "jose"),
        ("passlib", "passlib"),
        ("python-dotenv", "dotenv"),
        ("openai", "openai"),
        ("httpx", "httpx"),
        ("PyPDF2", "PyPDF2"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("PyJWT", "jwt"),
        ("pdfplumber", "pdfplumber"),
        ("python-docx", "docx"),
        ("numpy", "numpy"),
    ]
    
    # 检查标准库
    standard_libs = [
        ("sqlite3", "sqlite3"),
        ("json", "json"),
        ("pathlib", "pathlib"),
        ("re", "re"),
        ("os", "os"),
        ("sys", "sys"),
        ("datetime", "datetime"),
        ("hashlib", "hashlib"),
        ("secrets", "secrets"),
        ("smtplib", "smtplib"),
        ("ssl", "ssl"),
        ("email", "email"),
        ("typing", "typing"),
        ("logging", "logging"),
        ("asyncio", "asyncio"),
        ("traceback", "traceback"),
        ("uuid", "uuid"),
    ]
    
    print("📦 第三方依赖包:")
    failed_packages = []
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            failed_packages.append(package_name)
    
    print(f"\n📚 标准库:")
    failed_stdlib = []
    for lib_name, import_name in standard_libs:
        if not check_package(lib_name, import_name):
            failed_stdlib.append(lib_name)
    
    print("\n" + "=" * 40)
    
    if not failed_packages and not failed_stdlib:
        print("🎉 所有依赖包检查通过!")
        
        # 测试项目模块导入
        print("\n🧪 测试项目模块导入:")
        try:
            sys.path.append('.')
            from llm_service import llm_service
            print("✅ llm_service")
            
            from ai_chat_service import ai_chat_service
            print("✅ ai_chat_service")
            
            from resume_parser import resume_parser
            print("✅ resume_parser")
            
            from excel_data_loader import excel_loader
            print("✅ excel_data_loader")
            
            from email_service import email_service
            print("✅ email_service")
            
            print("\n🎉 所有项目模块导入成功!")
            return True
            
        except Exception as e:
            print(f"❌ 项目模块导入失败: {e}")
            return False
    else:
        if failed_packages:
            print(f"❌ 缺失的第三方包: {', '.join(failed_packages)}")
            print("💡 运行以下命令安装:")
            print(f"   pip install {' '.join(failed_packages)}")
        
        if failed_stdlib:
            print(f"❌ 缺失的标准库: {', '.join(failed_stdlib)}")
            print("💡 这些是Python标准库，请检查Python安装")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)