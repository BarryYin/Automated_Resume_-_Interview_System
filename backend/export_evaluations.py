#!/usr/bin/env python3
"""
导出候选人评分数据到CSV
"""

import sqlite3
import pandas as pd
from pathlib import Path
import json

def export_evaluations_to_csv():
    """导出评分数据到CSV文件"""
    
    # 连接数据库
    conn = sqlite3.connect('recruitment.db')
    
    try:
        # 查询候选人基本信息和评分数据
        query = '''
        SELECT 
            c.id as candidate_id,
            c.name,
            c.email,
            c.invitation_code as position_code,
            c.created_at as candidate_created_at,
            COALESCE(e.knowledge, 0) as knowledge_score,
            COALESCE(e.skill, 0) as skill_score,
            COALESCE(e.ability, 0) as ability_score,
            COALESCE(e.personality, 0) as personality_score,
            COALESCE(e.motivation, 0) as motivation_score,
            COALESCE(e.value, 0) as value_score,
            COALESCE(e.total_score, 0) as total_score,
            e.strengths,
            e.improvements,
            e.summary,
            e.updated_at as evaluation_updated_at,
            s.status as interview_status,
            s.created_at as interview_date
        FROM candidates c
        LEFT JOIN candidate_evaluations e ON c.id = e.candidate_id
        LEFT JOIN interview_sessions s ON c.id = s.candidate_id
        ORDER BY c.id
        '''
        
        df = pd.read_sql_query(query, conn)
        
        # 添加职位信息
        position_mapping = {
            '1001': 'Python工程师服务器端开发-AIGC领域',
            '1002': 'C端产品经理-AIGC领域',
            '1003': '金融海外投资新媒体内容文案编辑运营'
        }
        
        df['position_name'] = df['position_code'].map(position_mapping).fillna('未知职位')
        
        # 添加计算字段
        df['has_evaluation'] = df['total_score'] > 0
        df['interview_completed'] = df['interview_status'] == '已完成'
        df['score_level'] = pd.cut(df['total_score'], 
                                  bins=[0, 60, 75, 85, 100], 
                                  labels=['待提升', '良好', '优秀', '卓越'])
        
        # 保存到CSV文件
        output_file = '../frontend/data/candidate_evaluations.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"评分数据已导出到: {output_file}")
        print(f"共导出 {len(df)} 条记录")
        
        # 显示数据预览
        print("\n数据预览:")
        print(df[['name', 'position_name', 'total_score', 'interview_status']].head())
        
        # 显示统计信息
        print(f"\n统计信息:")
        print(f"- 有评分的候选人: {df['has_evaluation'].sum()}人")
        print(f"- 已完成面试: {df['interview_completed'].sum()}人")
        print(f"- 平均总分: {df[df['total_score'] > 0]['total_score'].mean():.1f}分")
        
        return output_file
        
    except Exception as e:
        print(f"导出数据时出错: {e}")
        return None
    finally:
        conn.close()

def load_real_candidate_data():
    """从真实数据文件加载候选人信息并插入数据库"""
    
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 读取真实数据
        with open('../frontend/data/real_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 插入候选人数据
        for candidate in data['candidates']:
            cursor.execute('''
                INSERT OR REPLACE INTO candidates (id, name, email, invitation_code, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                candidate['id'],
                candidate['name'],
                candidate['email'],
                str(candidate['position_id']),
                '2025-01-25 10:00:00'
            ))
        
        conn.commit()
        print(f"已插入 {len(data['candidates'])} 个候选人记录")
        
    except Exception as e:
        print(f"加载候选人数据时出错: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("候选人评分数据导出工具")
    print("=" * 40)
    
    # 先加载真实候选人数据
    load_real_candidate_data()
    
    # 导出评分数据
    export_evaluations_to_csv()