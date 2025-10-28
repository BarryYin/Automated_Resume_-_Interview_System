#!/usr/bin/env python3
"""
测试简历文件映射
"""

import sys
import os
sys.path.append('backend')

from pathlib import Path

def test_resume_mapping():
    """测试简历文件映射逻辑"""
    
    print("测试简历文件映射...")
    print("=" * 50)
    
    # 真实候选人姓名列表
    candidates = ['田忠', '龙小天', '包涵', '栾平', '高飞虎', '乔志天']
    
    # 简历文件夹映射
    resume_folders = [
        "Python工程师服务器端开发",
        "C端产品经理-AIGC领域", 
        "金融海外投资新媒体内容文案编辑运营"
    ]
    
    print("候选人简历文件映射:")
    
    for candidate_name in candidates:
        found = False
        for folder in resume_folders:
            folder_path = Path("resouse") / folder
            if folder_path.exists():
                for pdf_file in folder_path.glob("*.pdf"):
                    if candidate_name in pdf_file.stem:
                        print(f"✅ {candidate_name} -> {folder}/{pdf_file.name}")
                        found = True
                        break
            if found:
                break
        
        if not found:
            print(f"❌ {candidate_name} -> 未找到对应简历文件")
    
    print("\n" + "=" * 50)
    print("测试不同情况下的问题生成:")
    
    # 测试有简历的候选人
    print("\n1. 有简历的候选人 (田忠):")
    test_candidate_with_resume('田忠')
    
    # 测试没有简历的候选人
    print("\n2. 没有简历的候选人 (张三):")
    test_candidate_without_resume('张三')

def test_candidate_with_resume(candidate_name):
    """测试有简历的候选人"""
    from llm_service import llm_service
    
    # 查找简历文件
    resume_path = find_resume_path(candidate_name)
    
    if resume_path:
        print(f"找到简历: {resume_path}")
        
        # 提取简历内容
        resume_text = llm_service.extract_text_from_pdf(resume_path)
        print(f"简历内容长度: {len(resume_text)} 字符")
        print(f"简历预览: {resume_text[:100]}...")
        
        # 生成个性化问题
        candidate_info = {
            'name': candidate_name,
            'email': f'{candidate_name}@example.com',
            'position': 'Python工程师服务器端开发-AIGC领域'
        }
        
        job_description = "Python工程师服务器端开发，要求熟悉Python、Django等技术"
        
        questions_data = llm_service.generate_interview_questions(
            candidate_info, resume_text, job_description
        )
        
        print(f"生成了 {len(questions_data['questions'])} 个个性化问题")
        print("前3个问题:")
        for i, q in enumerate(questions_data['questions'][:3], 1):
            print(f"  {i}. [{q['dimension']}] {q['question'][:50]}...")
    else:
        print("未找到简历文件")

def test_candidate_without_resume(candidate_name):
    """测试没有简历的候选人"""
    from llm_service import llm_service
    
    print("没有简历文件，使用标准问题生成")
    
    candidate_info = {
        'name': candidate_name,
        'email': f'{candidate_name}@example.com',
        'position': 'Python工程师服务器端开发-AIGC领域'
    }
    
    job_description = "Python工程师服务器端开发，要求熟悉Python、Django等技术"
    
    # 没有简历内容
    questions_data = llm_service.generate_interview_questions(
        candidate_info, "", job_description
    )
    
    print(f"生成了 {len(questions_data['questions'])} 个标准问题")
    print("前3个问题:")
    for i, q in enumerate(questions_data['questions'][:3], 1):
        print(f"  {i}. [{q['dimension']}] {q['question'][:50]}...")

def find_resume_path(candidate_name):
    """根据候选人姓名查找简历文件路径"""
    resume_folders = [
        "Python工程师服务器端开发",
        "C端产品经理-AIGC领域", 
        "金融海外投资新媒体内容文案编辑运营"
    ]
    
    for folder in resume_folders:
        folder_path = Path("resouse") / folder
        if folder_path.exists():
            for pdf_file in folder_path.glob("*.pdf"):
                if candidate_name in pdf_file.stem:
                    return str(pdf_file)
    
    return None

if __name__ == "__main__":
    test_resume_mapping()