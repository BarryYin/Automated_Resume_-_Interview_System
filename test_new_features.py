#!/usr/bin/env python3
"""
测试面试问题管理功能
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_get_candidates():
    """测试获取候选人列表（含问题状态）"""
    print_section("测试1: 获取候选人列表")
    
    try:
        response = requests.get(f"{API_BASE}/api/candidates")
        response.raise_for_status()
        
        candidates = response.json()
        print(f"✓ 成功获取 {len(candidates)} 个候选人\n")
        
        # 显示前3个候选人的信息
        for i, candidate in enumerate(candidates[:3], 1):
            print(f"{i}. {candidate['name']}")
            print(f"   职位: {candidate['position']}")
            print(f"   状态: {candidate['status']}")
            print(f"   是否有问题: {'是' if candidate.get('has_questions') else '否'}")
            if candidate.get('has_questions'):
                print(f"   问题数量: {len(candidate.get('interview_questions', []))}")
                print(f"   更新时间: {candidate.get('questions_generated_at', '未知')}")
            print()
        
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def test_get_questions(candidate_id=1):
    """测试获取指定候选人的问题"""
    print_section(f"测试2: 获取候选人 {candidate_id} 的面试问题")
    
    try:
        response = requests.get(f"{API_BASE}/api/candidates/{candidate_id}/questions")
        response.raise_for_status()
        
        data = response.json()
        print(f"✓ 成功获取问题")
        print(f"   候选人: {data['candidate_name']}")
        print(f"   是否有问题: {'是' if data['has_questions'] else '否'}")
        
        if data['has_questions']:
            print(f"   问题数量: {len(data['questions'])}")
            print(f"   面试策略: {data['strategy'][:50]}...")
            print(f"\n   前3个问题:")
            for i, q in enumerate(data['questions'][:3], 1):
                print(f"   {i}. [{q['dimension']}] {q['question'][:60]}...")
        else:
            print("   暂无问题")
        
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        return False

def test_generate_questions(candidate_id=1):
    """测试生成面试问题"""
    print_section(f"测试3: 为候选人 {candidate_id} 生成面试问题")
    
    # 先获取候选人信息
    try:
        response = requests.get(f"{API_BASE}/api/candidates")
        response.raise_for_status()
        candidates = response.json()
        
        candidate = next((c for c in candidates if c['id'] == candidate_id), None)
        if not candidate:
            print(f"✗ 未找到候选人 {candidate_id}")
            return False
        
        print(f"候选人: {candidate['name']}")
        print(f"职位: {candidate['position']}")
        print("\n正在生成问题，请稍候...")
        
        # 生成问题
        position_code_map = {
            'Python工程师服务器端开发': '1001',
            'C端产品经理-AIGC领域': '1002',
            '金融海外投资新媒体内容文案编辑运营': '1003'
        }
        
        request_data = {
            "candidate_id": candidate_id,
            "candidate_name": candidate['name'],
            "candidate_email": candidate['email'],
            "position": candidate['position'],
            "position_code": position_code_map.get(candidate['position'], '1001')
        }
        
        response = requests.post(
            f"{API_BASE}/api/candidates/{candidate_id}/generate-questions",
            json=request_data
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✓ 成功生成问题")
        print(f"   生成时间: {data['generated_at']}")
        print(f"   问题数量: {len(data['questions'])}")
        print(f"   面试策略: {data['strategy'][:80]}...")
        
        print(f"\n   生成的问题:")
        for i, q in enumerate(data['questions'], 1):
            print(f"   {i}. [{q['dimension']}] {q['question'][:60]}...")
        
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_regenerate_with_feedback(candidate_id=1):
    """测试根据反馈重新生成问题"""
    print_section(f"测试4: 根据反馈为候选人 {candidate_id} 重新生成问题")
    
    try:
        # 获取候选人信息
        response = requests.get(f"{API_BASE}/api/candidates")
        response.raise_for_status()
        candidates = response.json()
        
        candidate = next((c for c in candidates if c['id'] == candidate_id), None)
        if not candidate:
            print(f"✗ 未找到候选人 {candidate_id}")
            return False
        
        print(f"候选人: {candidate['name']}")
        print(f"职位: {candidate['position']}")
        
        feedback = "问题需要更加深入，增加对实际项目经验的考察，减少理论知识，增加实践案例。"
        print(f"\n管理员反馈: {feedback}")
        print("\n正在根据反馈重新生成问题，请稍候...")
        
        # 根据反馈重新生成
        position_code_map = {
            'Python工程师服务器端开发': '1001',
            'C端产品经理-AIGC领域': '1002',
            '金融海外投资新媒体内容文案编辑运营': '1003'
        }
        
        request_data = {
            "candidate_id": candidate_id,
            "candidate_name": candidate['name'],
            "candidate_email": candidate['email'],
            "position": candidate['position'],
            "position_code": position_code_map.get(candidate['position'], '1001'),
            "feedback": feedback
        }
        
        response = requests.post(
            f"{API_BASE}/api/candidates/{candidate_id}/generate-questions",
            json=request_data
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"\n✓ 成功根据反馈重新生成问题")
        print(f"   生成时间: {data['generated_at']}")
        print(f"   问题数量: {len(data['questions'])}")
        print(f"   面试策略: {data['strategy'][:80]}...")
        
        print(f"\n   重新生成的问题:")
        for i, q in enumerate(data['questions'], 1):
            print(f"   {i}. [{q['dimension']}] {q['question'][:60]}...")
        
        return True
    except Exception as e:
        print(f"✗ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("  面试问题管理功能测试")
    print("="*60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"\n✓ 后端服务运行正常 ({API_BASE})")
    except Exception as e:
        print(f"\n✗ 无法连接到后端服务: {e}")
        print(f"   请确保后端服务已启动: cd backend && python main.py")
        return
    
    # 运行测试
    results = []
    
    # 测试1: 获取候选人列表
    results.append(("获取候选人列表", test_get_candidates()))
    time.sleep(1)
    
    # 测试2: 获取问题
    results.append(("获取面试问题", test_get_questions(1)))
    time.sleep(1)
    
    # 测试3: 生成问题（可选，因为会调用LLM API）
    print("\n" + "="*60)
    choice = input("是否测试生成问题功能？(会调用LLM API，需要5-10秒) [y/N]: ")
    if choice.lower() == 'y':
        results.append(("生成面试问题", test_generate_questions(1)))
        time.sleep(2)
        
        # 测试4: 根据反馈重新生成
        choice = input("\n是否测试根据反馈重新生成？(会调用LLM API) [y/N]: ")
        if choice.lower() == 'y':
            results.append(("根据反馈重新生成", test_regenerate_with_feedback(1)))
    
    # 显示测试结果
    print_section("测试结果汇总")
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}  {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！功能正常工作。")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查日志。")

if __name__ == "__main__":
    main()
