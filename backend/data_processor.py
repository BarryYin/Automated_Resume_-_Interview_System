#!/usr/bin/env python3
"""
数据处理脚本 - 读取Excel文件并生成JSON数据
"""

import pandas as pd
import json
import os
from pathlib import Path

def read_excel_files():
    """读取Excel文件并转换为JSON"""
    
    # 文件路径
    job_file = "../resouse/job.xlsx"
    candidate_file = "../resouse/candidate.xlsx"
    
    data = {
        "jobs": [],
        "candidates": [],
        "resumes": {}
    }
    
    try:
        # 读取职位数据
        if os.path.exists(job_file):
            print(f"读取职位文件: {job_file}")
            job_df = pd.read_excel(job_file)
            data["jobs"] = job_df.to_dict('records')
            print(f"读取到 {len(data['jobs'])} 个职位")
        
        # 读取候选人数据
        if os.path.exists(candidate_file):
            print(f"读取候选人文件: {candidate_file}")
            candidate_df = pd.read_excel(candidate_file)
            data["candidates"] = candidate_df.to_dict('records')
            print(f"读取到 {len(data['candidates'])} 个候选人")
        
        # 扫描简历文件
        resume_base_path = "../resouse"
        job_folders = [
            "C端产品经理-AIGC领域",
            "Python工程师服务器端开发", 
            "金融海外投资新媒体内容文案编辑运营"
        ]
        
        for folder in job_folders:
            folder_path = os.path.join(resume_base_path, folder)
            if os.path.exists(folder_path):
                pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
                data["resumes"][folder] = pdf_files
                print(f"职位 '{folder}' 找到 {len(pdf_files)} 份简历")
        
        # 保存为JSON文件
        output_file = "../frontend/data/mock_data.json"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"数据已保存到: {output_file}")
        return data
        
    except Exception as e:
        print(f"处理数据时出错: {e}")
        # 返回模拟数据
        return generate_mock_data()

def generate_mock_data():
    """生成模拟数据"""
    print("生成模拟数据...")
    
    mock_data = {
        "jobs": [
            {
                "id": 1,
                "title": "高级前端工程师",
                "department": "技术部",
                "salary_min": 20000,
                "salary_max": 35000,
                "status": "招聘中",
                "description": "负责前端架构设计和开发，要求熟练掌握React、Vue等框架",
                "requirements": "3年以上前端开发经验，熟悉现代前端技术栈",
                "candidate_count": 12,
                "created_date": "2025-01-15"
            },
            {
                "id": 2,
                "title": "C端产品经理-AIGC领域",
                "department": "产品部",
                "salary_min": 18000,
                "salary_max": 30000,
                "status": "招聘中",
                "description": "负责AIGC产品的规划和设计，推动产品创新",
                "requirements": "3年以上产品经验，了解AI/ML相关技术",
                "candidate_count": 8,
                "created_date": "2025-01-20"
            },
            {
                "id": 3,
                "title": "Python工程师服务器端开发",
                "department": "技术部",
                "salary_min": 15000,
                "salary_max": 25000,
                "status": "招聘中",
                "description": "负责后端服务开发和维护，构建高性能的服务器端应用",
                "requirements": "熟练掌握Python、Django/Flask，有分布式系统经验",
                "candidate_count": 6,
                "created_date": "2025-01-18"
            },
            {
                "id": 4,
                "title": "金融海外投资新媒体内容文案编辑运营",
                "department": "运营部",
                "salary_min": 12000,
                "salary_max": 20000,
                "status": "招聘中",
                "description": "负责金融投资相关内容创作和新媒体运营",
                "requirements": "有金融背景，优秀的文案能力，熟悉新媒体运营",
                "candidate_count": 4,
                "created_date": "2025-01-22"
            }
        ],
        "candidates": [
            {
                "id": 1,
                "name": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138001",
                "position": "高级前端工程师",
                "status": "已完成",
                "score": 85,
                "interview_date": "2025-01-23",
                "resume_file": "张三.pdf"
            },
            {
                "id": 2,
                "name": "李四",
                "email": "lisi@example.com",
                "phone": "13800138002",
                "position": "高级前端工程师",
                "status": "已完成",
                "score": 92,
                "interview_date": "2025-01-24",
                "resume_file": "李四.pdf"
            },
            {
                "id": 3,
                "name": "包涵",
                "email": "baohan@example.com",
                "phone": "13800138003",
                "position": "C端产品经理-AIGC领域",
                "status": "已完成",
                "score": 88,
                "interview_date": "2025-01-24",
                "resume_file": "包涵.pdf"
            },
            {
                "id": 4,
                "name": "乔志天",
                "email": "qiaozhitian@example.com",
                "phone": "13800138004",
                "position": "C端产品经理-AIGC领域",
                "status": "面试中",
                "score": None,
                "interview_date": "2025-01-25",
                "resume_file": "乔志天.pdf"
            },
            {
                "id": 5,
                "name": "栾平",
                "email": "luanping@example.com",
                "phone": "13800138005",
                "position": "Python工程师服务器端开发",
                "status": "已完成",
                "score": 79,
                "interview_date": "2025-01-23",
                "resume_file": "栾平.pdf"
            },
            {
                "id": 6,
                "name": "田忠",
                "email": "tianzhong@example.com",
                "phone": "13800138006",
                "position": "Python工程师服务器端开发",
                "status": "已完成",
                "score": 82,
                "interview_date": "2025-01-24",
                "resume_file": "田忠.pdf"
            },
            {
                "id": 7,
                "name": "高飞虎",
                "email": "gaofeihu@example.com",
                "phone": "13800138007",
                "position": "金融海外投资新媒体内容文案编辑运营",
                "status": "待面试",
                "score": None,
                "interview_date": None,
                "resume_file": "高飞虎.pdf"
            },
            {
                "id": 8,
                "name": "龙小天",
                "email": "longxiaotian@example.com",
                "phone": "13800138008",
                "position": "金融海外投资新媒体内容文案编辑运营",
                "status": "面试中",
                "score": None,
                "interview_date": "2025-01-25",
                "resume_file": "龙小天.pdf"
            }
        ],
        "resumes": {
            "C端产品经理-AIGC领域": ["包涵.pdf", "乔志天.pdf"],
            "Python工程师服务器端开发": ["栾平.pdf", "田忠.pdf"],
            "金融海外投资新媒体内容文案编辑运营": ["高飞虎.pdf", "龙小天.pdf"]
        }
    }
    
    # 保存模拟数据
    output_file = "../frontend/data/mock_data.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    
    print(f"模拟数据已保存到: {output_file}")
    return mock_data

if __name__ == "__main__":
    data = read_excel_files()
    print("数据处理完成！")
    print(f"职位数量: {len(data['jobs'])}")
    print(f"候选人数量: {len(data['candidates'])}")
    print(f"简历文件夹: {list(data['resumes'].keys())}")