#!/usr/bin/env python3
"""
AI招聘系统启动脚本
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)

def install_dependencies():
    """安装依赖"""
    print("正在安装Python依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ])
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        sys.exit(1)

def start_backend():
    """启动后端服务"""
    print("正在启动后端服务...")
    os.chdir("backend")
    
    try:
        # 启动FastAPI服务
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
        return process
    except Exception as e:
        print(f"❌ 后端启动失败: {e}")
        sys.exit(1)

def start_frontend():
    """启动前端服务"""
    print("正在启动前端服务...")
    
    # 简单的HTTP服务器
    os.chdir("../frontend")
    
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ])
        return process
    except Exception as e:
        print(f"❌ 前端启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🚀 AI招聘系统启动器")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖
    install_dependencies()
    
    # 启动后端
    backend_process = start_backend()
    
    # 等待后端启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    
    # 等待前端启动
    print("⏳ 等待前端服务启动...")
    time.sleep(2)
    
    print("\n✅ 系统启动成功!")
    print("📱 前端地址: http://localhost:3000")
    print("🔧 后端API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("\n按 Ctrl+C 停止服务")
    
    # 自动打开浏览器
    try:
        webbrowser.open("http://localhost:3000")
    except:
        pass
    
    try:
        # 等待进程
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()