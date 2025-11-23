#!/bin/bash

echo "======================================"
echo "  AI招聘系统 - 面试问题管理功能测试"
echo "======================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✓ Python环境检查通过"

# 检查依赖
echo ""
echo "检查依赖包..."
cd backend

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  警告: 缺少依赖包，正在安装..."
    pip3 install -r requirements.txt
fi

echo "✓ 依赖包检查通过"

# 启动后端服务
echo ""
echo "======================================"
echo "启动后端服务..."
echo "======================================"
echo ""

python3 main.py &
BACKEND_PID=$!

echo "后端服务已启动 (PID: $BACKEND_PID)"
echo "API地址: http://localhost:8000"
echo ""

# 等待服务启动
echo "等待服务启动..."
sleep 3

# 检查服务是否正常
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✓ 后端服务运行正常"
else
    echo "❌ 后端服务启动失败"
    kill $BACKEND_PID
    exit 1
fi

echo ""
echo "======================================"
echo "  测试页面"
echo "======================================"
echo ""
echo "1. 管理员控制台: file://$(pwd)/../frontend/dashboard.html"
echo "2. API测试页面: file://$(pwd)/../test_questions_api.html"
echo "3. 首页: file://$(pwd)/../frontend/home.html"
echo ""
echo "======================================"
echo "  测试步骤"
echo "======================================"
echo ""
echo "1. 打开管理员控制台"
echo "2. 登录管理员账号（如果需要）"
echo "3. 切换到'候选人'标签页"
echo "4. 点击任意候选人的'面试问题'按钮"
echo "5. 测试生成和重新生成功能"
echo ""
echo "或者打开 test_questions_api.html 进行API测试"
echo ""
echo "======================================"
echo "  按 Ctrl+C 停止服务"
echo "======================================"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID; echo '服务已停止'; exit 0" INT

wait $BACKEND_PID
