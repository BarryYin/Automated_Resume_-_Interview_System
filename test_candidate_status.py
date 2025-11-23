#!/usr/bin/env python3
"""
测试候选人状态判断逻辑
"""

import sys
sys.path.append('backend')

from excel_data_loader import excel_loader

def test_candidate_status():
    print("="*60)
    print("  测试候选人状态判断")
    print("="*60)
    print()
    
    # 加载候选人数据
    candidates = excel_loader.load_candidates()
    
    print(f"总共加载 {len(candidates)} 个候选人\n")
    
    # 显示所有候选人的状态和评分
    print("候选人状态和评分:")
    print("-" * 80)
    print(f"{'姓名':<10} {'职位':<25} {'状态':<10} {'总分':<8} {'维度评分'}")
    print("-" * 80)
    
    for candidate in candidates:
        name = candidate['name']
        position = candidate['position'][:23] + '..' if len(candidate['position']) > 25 else candidate['position']
        status = candidate['status']
        score = candidate['score'] if candidate['score'] else '-'
        
        # 收集维度评分
        dimensions = []
        for dim in ['knowledge_score', 'skill_score', 'ability_score', 'personality_score', 'motivation_score', 'value_score']:
            val = candidate.get(dim)
            if val is not None:
                dimensions.append(f"{dim.split('_')[0][:3].upper()}:{val:.0f}")
        
        dim_str = ', '.join(dimensions) if dimensions else '-'
        
        print(f"{name:<10} {position:<25} {status:<10} {str(score):<8} {dim_str}")
    
    print("-" * 80)
    print()
    
    # 统计各状态的数量
    status_count = {}
    for candidate in candidates:
        status = candidate['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("状态统计:")
    for status, count in status_count.items():
        print(f"  {status}: {count} 人")
    
    print()
    
    # 检查栾平的状态
    luanping = next((c for c in candidates if c['name'] == '栾平'), None)
    if luanping:
        print("="*60)
        print("  栾平的详细信息")
        print("="*60)
        print(f"姓名: {luanping['name']}")
        print(f"职位: {luanping['position']}")
        print(f"状态: {luanping['status']}")
        print(f"总分: {luanping['score']}")
        print(f"维度评分:")
        for dim in ['knowledge_score', 'skill_score', 'ability_score', 'personality_score', 'motivation_score', 'value_score']:
            val = luanping.get(dim)
            if val is not None:
                print(f"  {dim}: {val}")
        
        # 验证状态是否正确
        has_scores = any(luanping.get(dim) is not None for dim in ['knowledge_score', 'skill_score', 'ability_score', 'personality_score', 'motivation_score', 'value_score'])
        
        print()
        if has_scores and luanping['status'] == '已完成':
            print("✓ 状态判断正确：有维度评分，状态为'已完成'")
        elif has_scores and luanping['status'] != '已完成':
            print("✗ 状态判断错误：有维度评分，但状态不是'已完成'")
        elif not has_scores and luanping['status'] == '待面试':
            print("✓ 状态判断正确：无评分，状态为'待面试'")
        else:
            print(f"? 状态: {luanping['status']}, 有评分: {has_scores}")
    else:
        print("未找到栾平的数据")

if __name__ == "__main__":
    test_candidate_status()
