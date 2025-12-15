#!/usr/bin/env python3
"""
测试百度文心大模型集成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service import llm_service
from ai_chat_service import ai_chat_service
import json

def test_llm_service():
    """测试LLM服务"""
    print("🧪 测试LLM服务...")
    
    # 测试数据
    candidate_info = {
        "name": "张三",
        "position": "Python开发工程师",
        "email": "zhangsan@example.com"
    }
    
    resume_text = "具有3年Python开发经验，熟悉Django、Flask框架，有大型项目经验。"
    job_description = "招聘Python后端开发工程师，要求熟悉Web开发框架，有团队协作经验。"
    
    try:
        result = llm_service.generate_interview_questions(
            candidate_info, resume_text, job_description
        )
        
        print("✅ LLM服务测试成功!")
        print(f"📝 生成了 {len(result.get('questions', []))} 个问题")
        
        # 显示第一个问题
        if result.get('questions'):
            first_q = result['questions'][0]
            print(f"🔍 示例问题: {first_q.get('question', '')}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM服务测试失败: {e}")
        return False

def test_ai_chat_service():
    """测试AI聊天服务"""
    print("\n🧪 测试AI聊天服务...")
    
    try:
        result = ai_chat_service.chat_with_ai("请分析一下当前的招聘数据概况")
        
        print("✅ AI聊天服务测试成功!")
        print(f"📝 AI回复预览: {result.get('response', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI聊天服务测试失败: {e}")
        return False

def test_answer_evaluation():
    """测试回答评估功能"""
    print("\n🧪 测试回答评估功能...")
    
    try:
        question = "请介绍一下您的Python开发经验"
        answer = "我有3年的Python开发经验，主要使用Django框架开发Web应用，参与过电商平台的后端开发。"
        dimension = "Knowledge"
        
        result = llm_service.evaluate_answer(question, answer, dimension)
        
        print("✅ 回答评估测试成功!")
        print(f"📊 评分: {result.get('score', 0)}分")
        print(f"💬 反馈: {result.get('feedback', '')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 回答评估测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎯 开始测试百度文心大模型集成...")
    print("=" * 50)
    
    # 显示当前配置
    from config import config
    print(f"🔧 当前配置:")
    print(f"   模型: {config.get('llm.model')}")
    print(f"   API地址: {config.get('llm.base_url')}")
    print(f"   API密钥: {config.get('llm.api_key')[:20]}...")
    print("=" * 50)
    
    tests = [
        test_llm_service,
        test_ai_chat_service,
        test_answer_evaluation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("✅ 所有测试通过! 百度文心大模型集成成功!")
    else:
        print("⚠️ 部分测试失败，请检查配置和网络连接")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)