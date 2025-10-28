#!/usr/bin/env python3
"""
CSV文件处理模块
用于读取和更新候选人评分数据
"""

import pandas as pd
import os
from pathlib import Path

class CandidateCSVHandler:
    def __init__(self):
        # CSV文件路径
        self.csv_path = Path("../resouse/candidate.xlsx")
        
    def load_candidates(self):
        """加载候选人数据"""
        try:
            if self.csv_path.exists():
                df = pd.read_excel(self.csv_path)
                return df
            else:
                print(f"候选人文件不存在: {self.csv_path}")
                return None
        except Exception as e:
            print(f"读取候选人文件失败: {e}")
            return None
    
    def update_candidate_score(self, candidate_name, dimension, score):
        """更新候选人某个维度的评分"""
        try:
            df = self.load_candidates()
            if df is None:
                return False
            
            # 查找候选人
            candidate_row = df[df['姓名'] == candidate_name]
            if candidate_row.empty:
                print(f"未找到候选人: {candidate_name}")
                return False
            
            # 更新评分
            df.loc[df['姓名'] == candidate_name, dimension] = score
            
            # 保存文件
            df.to_excel(self.csv_path, index=False)
            print(f"成功更新候选人 {candidate_name} 的 {dimension} 评分: {score}")
            return True
            
        except Exception as e:
            print(f"更新候选人评分失败: {e}")
            return False
    
    def get_candidate_scores(self, candidate_name):
        """获取候选人的所有评分"""
        try:
            df = self.load_candidates()
            if df is None:
                return None
            
            candidate_row = df[df['姓名'] == candidate_name]
            if candidate_row.empty:
                return None
            
            # 返回评分数据
            score_columns = ['Knowledge', 'Skill', 'Ability', 'Personality', 'Motivation', 'Value']
            scores = {}
            
            for col in score_columns:
                if col in df.columns:
                    scores[col] = candidate_row[col].iloc[0]
            
            return scores
            
        except Exception as e:
            print(f"获取候选人评分失败: {e}")
            return None
    
    def calculate_total_score(self, candidate_name):
        """计算候选人总分"""
        scores = self.get_candidate_scores(candidate_name)
        if not scores:
            return 0
        
        # 计算有效评分的平均值
        valid_scores = [score for score in scores.values() if pd.notna(score) and score > 0]
        if valid_scores:
            return round(sum(valid_scores) / len(valid_scores), 1)
        return 0

# 创建全局实例
csv_handler = CandidateCSVHandler()