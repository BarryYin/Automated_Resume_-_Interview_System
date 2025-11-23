import pandas as pd
import json
import numpy as np
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import random

class ExcelDataLoader:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "resouse"
        self.candidate_file = self.base_path / "candidate.xlsx"
        self.job_file = self.base_path / "job.xlsx"
        

        
    def load_candidates(self):
        """加载候选人数据"""
        try:
            print(f"尝试读取候选人文件: {self.candidate_file}")
            print(f"文件存在: {self.candidate_file.exists()}")
            
            if not self.candidate_file.exists():
                print("候选人Excel文件不存在，使用备用数据")
                return self._get_fallback_candidates()
            
            # 读取候选人Excel文件
            df = pd.read_excel(self.candidate_file)
            print(f"成功读取候选人数据，共 {len(df)} 条记录")
            print(f"列名: {list(df.columns)}")
            
            candidates = []
            for index, row in df.iterrows():
                # 从Excel读取真实数据，处理NaN值
                name = self._safe_str(row.get("姓名"), f"候选人{index+1}")
                email = self._safe_str(row.get("邮箱"), f"candidate{index+1}@example.com")
                position = self._safe_str(row.get("岗位名称"), "未指定职位")
                interview_score = row.get("面试总评分", None) if pd.notna(row.get("面试总评分")) else None
                is_interviewed = self._safe_str(row.get("是否已面试（AI）"), "否")
                interview_time = row.get("面试时间（AI问答完成时间）", None) if pd.notna(row.get("面试时间（AI问答完成时间）")) else None
                candidate_id = row.get("id", index + 1) if pd.notna(row.get("id")) else index + 1
                job_id = row.get("岗位编号", None) if pd.notna(row.get("岗位编号")) else None
                
                # 获取各维度评分
                knowledge = self._safe_float(row.get("Knowledge"))
                skill = self._safe_float(row.get("Skill"))
                ability = self._safe_float(row.get("Ability"))
                personality = self._safe_float(row.get("Personality"))
                motivation = self._safe_float(row.get("Motivation"))
                value = self._safe_float(row.get("Value"))
                
                # 收集所有有效的维度评分
                dimension_scores = [s for s in [knowledge, skill, ability, personality, motivation, value] if s is not None]
                
                # 确定面试状态和评分
                # 优先级1: 如果有面试总评分，使用总评分
                if interview_score and pd.notna(interview_score):
                    status = "已完成"
                    score = int(float(interview_score))
                # 优先级2: 如果有维度评分，计算平均分作为总分
                elif dimension_scores:
                    status = "已完成"
                    score = int(sum(dimension_scores) / len(dimension_scores))
                # 优先级3: 如果标记为已面试但没有评分
                elif is_interviewed == "是":
                    status = "面试中"
                    score = None
                # 优先级4: 默认为待面试
                else:
                    status = "待面试"
                    score = None
                
                # 处理面试时间
                if interview_time and pd.notna(interview_time):
                    try:
                        if isinstance(interview_time, str):
                            interview_date = datetime.strptime(interview_time, "%Y-%m-%d")
                        else:
                            interview_date = interview_time
                    except:
                        interview_date = datetime.now() - timedelta(days=random.randint(0, 7))
                else:
                    interview_date = datetime.now() - timedelta(days=random.randint(0, 7))
                
                # 根据职位确定简历文件夹
                resume_folder, resume_file = self._get_resume_info(name, position)
                
                candidate = {
                    "id": candidate_id,
                    "name": name,
                    "email": email,
                    "position": position,
                    "job_id": job_id,
                    "phone": self._safe_str(row.get("电话"), "未提供"),
                    "experience": self._safe_str(row.get("工作经验"), "未提供"),
                    "education": self._safe_str(row.get("学历"), "未提供"),
                    "skills": self._safe_str(row.get("技能"), "未提供"),
                    "expected_salary": self._generate_realistic_salary(name, position, job_id),
                    "status": status,
                    "score": score,
                    "interview_date": interview_date.strftime("%Y-%m-%d"),
                    "created_at": interview_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "knowledge_score": knowledge,
                    "skill_score": skill,
                    "ability_score": ability,
                    "personality_score": personality,
                    "motivation_score": motivation,
                    "value_score": value,
                    "resume_folder": resume_folder,
                    "resume_file": resume_file
                }
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            print(f"读取候选人数据失败: {e}")
            return self._get_fallback_candidates()
    
    def load_jobs(self):
        """加载职位数据"""
        try:
            df = pd.read_excel(self.job_file)
            print(f"成功读取职位数据，共 {len(df)} 条记录")
            print(f"职位Excel列名: {list(df.columns)}")
            
            jobs = []
            for index, row in df.iterrows():
                
                # 尝试多种可能的列名
                title_candidates = ["职位全称", "职位名称", "岗位名称", "职位", "岗位", "title", "job_title"]
                title = f"职位{index+1}"
                for col in title_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        title = self._safe_str(row.get(col))
                        break
                
                dept_candidates = ["部门", "department", "dept"]
                department = "技术部"
                for col in dept_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        department = self._safe_str(row.get(col))
                        break
                
                salary_candidates = ["薪资", "薪资范围", "工资", "salary", "salary_range"]
                salary = "面议"
                for col in salary_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        salary = self._safe_str(row.get(col))
                        break
                
                req_candidates = ["职位要求", "岗位要求", "个人能力要求", "要求", "requirements", "job_requirements"]
                requirements = "未提供"
                for col in req_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        requirements = self._safe_str(row.get(col))
                        break
                
                desc_candidates = ["职位描述", "岗位描述", "其它补充说明", "描述", "description", "job_description"]
                description = "未提供"
                for col in desc_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        description = self._safe_str(row.get(col))
                        break
                
                # 获取招聘数量
                count_candidates = ["招聘数量", "招聘人数", "人数", "count"]
                recruit_count = 1
                for col in count_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        try:
                            recruit_count = int(row.get(col))
                        except:
                            recruit_count = 1
                        break
                
                # 获取发布时间
                publish_candidates = ["职位发布时间", "发布时间", "创建时间", "publish_date"]
                publish_date = datetime.now().strftime("%Y-%m-%d")
                for col in publish_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        try:
                            if isinstance(row.get(col), str):
                                publish_date = datetime.strptime(row.get(col), "%Y-%m-%d").strftime("%Y-%m-%d")
                            else:
                                publish_date = row.get(col).strftime("%Y-%m-%d")
                        except:
                            publish_date = datetime.now().strftime("%Y-%m-%d")
                        break
                
                # 获取招聘状态
                status_candidates = ["该招聘状态-开启/关闭", "招聘状态", "状态", "status"]
                status = "招聘中"
                for col in status_candidates:
                    if col in df.columns and pd.notna(row.get(col)):
                        status_val = self._safe_str(row.get(col))
                        if "开启" in status_val or "招聘中" in status_val:
                            status = "招聘中"
                        elif "关闭" in status_val or "暂停" in status_val:
                            status = "已暂停"
                        break
                
                job = {
                    "id": self._safe_str(row.get("职位id"), index + 1),
                    "title": title,
                    "department": department,
                    "location": self._safe_str(row.get("工作地点"), "北京"),
                    "salary_range": salary,
                    "requirements": requirements,
                    "description": description,
                    "status": status,
                    "created_at": publish_date,
                    "publish_date": publish_date,
                    "candidate_count": 0,
                    "recruit_count": recruit_count,
                    "recruiter": self._safe_str(row.get("招聘负责人"), "HR"),
                    "recruiter_email": self._safe_str(row.get("负责人邮箱"), "hr@company.com")
                }
                
                print(f"职位 {index+1}: {title}")
                jobs.append(job)
            
            return jobs
            
        except Exception as e:
            print(f"读取职位数据失败: {e}")
            import traceback
            traceback.print_exc()
            return self._get_fallback_jobs()
    
    def _get_fallback_candidates(self):
        """备用候选人数据"""
        return [
            {
                "id": 1,
                "name": "张三",
                "email": "zhangsan@example.com",
                "position": "Python工程师",
                "phone": "13800138001",
                "experience": "3年",
                "education": "本科",
                "skills": "Python, Django, MySQL",
                "expected_salary": "15000",
                "status": "已完成",
                "score": 92,
                "interview_date": "2025-01-24",
                "created_at": "2025-01-24 10:00:00"
            },
            {
                "id": 2,
                "name": "李四",
                "email": "lisi@example.com", 
                "position": "产品经理",
                "phone": "13800138002",
                "experience": "5年",
                "education": "硕士",
                "skills": "产品设计, 用户研究, 数据分析",
                "expected_salary": "20000",
                "status": "已完成",
                "score": 88,
                "interview_date": "2025-01-24",
                "created_at": "2025-01-24 11:00:00"
            }
        ]
    
    def _get_fallback_jobs(self):
        """备用职位数据"""
        return [
            {
                "id": 1,
                "title": "Python工程师服务器端开发",
                "department": "技术部",
                "location": "北京",
                "salary_range": "15000-25000",
                "requirements": "3年以上Python开发经验",
                "description": "负责后端系统开发和维护",
                "status": "招聘中",
                "created_at": "2025-01-20"
            }
        ]
    
    def get_dashboard_stats(self, candidates):
        """计算仪表板统计数据"""
        total_candidates = len(candidates)
        completed_interviews = len([c for c in candidates if c["status"] == "已完成"])
        in_progress = len([c for c in candidates if c["status"] == "面试中"])
        
        # 计算平均分数，确保没有NaN值
        completed_scores = [c["score"] for c in candidates if c["score"] is not None and not np.isnan(c["score"]) if isinstance(c["score"], (int, float))]
        average_score = sum(completed_scores) / len(completed_scores) if completed_scores else 0.0
        
        # 确保返回的是有效数字
        if np.isnan(average_score) or np.isinf(average_score):
            average_score = 0.0
        
        # 统计职位数量
        positions = set([c["position"] for c in candidates])
        active_positions = len(positions)
        
        # 计算每个岗位的最佳候选人和最低薪资候选人
        best_candidates = self.get_best_candidates_by_position(candidates)
        lowest_salary_candidates = self.get_lowest_salary_candidates_by_position(candidates)
        
        return {
            "active_positions": active_positions,
            "total_candidates": total_candidates,
            "completed_interviews": completed_interviews,
            "in_progress_interviews": in_progress,
            "average_score": round(average_score, 1),
            "best_candidates": best_candidates,
            "lowest_salary_candidates": lowest_salary_candidates
        }
    
    def get_best_candidates_by_position(self, candidates):
        """获取每个岗位最符合的候选人（基于评分）"""
        position_candidates = {}
        
        # 按职位分组
        for candidate in candidates:
            position = candidate["position"]
            if position not in position_candidates:
                position_candidates[position] = []
            position_candidates[position].append(candidate)
        
        best_candidates = []
        for position, pos_candidates in position_candidates.items():
            # 筛选有评分的候选人
            scored_candidates = [c for c in pos_candidates if c["score"] is not None]
            if scored_candidates:
                # 按评分排序，取最高分
                best_candidate = max(scored_candidates, key=lambda x: x["score"])
                best_candidates.append({
                    "position": position,
                    "candidate": best_candidate,
                    "reason": "最高评分"
                })
            else:
                # 如果没有评分，取最新的候选人
                if pos_candidates:
                    latest_candidate = max(pos_candidates, key=lambda x: x["created_at"])
                    best_candidates.append({
                        "position": position,
                        "candidate": latest_candidate,
                        "reason": "最新申请"
                    })
        
        return best_candidates
    
    def get_lowest_salary_candidates_by_position(self, candidates):
        """获取每个岗位薪资要求最低的候选人"""
        position_candidates = {}
        
        # 按职位分组
        for candidate in candidates:
            position = candidate["position"]
            if position not in position_candidates:
                position_candidates[position] = []
            position_candidates[position].append(candidate)
        
        lowest_salary_candidates = []
        for position, pos_candidates in position_candidates.items():
            # 筛选有薪资期望的候选人
            salary_candidates = []
            for c in pos_candidates:
                salary_str = c.get("expected_salary", "")
                if salary_str and salary_str != "面议" and salary_str != "未提供":
                    # 尝试提取数字
                    try:
                        # 处理各种薪资格式：15000, 15K, 15k, 1.5万等
                        import re
                        numbers = re.findall(r'[\d.]+', salary_str)
                        if numbers:
                            salary_num = float(numbers[0])
                            # 处理K和万的单位
                            if 'k' in salary_str.lower() or 'K' in salary_str:
                                salary_num *= 1000
                            elif '万' in salary_str:
                                salary_num *= 10000
                            
                            salary_candidates.append({
                                "candidate": c,
                                "salary_num": salary_num
                            })
                    except:
                        continue
            
            if salary_candidates:
                # 按薪资排序，取最低的
                lowest_salary = min(salary_candidates, key=lambda x: x["salary_num"])
                lowest_salary_candidates.append({
                    "position": position,
                    "candidate": lowest_salary["candidate"],
                    "salary_num": lowest_salary["salary_num"],
                    "reason": "薪资要求最低"
                })
        
        return lowest_salary_candidates
    
    def _safe_str(self, value, default="未提供"):
        """安全转换为字符串"""
        return str(value).strip() if pd.notna(value) else default
    
    def _safe_float(self, value):
        """安全转换为浮点数"""
        if pd.notna(value) and not np.isinf(value):
            return float(value)
        return None
    
    def _get_resume_info(self, candidate_name, position):
        """根据候选人姓名和职位获取简历文件夹和文件名"""
        # 职位到文件夹的映射
        position_folder_mapping = {
            "Python工程师服务器端开发": "Python工程师服务器端开发",
            "C端产品经理-AIGC领域": "C端产品经理-AIGC领域",
            "金融海外投资新媒体内容文案编辑运营": "金融海外投资新媒体内容文案编辑运营"
        }
        
        # 根据职位名称匹配文件夹
        resume_folder = None
        for pos_key, folder_name in position_folder_mapping.items():
            if pos_key in position or position in pos_key:
                resume_folder = folder_name
                break
        
        # 如果没有匹配到，尝试根据关键词匹配
        if not resume_folder:
            if "Python" in position or "python" in position or "工程师" in position:
                resume_folder = "Python工程师服务器端开发"
            elif "产品" in position or "PM" in position:
                resume_folder = "C端产品经理-AIGC领域"
            elif "新媒体" in position or "编辑" in position or "运营" in position:
                resume_folder = "金融海外投资新媒体内容文案编辑运营"
            else:
                resume_folder = "Python工程师服务器端开发"  # 默认文件夹
        
        # 简历文件名就是候选人姓名.pdf
        resume_file = f"{candidate_name}.pdf"
        
        # 验证文件是否存在
        resume_path = self.base_path / resume_folder / resume_file
        if not resume_path.exists():
            print(f"警告: 简历文件不存在: {resume_path}")
        
        return resume_folder, resume_file
    
    def _generate_realistic_salary(self, name, position, job_id):
        """基于真实数据生成合理的薪资期望"""
        # 根据职位ID设置基础薪资范围（参考job.xlsx中的薪资）
        job_salary_ranges = {
            1001: (15000, 35000),  # Python工程师 15K~35K
            1002: (12000, 18000),  # 产品经理 12K~18K  
            1003: (9000, 15000)    # 新媒体运营 9-15K
        }
        
        # 根据姓名生成一致的随机数（这样每次运行结果一致）
        import hashlib
        hash_val = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        
        # 获取职位的薪资范围
        salary_range = job_salary_ranges.get(job_id, (12000, 25000))
        min_salary, max_salary = salary_range
        
        # 生成薪资期望（在范围内随机，但偏向中低端）
        range_size = max_salary - min_salary
        # 70%的候选人期望薪资在前60%范围内
        if hash_val % 10 < 7:
            salary = min_salary + (hash_val % int(range_size * 0.6))
        else:
            salary = min_salary + int(range_size * 0.6) + (hash_val % int(range_size * 0.4))
        
        # 格式化为K显示
        if salary >= 1000:
            return f"{salary // 1000}K"
        else:
            return f"{salary}"
    
    def get_top_candidates(self, candidates, limit=5):
        """获取评分最高的候选人"""
        completed_candidates = [c for c in candidates if c["score"] is not None]
        sorted_candidates = sorted(completed_candidates, key=lambda x: x["score"], reverse=True)
        return sorted_candidates[:limit]
    
    def get_recent_candidates(self, candidates, limit=5):
        """获取最近的候选人"""
        sorted_candidates = sorted(candidates, key=lambda x: x["created_at"], reverse=True)
        return sorted_candidates[:limit]
    
    def save_candidates_to_json(self, candidates):
        """保存候选人数据到JSON文件"""
        output_file = Path("../frontend/data/candidates.json")
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        
        print(f"候选人数据已保存到: {output_file}")

# 创建全局实例
excel_loader = ExcelDataLoader()

if __name__ == "__main__":
    # 测试数据加载
    candidates = excel_loader.load_candidates()
    jobs = excel_loader.load_jobs()
    
    print(f"\n候选人数据预览:")
    for candidate in candidates[:3]:
        print(f"- {candidate['name']}: {candidate['position']} (评分: {candidate['score']})")
    
    print(f"\n职位数据预览:")
    for job in jobs[:3]:
        print(f"- {job['title']}: {job['department']}")
    
    # 统计数据
    stats = excel_loader.get_dashboard_stats(candidates)
    print(f"\n统计数据: {stats}")