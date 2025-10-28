#!/usr/bin/env python3
"""
AI聊天服务 - 数据分析助手
"""

import openai
import json
import sqlite3
from datetime import datetime, timedelta

class AIChatService:
    def __init__(self):
        # 配置通义千问Code API
        self.client = openai.OpenAI(
            api_key="sk-ebf86b67058945fa827863a3742df0b0",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        # 缓存数据
        self.cached_data = None
        self.cache_timestamp = None

    def get_recruitment_data(self):
        """获取招聘数据用于AI分析 - 直接从Excel和真实数据"""
        import pandas as pd
        from pathlib import Path
        import json
        from datetime import datetime, timedelta
        
        # 检查缓存
        now = datetime.now()
        if (self.cached_data and self.cache_timestamp and 
            (now - self.cache_timestamp).seconds < 300):  # 5分钟缓存
            return self.cached_data
        
        try:
            data = {}
            
            # 1. 读取真实候选人JSON数据
            real_data_path = Path("../frontend/data/real_data.json")
            if real_data_path.exists():
                with open(real_data_path, 'r', encoding='utf-8') as f:
                    real_data = json.load(f)
                    data['jobs'] = real_data.get('jobs', [])
                    data['candidates'] = real_data.get('candidates', [])
                    print(f"从JSON加载: {len(data['jobs'])}个职位, {len(data['candidates'])}个候选人")
            else:
                data['jobs'] = []
                data['candidates'] = []
            
            # 2. 直接读取Excel文件
            try:
                # 尝试多个可能的路径
                possible_paths = [
                    "../resouse/job.xlsx",
                    "./resouse/job.xlsx", 
                    "resouse/job.xlsx",
                    "/Users/mac/Documents/GitHub/test2_1025/resouse/job.xlsx"
                ]
                
                job_df = None
                for path in possible_paths:
                    job_excel_path = Path(path)
                    print(f"尝试路径: {job_excel_path.absolute()}")
                    if job_excel_path.exists():
                        print(f"找到职位文件: {path}")
                        job_df = pd.read_excel(job_excel_path)
                        break
                
                if job_df is not None:
                    data['job_excel'] = job_df.to_dict('records')
                    print(f"从Excel加载职位数据: {len(data['job_excel'])}条")
                else:
                    data['job_excel'] = []
                    print("未找到职位Excel文件")
                
                # 读取候选人Excel
                candidate_df = None
                candidate_paths = [
                    "../resouse/candidate.xlsx",
                    "./resouse/candidate.xlsx",
                    "resouse/candidate.xlsx", 
                    "/Users/mac/Documents/GitHub/test2_1025/resouse/candidate.xlsx"
                ]
                
                for path in candidate_paths:
                    candidate_excel_path = Path(path)
                    print(f"尝试路径: {candidate_excel_path.absolute()}")
                    if candidate_excel_path.exists():
                        print(f"找到候选人文件: {path}")
                        candidate_df = pd.read_excel(candidate_excel_path)
                        break
                
                if candidate_df is not None:
                    data['candidate_excel'] = candidate_df.to_dict('records')
                    print(f"从Excel加载候选人数据: {len(data['candidate_excel'])}条")
                else:
                    data['candidate_excel'] = []
                    print("未找到候选人Excel文件")
                    
            except Exception as e:
                print(f"读取Excel文件失败: {e}")
                import traceback
                traceback.print_exc()
                data['job_excel'] = []
                data['candidate_excel'] = []
            
            # 3. 读取CSV评分数据（如果存在）
            csv_path = Path("../frontend/data/candidate_evaluations.csv")
            if csv_path.exists():
                try:
                    df = pd.read_csv(csv_path, encoding='utf-8')
                    data['csv_evaluations'] = df.to_dict('records')
                    print(f"从CSV加载评分数据: {len(data['csv_evaluations'])}条")
                except Exception as e:
                    print(f"读取CSV失败: {e}")
                    data['csv_evaluations'] = []
            else:
                data['csv_evaluations'] = []
            
            # 4. 尝试从数据库获取补充数据（如果表存在）
            data['db_evaluations'] = []
            data['interview_sessions'] = []
            
            try:
                conn = sqlite3.connect('recruitment.db')
                cursor = conn.cursor()
                
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"数据库中的表: {tables}")
                
                if 'candidate_evaluations' in tables:
                    cursor.execute('''
                        SELECT candidate_id, knowledge, skill, ability, personality, 
                               motivation, value, total_score, updated_at
                        FROM candidate_evaluations
                        ORDER BY updated_at DESC
                    ''')
                    
                    evaluations = []
                    for row in cursor.fetchall():
                        evaluations.append({
                            'candidate_id': row[0],
                            'knowledge': row[1],
                            'skill': row[2],
                            'ability': row[3],
                            'personality': row[4],
                            'motivation': row[5],
                            'value': row[6],
                            'total_score': row[7],
                            'updated_at': row[8]
                        })
                    
                    data['db_evaluations'] = evaluations
                    print(f"从数据库加载评分: {len(evaluations)}条")
                
                conn.close()
                
            except Exception as e:
                print(f"数据库查询失败: {e}")
            
            # 5. 计算统计数据
            stats = self.calculate_statistics(data)
            data['statistics'] = stats
            
            # 更新缓存
            self.cached_data = data
            self.cache_timestamp = now
            
            return data
            
        except Exception as e:
            print(f"获取招聘数据失败: {e}")
            import traceback
            traceback.print_exc()
            return self.get_fallback_data()

    def calculate_statistics(self, data):
        """计算统计数据 - 基于真实Excel数据"""
        stats = {}
        
        # 从不同数据源获取数据
        json_candidates = data.get('candidates', [])
        json_jobs = data.get('jobs', [])
        excel_candidates = data.get('candidate_excel', [])
        excel_jobs = data.get('job_excel', [])
        db_evaluations = data.get('db_evaluations', [])
        csv_evaluations = data.get('csv_evaluations', [])
        
        # 使用Excel数据作为主要数据源
        primary_candidates = excel_candidates if excel_candidates else json_candidates
        primary_jobs = excel_jobs if excel_jobs else json_jobs
        
        # 基础统计
        stats['total_candidates'] = len(primary_candidates)
        stats['total_jobs'] = len(primary_jobs)
        stats['excel_candidates'] = len(excel_candidates)
        stats['excel_jobs'] = len(excel_jobs)
        stats['json_candidates'] = len(json_candidates)
        stats['json_jobs'] = len(json_jobs)
        
        # 面试状态统计（从Excel候选人数据）
        interview_status_counts = {}
        completed_count = 0
        
        for candidate in primary_candidates:
            # Excel中的字段可能是中文
            status = candidate.get('是否已面试（AI）', candidate.get('interview_status', '否'))
            interview_status_counts[status] = interview_status_counts.get(status, 0) + 1
            if status in ['是', '已完成', 'completed']:
                completed_count += 1
        
        stats['completed_interviews'] = completed_count
        stats['completion_rate'] = (completed_count / len(primary_candidates) * 100) if primary_candidates else 0
        stats['interview_status_distribution'] = interview_status_counts
        
        # 评分统计
        evaluations = db_evaluations if db_evaluations else csv_evaluations
        
        if evaluations:
            # 平均分数
            scores = [e.get('total_score', e.get('面试总评分', 0)) for e in evaluations if e.get('total_score', e.get('面试总评分', 0))]
            stats['average_score'] = sum(scores) / len(scores) if scores else 0
            stats['max_score'] = max(scores) if scores else 0
            stats['min_score'] = min(scores) if scores else 0
            
            # 各维度平均分
            dimension_mapping = {
                'knowledge': ['knowledge', '评价维度1（可修改）'],
                'skill': ['skill', '评价维度2（可修改）'],
                'ability': ['ability', '评价维度3（可修改）'],
                'personality': ['personality', 'personality_score'],
                'motivation': ['motivation', 'motivation_score'],
                'value': ['value', 'value_score']
            }
            
            for dim, possible_keys in dimension_mapping.items():
                dim_scores = []
                for e in evaluations:
                    for key in possible_keys:
                        if key in e and e[key] is not None:
                            try:
                                score = float(e[key])
                                if score > 0:
                                    dim_scores.append(score)
                                break
                            except (ValueError, TypeError):
                                continue
                
                stats[f'avg_{dim}'] = sum(dim_scores) / len(dim_scores) if dim_scores else 0
        else:
            stats['average_score'] = 0
            stats['max_score'] = 0
            stats['min_score'] = 0
            for dim in ['knowledge', 'skill', 'ability', 'personality', 'motivation', 'value']:
                stats[f'avg_{dim}'] = 0
        
        # 职位分布统计
        position_counts = {}
        
        for candidate in primary_candidates:
            # 尝试不同的职位字段名
            pos = (candidate.get('岗位名称') or 
                   candidate.get('position') or 
                   candidate.get('职位全称') or 
                   '未知职位')
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        stats['position_distribution'] = position_counts
        
        # 职位详细信息
        job_details = []
        for job in primary_jobs:
            job_info = {
                'title': job.get('职位全称', job.get('title', '未知')),
                'salary': job.get('薪资', job.get('salary', '未知')),
                'count': job.get('招聘数量', job.get('recruit_count', 0)),
                'status': job.get('该招聘状态-开启/关闭', job.get('status', '未知'))
            }
            job_details.append(job_info)
        
        stats['job_details'] = job_details
        
        return stats

    def get_fallback_data(self):
        """获取备用数据"""
        return {
            'candidates': [],
            'jobs': [],
            'interview_sessions': [],
            'db_evaluations': [],
            'csv_evaluations': [],
            'statistics': {
                'total_candidates': 0,
                'total_jobs': 0,
                'completed_interviews': 0,
                'average_score': 0,
                'completion_rate': 0
            }
        }

    def chat_with_ai(self, user_message, context=None):
        """与AI进行对话 - 基于真实数据"""
        
        # 获取最新的招聘数据
        recruitment_data = self.get_recruitment_data()
        stats = recruitment_data.get('statistics', {})
        
        # 构建详细的数据上下文
        data_summary = self.format_data_for_ai(recruitment_data)
        
        # 构建系统提示
        system_prompt = f"""
你是一个专业的HR数据分析助手，专门基于真实招聘数据进行分析和回答问题。

重要原则：
1. 只基于提供的真实数据回答问题
2. 如果数据不足，明确说明数据限制
3. 提供具体的数字和事实
4. 不要编造或推测数据
5. 用专业但易懂的语言回答

当前真实数据概况：
{data_summary}

你的能力：
- 分析候选人表现趋势
- 计算招聘效率指标
- 对比不同职位数据
- 识别数据中的模式和洞察
- 提供基于数据的建议

回答要求：
- 引用具体数据支持观点
- 承认数据的局限性
- 提供可操作的建议
- 保持客观和准确
"""

        # 构建用户消息
        user_prompt = f"""
基于以上真实招聘数据，请回答以下问题：

用户问题：{user_message}

请确保：
1. 只使用提供的真实数据
2. 明确指出数据来源
3. 如果数据不足以回答问题，请说明
4. 提供具体的数字和百分比
"""

        try:
            response = self.client.chat.completions.create(
                model="qwen-coder-plus",  # 使用qwen-coder模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # 降低温度以提高准确性
                max_tokens=800
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "data_context": recruitment_data,
                "data_summary": data_summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"AI对话失败: {e}")
            return {
                "response": f"抱歉，AI服务暂时不可用。基于当前数据：总候选人{stats.get('total_candidates', 0)}人，已完成面试{stats.get('completed_interviews', 0)}人，平均分{stats.get('average_score', 0):.1f}分。请稍后再试完整的AI分析。",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def format_data_for_ai(self, data):
        """格式化数据供AI使用 - 基于真实Excel数据"""
        stats = data.get('statistics', {})
        excel_candidates = data.get('candidate_excel', [])
        excel_jobs = data.get('job_excel', [])
        json_candidates = data.get('candidates', [])
        json_jobs = data.get('jobs', [])
        
        # 使用Excel数据作为主要数据源
        primary_candidates = excel_candidates if excel_candidates else json_candidates
        primary_jobs = excel_jobs if excel_jobs else json_jobs
        
        summary = f"""
数据来源：
- Excel候选人数据：{stats.get('excel_candidates', 0)}条
- Excel职位数据：{stats.get('excel_jobs', 0)}条
- JSON候选人数据：{stats.get('json_candidates', 0)}条
- JSON职位数据：{stats.get('json_jobs', 0)}条

基础统计：
- 总候选人数：{stats.get('total_candidates', 0)}人
- 总职位数：{stats.get('total_jobs', 0)}个
- 已完成面试：{stats.get('completed_interviews', 0)}人
- 面试完成率：{stats.get('completion_rate', 0):.1f}%
- 平均总分：{stats.get('average_score', 0):.1f}分
- 最高分：{stats.get('max_score', 0):.1f}分
- 最低分：{stats.get('min_score', 0):.1f}分

各维度平均分：
- 专业知识：{stats.get('avg_knowledge', 0):.1f}分
- 专业技能：{stats.get('avg_skill', 0):.1f}分
- 综合能力：{stats.get('avg_ability', 0):.1f}分
- 个性特质：{stats.get('avg_personality', 0):.1f}分
- 求职动机：{stats.get('avg_motivation', 0):.1f}分
- 价值观：{stats.get('avg_value', 0):.1f}分

面试状态分布：
"""
        
        # 添加面试状态分布
        status_dist = stats.get('interview_status_distribution', {})
        for status, count in status_dist.items():
            summary += f"- {status}：{count}人\n"
        
        summary += "\n职位分布：\n"
        # 添加职位分布
        position_dist = stats.get('position_distribution', {})
        for pos, count in position_dist.items():
            summary += f"- {pos}：{count}人\n"
        
        # 添加职位详细信息
        job_details = stats.get('job_details', [])
        if job_details:
            summary += f"\n职位详情：\n"
            for job in job_details:
                summary += f"- {job.get('title', '未知')}: 薪资{job.get('salary', '未知')}, 招聘{job.get('count', 0)}人, 状态:{job.get('status', '未知')}\n"
        
        # 添加候选人样本
        if primary_candidates:
            summary += f"\n候选人样本（前5名）：\n"
            for i, candidate in enumerate(primary_candidates[:5], 1):
                name = candidate.get('姓名', candidate.get('name', '未知'))
                position = candidate.get('岗位名称', candidate.get('position', '未知职位'))
                email = candidate.get('邮箱', candidate.get('email', '未知邮箱'))
                summary += f"{i}. {name} - {position} ({email})\n"
        
        return summary.strip()

    def generate_analytics_report(self, report_type="comprehensive"):
        """生成基于真实数据的分析报告"""
        
        recruitment_data = self.get_recruitment_data()
        data_summary = self.format_data_for_ai(recruitment_data)
        
        report_prompt = f"""
基于以下真实招聘数据，生成一份专业的{report_type}分析报告：

{data_summary}

报告要求：
1. 只基于提供的真实数据
2. 包含具体的数字和百分比
3. 识别数据中的关键趋势
4. 提供可操作的改进建议
5. 承认数据的局限性

报告结构：
1. 执行摘要
2. 数据概览
3. 关键指标分析
4. 候选人表现分析
5. 招聘效率评估
6. 发现和洞察
7. 改进建议

请确保所有结论都有数据支撑，不要推测或编造信息。
"""

        try:
            response = self.client.chat.completions.create(
                model="qwen-coder-plus",
                messages=[
                    {"role": "system", "content": "你是一个专业的HR数据分析师，专门基于真实数据生成准确的招聘分析报告。"},
                    {"role": "user", "content": report_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return {
                "report": response.choices[0].message.content,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "data_source": recruitment_data,
                "data_summary": data_summary
            }
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            stats = recruitment_data.get('statistics', {})
            fallback_report = f"""
招聘数据分析报告

数据概览：
- 总候选人：{stats.get('total_candidates', 0)}人
- 已完成面试：{stats.get('completed_interviews', 0)}人
- 面试完成率：{stats.get('completion_rate', 0):.1f}%
- 平均得分：{stats.get('average_score', 0):.1f}分

注意：由于AI服务暂时不可用，这是基于基础数据的简化报告。
建议稍后重新生成完整的AI分析报告。
"""
            
            return {
                "report": fallback_report,
                "report_type": report_type,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

# 创建全局AI聊天服务实例
ai_chat_service = AIChatService()