#!/usr/bin/env python3
"""
预生成面试问题脚本
为所有候选人提前生成个性化面试问题并保存到数据库
"""

import sqlite3
import json
import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service import llm_service

def init_questions_table():
    """初始化面试问题表"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 创建面试问题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT,
                candidate_email TEXT,
                position_code TEXT,
                questions_json TEXT,
                strategy TEXT,
                resume_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_candidate_email 
            ON interview_questions(candidate_email)
        ''')
        
        conn.commit()
        print("面试问题表初始化完成")
        
    finally:
        conn.close()

def get_candidate_resume_mapping():
    """获取候选人和简历文件的映射关系"""
    resume_mapping = {
        # Python工程师服务器端开发
        "栾平": {
            "position": "Python工程师服务器端开发",
            "position_code": "1001",
            "resume_path": "resouse/Python工程师服务器端开发/栾平.pdf"
        },
        "田忠": {
            "position": "Python工程师服务器端开发", 
            "position_code": "1001",
            "resume_path": "resouse/Python工程师服务器端开发/田忠.pdf"
        },
        
        # C端产品经理-AIGC领域
        "包涵": {
            "position": "C端产品经理-AIGC领域",
            "position_code": "1002", 
            "resume_path": "resouse/C端产品经理-AIGC领域/包涵.pdf"
        },
        "乔志天": {
            "position": "C端产品经理-AIGC领域",
            "position_code": "1002",
            "resume_path": "resouse/C端产品经理-AIGC领域/乔志天.pdf"
        },
        
        # 金融海外投资新媒体内容文案编辑运营
        "高飞虎": {
            "position": "金融海外投资新媒体内容文案编辑运营",
            "position_code": "1003",
            "resume_path": "resouse/金融海外投资新媒体内容文案编辑运营/高飞虎.pdf"
        },
        "龙小天": {
            "position": "金融海外投资新媒体内容文案编辑运营",
            "position_code": "1003", 
            "resume_path": "resouse/金融海外投资新媒体内容文案编辑运营/龙小天.pdf"
        }
    }
    
    return resume_mapping

def get_job_description(position_code):
    """获取职位描述"""
    job_descriptions = {
        "1001": """
Python工程师服务器端开发-AIGC领域
职位要求：设计、开发、测试和维护Python应用程序，与团队成员合作，确保代码质量、可靠性和可维护性，在AIGC相关领域进行研究和开发。
能力要求：至少2年Python开发经验，熟练掌握Python编程语言及相关的开发框架和库，熟练掌握Web开发技术，熟练使用常用的数据库。
        """,
        "1002": """
C端产品经理-AIGC领域
职位要求：研究行业竞品和市场动态，挖掘客户需求，撰写MRD、PRD等产品设计文档，设计并优化产品功能和用户体验。
能力要求：1-3年产品设计经验，熟悉Axure、Visio等原型工具，对社交需求和场景有深入理解，熟悉AIGC行业。
        """,
        "1003": """
金融海外投资新媒体内容文案编辑运营
职位要求：负责金融&投资类自媒体账号的策略、目标、和落地执行，负责相关内容的采写、剪辑、发布、用户互动等。
能力要求：3年以上新媒体文案编辑的经验，有很强的文字功底，熟悉内容采编，对财经类、投资类以及海外热点事件敏感。
        """
    }
    
    return job_descriptions.get(position_code, "职位描述暂无")

def generate_questions_for_candidate(candidate_name, candidate_info):
    """为单个候选人生成面试问题"""
    print(f"\n正在为候选人 {candidate_name} 生成面试问题...")
    
    # 读取简历内容
    resume_text = ""
    
    # 尝试多个可能的路径
    possible_paths = [
        Path("..") / candidate_info["resume_path"],  # ../resouse/...
        Path(candidate_info["resume_path"]),         # resouse/...
        Path(".") / ".." / candidate_info["resume_path"],  # ./resouse/...
    ]
    
    resume_path = None
    for path in possible_paths:
        if path.exists():
            resume_path = path
            break
    
    if resume_path:
        try:
            resume_text = llm_service.extract_text_from_pdf(str(resume_path))
            print(f"成功读取简历文件: {resume_path}")
        except Exception as e:
            print(f"读取简历失败: {e}")
    else:
        print(f"简历文件不存在，尝试的路径:")
        for path in possible_paths:
            print(f"  - {path.resolve()}")
    
    # 获取职位描述
    job_description = get_job_description(candidate_info["position_code"])
    
    # 构建候选人信息
    candidate_data = {
        'name': candidate_name,
        'email': f"{candidate_name.lower()}@example.com",  # 临时邮箱
        'position': candidate_info["position"]
    }
    
    # 生成面试问题
    try:
        questions_data = llm_service.generate_interview_questions(
            candidate_data, resume_text, job_description
        )
        
        print(f"成功生成 {len(questions_data['questions'])} 个问题")
        return questions_data
        
    except Exception as e:
        print(f"生成问题失败: {e}")
        return None

def save_questions_to_db(candidate_name, candidate_info, questions_data):
    """保存问题到数据库"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 检查是否已存在
        cursor.execute('''
            SELECT id FROM interview_questions 
            WHERE candidate_name = ? AND position_code = ?
        ''', (candidate_name, candidate_info["position_code"]))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute('''
                UPDATE interview_questions 
                SET questions_json = ?, strategy = ?, resume_path = ?, updated_at = CURRENT_TIMESTAMP
                WHERE candidate_name = ? AND position_code = ?
            ''', (
                json.dumps(questions_data["questions"], ensure_ascii=False),
                questions_data.get("interview_strategy", ""),
                candidate_info["resume_path"],
                candidate_name,
                candidate_info["position_code"]
            ))
            print(f"更新了候选人 {candidate_name} 的面试问题")
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO interview_questions 
                (candidate_name, candidate_email, position_code, questions_json, strategy, resume_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                candidate_name,
                f"{candidate_name.lower()}@example.com",
                candidate_info["position_code"],
                json.dumps(questions_data["questions"], ensure_ascii=False),
                questions_data.get("interview_strategy", ""),
                candidate_info["resume_path"]
            ))
            print(f"保存了候选人 {candidate_name} 的面试问题")
        
        conn.commit()
        
    finally:
        conn.close()

def main():
    """主函数"""
    print("开始预生成面试问题...")
    
    # 初始化数据库表
    init_questions_table()
    
    # 获取候选人映射
    resume_mapping = get_candidate_resume_mapping()
    
    # 为每个候选人生成问题
    success_count = 0
    total_count = len(resume_mapping)
    
    for candidate_name, candidate_info in resume_mapping.items():
        try:
            questions_data = generate_questions_for_candidate(candidate_name, candidate_info)
            
            if questions_data:
                save_questions_to_db(candidate_name, candidate_info, questions_data)
                success_count += 1
            else:
                print(f"候选人 {candidate_name} 的问题生成失败")
                
        except Exception as e:
            print(f"处理候选人 {candidate_name} 时出错: {e}")
    
    print(f"\n预生成完成！成功: {success_count}/{total_count}")

if __name__ == "__main__":
    main()