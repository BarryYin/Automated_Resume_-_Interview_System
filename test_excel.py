#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

# 测试候选人Excel文件
candidate_file = Path('/Users/mac/Documents/GitHub/test2_1025/resouse/candidate.xlsx')
job_file = Path('/Users/mac/Documents/GitHub/test2_1025/resouse/job.xlsx')

print("=== 测试候选人Excel文件 ===")
print(f"文件路径: {candidate_file}")
print(f"文件存在: {candidate_file.exists()}")

if candidate_file.exists():
    try:
        df = pd.read_excel(candidate_file)
        print(f"成功读取候选人Excel，共 {len(df)} 行")
        print(f"列名: {list(df.columns)}")
        print("\n前3行数据:")
        print(df.head(3))
        
        # 查看所有列的数据
        for col in df.columns:
            print(f"\n列 '{col}' 的值:")
            print(df[col].tolist())
                
    except Exception as e:
        print(f"读取候选人Excel失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("候选人Excel文件不存在！")

print("\n" + "="*50)
print("=== 测试职位Excel文件 ===")
if job_file.exists():
    try:
        df_job = pd.read_excel(job_file)
        print(f"成功读取职位Excel，共 {len(df_job)} 行")
        print(f"列名: {list(df_job.columns)}")
        print("\n职位数据:")
        for i, row in df_job.iterrows():
            print(f"职位{i+1}: {row.get('职位全称', 'N/A')}")
                
    except Exception as e:
        print(f"读取职位Excel失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("职位Excel文件不存在！")