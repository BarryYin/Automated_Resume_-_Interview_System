#!/usr/bin/env python3
import sys
import os
sys.path.append('backend')

# 直接测试Excel加载器
try:
    from excel_data_loader import ExcelDataLoader
    
    loader = ExcelDataLoader()
    print("Excel加载器创建成功")
    
    # 测试加载候选人
    candidates = loader.load_candidates()
    print(f"加载了 {len(candidates)} 个候选人")
    
    for candidate in candidates[:3]:
        print(f"- {candidate['name']}: {candidate['position']} ({candidate['expected_salary']})")
    
    # 测试加载职位
    jobs = loader.load_jobs()
    print(f"\n加载了 {len(jobs)} 个职位")
    
    for job in jobs:
        print(f"- {job['title']}: {job['salary_range']}")
        
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()