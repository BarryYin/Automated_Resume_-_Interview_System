#!/usr/bin/env python3
import asyncio
from main import get_candidates, get_dashboard_stats

async def test_api_endpoints():
    """直接测试API端点"""
    try:
        print("=== 测试候选人API ===")
        candidates = await get_candidates()
        print(f"候选人数量: {len(candidates)}")
        
        for candidate in candidates[:3]:
            print(f"- {candidate['name']}: {candidate['position']}")
        
        print("\n=== 测试统计API ===")
        stats = await get_dashboard_stats()
        print(f"统计数据: {stats}")
        
    except Exception as e:
        print(f"API测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())