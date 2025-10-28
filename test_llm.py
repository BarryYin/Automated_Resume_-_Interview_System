#!/usr/bin/env python3
"""
测试LLM服务
"""

import sys
import os
sys.path.append('backend')

from llm_service import llm_service

def test_llm_service():
    """测试LLM服务功能"""
    
    print("测试LLM服务...")
    print("=" * 50)
    
    # 测试候选人信息
    candidate_info = {
        'name': '张三',
        'email': 'zhangsan@example.com',
        'position': 'Python工程师服务器端开发-AIGC领域'
    }
    
    # 模拟简历内容
    resume_text = """
    张三
    Python开发工程师
    
    教育背景：
    - 计算机科学与技术学士学位
    - 熟悉Python、Django、Flask框架
    
    工作经验：
    - 3年Python开发经验
    - 参与过多个Web项目开发
    - 熟悉数据库设计和优化
    
    技能：
    - Python, Django, Flask
    - MySQL, PostgreSQL
    - Git, Docker
    """
    
    # 职位描述
    job_description = """
    Python工程师服务器端开发-AIGC领域
    职位要求：设计、开发、测试和维护Python应用程序
    能力要求：至少2年Python开发经验，熟练掌握相关框架
    """
    
    print("1. 测试生成面试问题...")
    try:
        questions_data = llm_service.generate_interview_questions(
            candidate_info, resume_text, job_description
        )
        
        print(f"✅ 成功生成 {len(questions_data['questions'])} 个问题")
        print(f"面试策略: {questions_data.get('interview_strategy', '无')}")
        
        print("\n生成的问题:")
        for i, q in enumerate(questions_data['questions'][:3], 1):
            print(f"{i}. [{q['dimension']}] {q['question']}")
            if q.get('follow_up'):
                print(f"   追问: {q['follow_up']}")
        
        # 测试评估回答
        print("\n2. 测试评估回答...")
        test_question = questions_data['questions'][0]
        test_answer = "我有3年的Python开发经验，熟悉Django和Flask框架，参与过多个项目的开发。"
        
        evaluation = llm_service.evaluate_answer(
            test_question['question'], 
            test_answer, 
            test_question['dimension']
        )
        
        print(f"✅ 评估完成")
        print(f"评分: {evaluation['score']}分")
        print(f"反馈: {evaluation['feedback']}")
        print(f"优势: {evaluation.get('strengths', [])}")
        print(f"改进建议: {evaluation.get('improvements', [])}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_service()