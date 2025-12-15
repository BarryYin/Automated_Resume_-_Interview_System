#!/bin/bash

echo "🚀 开始安装项目依赖..."
echo "================================"

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "🐍 Python版本: $python_version"

# 检查pip版本
pip_version=$(pip3 --version 2>&1)
echo "📦 pip版本: $pip_version"

echo ""
echo "📋 安装requirements.txt中的依赖包..."

# 安装依赖
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖安装完成!"
    echo ""
    echo "🔍 运行依赖检查..."
    python3 check_dependencies.py
else
    echo ""
    echo "❌ 依赖安装失败!"
    echo "💡 请检查网络连接和pip配置"
    exit 1
fi

echo ""
echo "🎉 安装完成! 现在可以运行项目了:"
echo "   python3 main.py"