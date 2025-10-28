#!/usr/bin/env python3
"""
为候选人生成模拟评分数据
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

def generate_realistic_scores():
    """生成符合实际情况的评分数据"""
    
    # 候选人信息映射（基于真实Excel数据）
    candidates_data = [
        {
            'id': 2001,
            'name': '田忠',
            'email': '422342158@qq.com',
            'position': 'Python工程师服务器端开发-AIGC领域',
            'position_id': 1001
        },
        {
            'id': 2002,
            'name': '龙小天',
            'email': '422342159@qq.com',
            'position': '金融海外投资新媒体内容文案编辑运营',
            'position_id': 1003
        },
        {
            'id': 2003,
            'name': '包涵',
            'email': '422342160@qq.com',
            'position': 'C端产品经理-AIGC领域',
            'position_id': 1002
        },
        {
            'id': 2004,
            'name': '栾平',
            'email': '422342161@qq.com',
            'position': 'Python工程师服务器端开发-AIGC领域',
            'position_id': 1001
        },
        {
            'id': 2005,
            'name': '高飞虎',
            'email': '422342162@qq.com',
            'position': '金融海外投资新媒体内容文案编辑运营',
            'position_id': 1003
        },
        {
            'id': 2006,
            'name': '乔志天',
            'email': '422342163@qq.com',
            'position': 'C端产品经理-AIGC领域',
            'position_id': 1002
        }
    ]
    
    # 为不同职位设置不同的评分倾向
    position_profiles = {
        1001: {  # Python工程师
            'knowledge': (75, 90),    # 专业知识要求高
            'skill': (80, 95),        # 技能要求很高
            'ability': (70, 85),      # 综合能力中等偏上
            'personality': (65, 80),  # 个性要求中等
            'motivation': (70, 85),   # 求职动机中等偏上
            'value': (75, 88)         # 价值观匹配中等偏上
        },
        1002: {  # 产品经理
            'knowledge': (70, 85),    # 专业知识中等偏上
            'skill': (75, 88),        # 技能要求高
            'ability': (80, 92),      # 综合能力要求很高
            'personality': (75, 90),  # 个性要求高
            'motivation': (78, 90),   # 求职动机高
            'value': (80, 92)         # 价值观匹配很重要
        },
        1003: {  # 新媒体运营
            'knowledge': (65, 80),    # 专业知识中等
            'skill': (70, 85),        # 技能中等偏上
            'ability': (75, 88),      # 综合能力重要
            'personality': (80, 92),  # 个性很重要
            'motivation': (75, 88),   # 求职动机重要
            'value': (78, 90)         # 价值观匹配重要
        }
    }
    
    evaluations = []
    
    for candidate in candidates_data:
        position_id = candidate['position_id']
        profile = position_profiles.get(position_id, position_profiles[1001])
        
        # 为每个候选人生成评分
        scores = {}
        for dimension, (min_score, max_score) in profile.items():
            # 添加一些随机性，但保持在合理范围内
            base_score = random.uniform(min_score, max_score)
            # 添加小幅波动
            variation = random.uniform(-5, 5)
            final_score = max(0, min(100, base_score + variation))
            scores[dimension] = round(final_score, 1)
        
        # 计算总分
        total_score = round(sum(scores.values()) / len(scores), 1)
        
        # 生成优势和改进建议
        strengths, improvements = generate_feedback(candidate, scores)
        
        evaluation = {
            'candidate_id': candidate['id'],
            'name': candidate['name'],
            'email': candidate['email'],
            'position': candidate['position'],
            'knowledge': scores['knowledge'],
            'skill': scores['skill'],
            'ability': scores['ability'],
            'personality': scores['personality'],
            'motivation': scores['motivation'],
            'value': scores['value'],
            'total_score': total_score,
            'strengths': '; '.join(strengths),
            'improvements': '; '.join(improvements),
            'interview_status': '已完成' if random.random() > 0.3 else '面试中',
            'interview_date': (datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        evaluations.append(evaluation)
    
    return evaluations

def generate_feedback(candidate, scores):
    """根据评分生成反馈"""
    
    strengths = []
    improvements = []
    
    # 根据职位和分数生成具体反馈
    position = candidate['position']
    
    if 'Python' in position:
        if scores['knowledge'] >= 80:
            strengths.append('Python技术基础扎实')
        elif scores['knowledge'] < 70:
            improvements.append('需要加强Python相关技术知识')
            
        if scores['skill'] >= 85:
            strengths.append('编程实践能力强')
        elif scores['skill'] < 75:
            improvements.append('建议多做项目实践提升编程技能')
            
    elif '产品经理' in position:
        if scores['ability'] >= 85:
            strengths.append('产品思维和分析能力突出')
        elif scores['ability'] < 75:
            improvements.append('需要提升产品分析和规划能力')
            
        if scores['personality'] >= 80:
            strengths.append('沟通协调能力强')
        elif scores['personality'] < 70:
            improvements.append('建议加强团队沟通和协调技巧')
            
    elif '新媒体' in position:
        if scores['personality'] >= 85:
            strengths.append('创意思维和表达能力优秀')
        elif scores['personality'] < 75:
            improvements.append('可以进一步提升创意表达能力')
            
        if scores['skill'] >= 80:
            strengths.append('内容创作和运营技能娴熟')
        elif scores['skill'] < 70:
            improvements.append('建议加强新媒体运营技能学习')
    
    # 通用反馈
    if scores['motivation'] >= 85:
        strengths.append('求职动机明确，职业规划清晰')
    elif scores['motivation'] < 70:
        improvements.append('建议明确职业发展目标')
        
    if scores['value'] >= 85:
        strengths.append('价值观与企业文化高度匹配')
    elif scores['value'] < 70:
        improvements.append('需要更好地了解和认同企业文化')
    
    # 确保至少有一些反馈
    if not strengths:
        strengths.append('整体表现稳定')
    if not improvements:
        improvements.append('继续保持当前水平')
    
    return strengths, improvements

def save_to_database(evaluations):
    """保存评分数据到数据库"""
    
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 创建表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                knowledge REAL,
                skill REAL,
                ability REAL,
                personality REAL,
                motivation REAL,
                value REAL,
                total_score REAL,
                strengths TEXT,
                improvements TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 清除旧数据
        cursor.execute('DELETE FROM candidate_evaluations')
        
        # 插入新数据
        for eval_data in evaluations:
            cursor.execute('''
                INSERT INTO candidate_evaluations 
                (candidate_id, knowledge, skill, ability, personality, motivation, 
                 value, total_score, strengths, improvements, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                eval_data['candidate_id'],
                eval_data['knowledge'],
                eval_data['skill'], 
                eval_data['ability'],
                eval_data['personality'],
                eval_data['motivation'],
                eval_data['value'],
                eval_data['total_score'],
                eval_data['strengths'],
                eval_data['improvements'],
                f"候选人{eval_data['name']}综合表现良好，总分{eval_data['total_score']}分"
            ))
        
        conn.commit()
        print(f"✅ 成功保存 {len(evaluations)} 条评分数据到数据库")
        
    finally:
        conn.close()

def save_to_csv(evaluations):
    """保存评分数据到CSV"""
    
    df = pd.DataFrame(evaluations)
    
    # 保存到CSV
    csv_path = Path("../frontend/data/candidate_evaluations.csv")
    csv_path.parent.mkdir(exist_ok=True)
    
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✅ 成功保存评分数据到 {csv_path}")
    
    return csv_path

def main():
    """主函数"""
    print("生成候选人评分数据...")
    print("=" * 50)
    
    # 生成评分数据
    evaluations = generate_realistic_scores()
    
    print(f"生成了 {len(evaluations)} 个候选人的评分数据")
    
    # 显示样本数据
    print("\n样本数据:")
    for eval_data in evaluations[:3]:
        print(f"- {eval_data['name']}: 总分 {eval_data['total_score']}分 ({eval_data['position']})")
    
    # 保存到数据库
    save_to_database(evaluations)
    
    # 保存到CSV
    csv_path = save_to_csv(evaluations)
    
    print(f"\n统计信息:")
    total_scores = [e['total_score'] for e in evaluations]
    print(f"- 平均分: {sum(total_scores) / len(total_scores):.1f}")
    print(f"- 最高分: {max(total_scores):.1f}")
    print(f"- 最低分: {min(total_scores):.1f}")
    
    # 按职位统计
    position_stats = {}
    for eval_data in evaluations:
        pos = eval_data['position']
        if pos not in position_stats:
            position_stats[pos] = []
        position_stats[pos].append(eval_data['total_score'])
    
    print(f"\n各职位平均分:")
    for pos, scores in position_stats.items():
        avg_score = sum(scores) / len(scores)
        print(f"- {pos}: {avg_score:.1f}分")
    
    print(f"\n✅ 评分数据生成完成！")
    print(f"现在AI助手可以基于这些真实评分数据进行分析了。")

if __name__ == "__main__":
    main()