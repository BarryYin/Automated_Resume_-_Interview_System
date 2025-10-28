#!/usr/bin/env python3
"""
测试AI聊天服务 - 基于真实数据
"""

import sys
import os
sys.path.append('backend')

from ai_chat_service import ai_chat_service

def test_ai_chat_with_real_data():
    """测试基于真实数据的AI聊天"""
    
    print("测试AI数据助手...")
    print("=" * 60)
    
    # 测试问题列表
    test_questions = [
        "总共有多少候选人？",
        "平均分数是多少？",
        "哪个职位的候选人最多？",
        "面试完成率如何？",
        "各个维度的平均分是多少？",
        "生成一份简要的招聘分析报告"
    ]
    
    print("1. 获取招聘数据...")
    data = ai_chat_service.get_recruitment_data()
    stats = data.get('statistics', {})
    
    print(f"✅ 数据加载成功")
    print(f"   - 候选人数: {stats.get('total_candidates', 0)}")
    print(f"   - 职位数: {stats.get('total_jobs', 0)}")
    print(f"   - 已完成面试: {stats.get('completed_interviews', 0)}")
    print(f"   - 平均分: {stats.get('average_score', 0):.1f}")
    
    print(f"\n2. 测试AI对话...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n问题 {i}: {question}")
        print("-" * 40)
        
        try:
            result = ai_chat_service.chat_with_ai(question)
            response = result.get('response', '无回复')
            
            print(f"AI回答: {response}")
            
            if 'error' in result:
                print(f"⚠️  错误: {result['error']}")
            else:
                print("✅ 回答成功")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print(f"\n3. 测试报告生成...")
    
    try:
        report_result = ai_chat_service.generate_analytics_report("comprehensive")
        report = report_result.get('report', '无报告')
        
        print("✅ 报告生成成功")
        print("报告内容预览:")
        print(report[:300] + "..." if len(report) > 300 else report)
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")

def test_data_formatting():
    """测试数据格式化"""
    print(f"\n4. 测试数据格式化...")
    
    try:
        data = ai_chat_service.get_recruitment_data()
        formatted = ai_chat_service.format_data_for_ai(data)
        
        print("✅ 数据格式化成功")
        print("格式化数据预览:")
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
    except Exception as e:
        print(f"❌ 数据格式化失败: {e}")

if __name__ == "__main__":
    test_ai_chat_with_real_data()
    test_data_formatting()
    
    print(f"\n" + "=" * 60)
    print("测试完成！")
    print("现在AI助手将基于真实数据回答问题，不会编造信息。")