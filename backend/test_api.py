#!/usr/bin/env python3
import sys
import traceback
from excel_data_loader import excel_loader

def test_candidates_api():
    """测试候选人API"""
    try:
        print("=== 测试候选人数据加载 ===")
        candidates = excel_loader.load_candidates()
        print(f"成功加载 {len(candidates)} 个候选人")
        
        for i, candidate in enumerate(candidates[:3]):
            print(f"{i+1}. {candidate['name']} - {candidate['position']} - {candidate['status']}")
        
        print("\n=== 测试统计数据 ===")
        stats = excel_loader.get_dashboard_stats(candidates)
        print(f"统计数据: {stats}")
        
        print("\n=== 测试最佳候选人 ===")
        top_candidates = excel_loader.get_top_candidates(candidates)
        print(f"最佳候选人数量: {len(top_candidates)}")
        
        print("\n=== 测试最新候选人 ===")
        recent_candidates = excel_loader.get_recent_candidates(candidates)
        print(f"最新候选人数量: {len(recent_candidates)}")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_candidates_api()
    sys.exit(0 if success else 1)