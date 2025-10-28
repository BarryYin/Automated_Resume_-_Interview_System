from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
from datetime import datetime
from llm_service import llm_service
from ai_chat_service import ai_chat_service
from email_service import email_service
from excel_data_loader import excel_loader

app = FastAPI(title="AI招聘系统API")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class Candidate(BaseModel):
    name: str
    email: str
    invitation_code: Optional[str] = None

class InterviewSession(BaseModel):
    candidate_id: int
    session_id: str
    status: str = "进行中"
    score: Optional[float] = None
    
class InterviewQuestion(BaseModel):
    question: str
    answer: Optional[str] = None

# 初始化数据库
def init_db():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    # 候选人表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            invitation_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 面试会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            session_id TEXT UNIQUE,
            status TEXT DEFAULT '进行中',
            score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    ''')
    
    # 面试问答表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interview_qa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            question TEXT,
            answer TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES interview_sessions (session_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# API路由
@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "AI招聘系统API"}

@app.post("/api/candidates")
async def create_candidate(candidate: Candidate):
    """创建候选人"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO candidates (name, email, invitation_code) VALUES (?, ?, ?)",
            (candidate.name, candidate.email, candidate.invitation_code)
        )
        conn.commit()
        candidate_id = cursor.lastrowid
        return {"id": candidate_id, "message": "候选人创建成功"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    finally:
        conn.close()

@app.get("/api/candidates")
async def get_candidates():
    """获取候选人列表 - 使用真实Excel数据"""
    try:
        # 从Excel加载真实候选人数据
        candidates = excel_loader.load_candidates()
        
        # 确保数据可以JSON序列化
        import json
        import numpy as np
        
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            else:
                return str(obj)
        
        cleaned_candidates = clean_for_json(candidates)
        return cleaned_candidates
    except Exception as e:
        print(f"加载候选人数据失败: {e}")
        import traceback
        traceback.print_exc()
        # 返回空列表或错误信息
        raise HTTPException(status_code=500, detail=f"加载候选人数据失败: {str(e)}")

@app.post("/api/interview/start")
async def start_interview(candidate: Candidate):
    """开始面试"""
    import uuid
    
    # 先创建候选人
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO candidates (name, email, invitation_code) VALUES (?, ?, ?)",
            (candidate.name, candidate.email, candidate.invitation_code)
        )
        
        cursor.execute("SELECT id FROM candidates WHERE email = ?", (candidate.email,))
        candidate_id = cursor.fetchone()[0]
        
        # 创建面试会话
        session_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO interview_sessions (candidate_id, session_id) VALUES (?, ?)",
            (candidate_id, session_id)
        )
        
        conn.commit()
        return {"session_id": session_id, "message": "面试开始"}
    finally:
        conn.close()

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """获取仪表板统计数据 - 使用真实Excel数据"""
    try:
        # 从Excel加载真实数据
        candidates = excel_loader.load_candidates()
        stats = excel_loader.get_dashboard_stats(candidates)
        
        # 确保所有数值都是JSON可序列化的
        import numpy as np
        for key, value in stats.items():
            if isinstance(value, (np.integer, np.floating)):
                stats[key] = value.item()
            elif isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                stats[key] = 0.0
        
        return stats
    except Exception as e:
        print(f"加载统计数据失败: {e}")
        import traceback
        traceback.print_exc()
        # 返回默认统计数据
        return {
            "active_positions": 3,
            "total_candidates": 0,
            "completed_interviews": 0,
            "average_score": 0.0
        }

@app.get("/api/resume/{folder}/{filename}")
async def get_resume(folder: str, filename: str):
    """获取简历文件"""
    from fastapi.responses import Response
    import os
    from urllib.parse import unquote
    from pathlib import Path
    
    try:
        # URL解码
        folder = unquote(folder)
        filename = unquote(filename)
        
        print(f"请求文件: folder={folder}, filename={filename}")
        
        # 获取当前脚本的目录
        current_dir = Path(__file__).parent
        print(f"当前目录: {current_dir}")
        
        # 构建文件路径 - 尝试多个可能的路径
        possible_paths = [
            current_dir.parent / "resouse" / folder / filename,  # ../resouse/
            current_dir / ".." / "resouse" / folder / filename,  # ../resouse/
            Path("resouse") / folder / filename,  # ./resouse/
            Path(".") / "resouse" / folder / filename,  # ./resouse/
        ]
        
        file_path = None
        for path in possible_paths:
            abs_path = path.resolve()
            print(f"检查路径: {abs_path}")
            if abs_path.exists():
                file_path = abs_path
                break
        
        if not file_path:
            print(f"所有路径都不存在:")
            for path in possible_paths:
                print(f"  - {path.resolve()}")
            raise HTTPException(status_code=404, detail=f"简历文件未找到: {filename}")
        
        print(f"找到文件: {file_path}")
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 返回文件内容
        return Response(
            content=file_content,
            media_type='application/pdf',
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=3600",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        print(f"获取简历文件时出错: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

# 候选人评分数据模型
class CandidateEvaluation(BaseModel):
    candidate_id: int
    knowledge: Optional[int] = None
    skill: Optional[int] = None
    ability: Optional[int] = None
    personality: Optional[int] = None
    motivation: Optional[int] = None
    value: Optional[int] = None
    total_score: Optional[float] = None
    strengths: Optional[str] = None
    improvements: Optional[str] = None
    summary: Optional[str] = None

@app.post("/api/candidates/{candidate_id}/evaluation")
async def save_candidate_evaluation(candidate_id: int, evaluation: CandidateEvaluation):
    """保存候选人评分"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 创建评分表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                knowledge INTEGER,
                skill INTEGER,
                ability INTEGER,
                personality INTEGER,
                motivation INTEGER,
                value INTEGER,
                total_score REAL,
                strengths TEXT,
                improvements TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        ''')
        
        # 检查是否已存在评分记录
        cursor.execute("SELECT id FROM candidate_evaluations WHERE candidate_id = ?", (candidate_id,))
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute('''
                UPDATE candidate_evaluations 
                SET knowledge = ?, skill = ?, ability = ?, personality = ?, 
                    motivation = ?, value = ?, total_score = ?, strengths = ?, 
                    improvements = ?, summary = ?, updated_at = CURRENT_TIMESTAMP
                WHERE candidate_id = ?
            ''', (
                evaluation.knowledge, evaluation.skill, evaluation.ability,
                evaluation.personality, evaluation.motivation, evaluation.value,
                evaluation.total_score, evaluation.strengths, evaluation.improvements,
                evaluation.summary, candidate_id
            ))
        else:
            # 插入新记录
            cursor.execute('''
                INSERT INTO candidate_evaluations 
                (candidate_id, knowledge, skill, ability, personality, motivation, 
                 value, total_score, strengths, improvements, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate_id, evaluation.knowledge, evaluation.skill, evaluation.ability,
                evaluation.personality, evaluation.motivation, evaluation.value,
                evaluation.total_score, evaluation.strengths, evaluation.improvements,
                evaluation.summary
            ))
        
        conn.commit()
        return {"message": "评分保存成功", "candidate_id": candidate_id}
        
    except Exception as e:
        print(f"保存评分时出错: {e}")
        raise HTTPException(status_code=500, detail=f"保存评分失败: {str(e)}")
    finally:
        conn.close()

@app.get("/api/candidates/{candidate_id}/evaluation")
async def get_candidate_evaluation(candidate_id: int):
    """获取候选人评分"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT knowledge, skill, ability, personality, motivation, value, 
                   total_score, strengths, improvements, summary, updated_at
            FROM candidate_evaluations 
            WHERE candidate_id = ?
        ''', (candidate_id,))
        
        result = cursor.fetchone()
        
        if result:
            return {
                "candidate_id": candidate_id,
                "knowledge": result[0],
                "skill": result[1],
                "ability": result[2],
                "personality": result[3],
                "motivation": result[4],
                "value": result[5],
                "total_score": result[6],
                "strengths": result[7],
                "improvements": result[8],
                "summary": result[9],
                "updated_at": result[10]
            }
        else:
            raise HTTPException(status_code=404, detail="评分记录未找到")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取评分时出错: {e}")
        raise HTTPException(status_code=500, detail=f"获取评分失败: {str(e)}")
    finally:
        conn.close()

@app.post("/api/interview/generate-questions")
async def generate_interview_questions(candidate: Candidate):
    """为候选人生成AI面试问题"""
    try:
        print(f"为候选人 {candidate.name} 生成面试问题")
        
        # 根据候选人姓名生成针对性问题
        questions_data = generate_questions_by_name(candidate.name, candidate.invitation_code)
        
        # 保存问题到数据库
        session_id = save_interview_questions(candidate, questions_data)
        
        return {
            "session_id": session_id,
            "questions": questions_data["questions"],
            "strategy": questions_data.get("interview_strategy", ""),
            "message": "面试问题生成成功"
        }
        
    except Exception as e:
        print(f"生成面试问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成面试问题失败: {str(e)}")

def generate_questions_by_name(candidate_name, position_code):
    """根据候选人姓名生成针对性问题"""
    
    # 高飞虎的专门问题（金融海外投资新媒体内容文案编辑运营）
    if candidate_name == "高飞虎":
        return {
            "questions": [
                {
                    "id": 1,
                    "dimension": "Knowledge",
                    "question": "请介绍一下您在金融投资领域的专业知识背景，特别是海外投资方面的了解。",
                    "follow_up": "能具体谈谈您对哪些海外市场比较熟悉吗？"
                },
                {
                    "id": 2,
                    "dimension": "Skill",
                    "question": "请描述一下您在新媒体内容创作方面的经验，包括使用过哪些平台和工具。",
                    "follow_up": "您通常如何保证内容的质量和时效性？"
                },
                {
                    "id": 3,
                    "dimension": "Ability",
                    "question": "在财经类内容创作中，您如何平衡专业性和可读性？",
                    "follow_up": "能举个具体的例子说明您是如何处理复杂金融概念的？"
                },
                {
                    "id": 4,
                    "dimension": "Knowledge",
                    "question": "您对当前的海外投资热点和趋势有什么看法？",
                    "follow_up": "您认为哪些因素会影响海外投资的决策？"
                },
                {
                    "id": 5,
                    "dimension": "Skill",
                    "question": "请谈谈您在内容采编方面的工作流程和方法。",
                    "follow_up": "您如何确保信息来源的可靠性？"
                },
                {
                    "id": 6,
                    "dimension": "Personality",
                    "question": "在快节奏的新媒体工作环境中，您如何保持工作效率和内容质量？",
                    "follow_up": "遇到突发热点事件时，您是如何快速响应的？"
                },
                {
                    "id": 7,
                    "dimension": "Motivation",
                    "question": "是什么吸引您选择金融新媒体这个领域？您的职业规划是什么？",
                    "follow_up": "您希望在这个职位上获得什么样的成长？"
                },
                {
                    "id": 8,
                    "dimension": "Ability",
                    "question": "请描述一次您成功策划和执行的内容营销案例。",
                    "follow_up": "这个案例的效果如何？您从中学到了什么？"
                },
                {
                    "id": 9,
                    "dimension": "Value",
                    "question": "您认为金融媒体从业者应该具备哪些职业操守？",
                    "follow_up": "在内容创作中如何平衡商业利益和客观性？"
                },
                {
                    "id": 10,
                    "dimension": "Motivation",
                    "question": "您对我们公司的业务和发展方向有什么了解？为什么想加入我们？",
                    "follow_up": "您认为自己能为公司带来什么价值？"
                }
            ],
            "interview_strategy": "重点考察候选人在金融投资知识、新媒体运营技能、内容创作能力以及对行业的理解程度。"
        }
    
    # 其他候选人的通用问题
    position_questions = {
        "1001": generate_python_engineer_questions(),  # Python工程师
        "1002": generate_product_manager_questions(),  # 产品经理
        "1003": generate_media_editor_questions()      # 新媒体编辑
    }
    
    return position_questions.get(position_code, generate_default_questions())

def generate_python_engineer_questions():
    """Python工程师问题"""
    return {
        "questions": [
            {
                "id": 1,
                "dimension": "Knowledge",
                "question": "请介绍一下您的Python开发经验和技术栈。",
                "follow_up": "您最熟悉哪些Python框架？"
            },
            {
                "id": 2,
                "dimension": "Skill",
                "question": "请描述一个您最近完成的Python项目。",
                "follow_up": "在这个项目中遇到了什么技术挑战？"
            },
            {
                "id": 3,
                "dimension": "Knowledge",
                "question": "您对AIGC领域有什么了解？",
                "follow_up": "您认为Python在AI开发中的优势是什么？"
            },
            {
                "id": 4,
                "dimension": "Skill",
                "question": "请谈谈您在数据库设计和优化方面的经验。",
                "follow_up": "您通常如何处理数据库性能问题？"
            },
            {
                "id": 5,
                "dimension": "Ability",
                "question": "在团队开发中，您如何保证代码质量？",
                "follow_up": "您使用过哪些代码审查工具？"
            },
            {
                "id": 6,
                "dimension": "Personality",
                "question": "您如何保持技术知识的更新？",
                "follow_up": "您通常关注哪些技术社区或资源？"
            },
            {
                "id": 7,
                "dimension": "Ability",
                "question": "请描述一次您解决复杂技术问题的经历。",
                "follow_up": "您的解决思路是什么？"
            },
            {
                "id": 8,
                "dimension": "Motivation",
                "question": "为什么选择Python开发这个方向？",
                "follow_up": "您的技术发展规划是什么？"
            },
            {
                "id": 9,
                "dimension": "Value",
                "question": "您认为优秀的后端工程师应该具备哪些素质？",
                "follow_up": "您如何看待技术债务的问题？"
            },
            {
                "id": 10,
                "dimension": "Motivation",
                "question": "您希望在新的工作环境中获得什么？",
                "follow_up": "您能为团队带来什么价值？"
            }
        ],
        "interview_strategy": "重点考察Python技术能力、AIGC领域理解、系统设计思维和团队协作能力。"
    }

def generate_product_manager_questions():
    """产品经理问题"""
    return {
        "questions": [
            {
                "id": 1,
                "dimension": "Knowledge",
                "question": "请介绍一下您的产品管理经验和背景。",
                "follow_up": "您主要负责过哪类产品？"
            },
            {
                "id": 2,
                "dimension": "Skill",
                "question": "请描述一个您主导的产品项目从0到1的过程。",
                "follow_up": "在这个过程中您是如何做需求分析的？"
            },
            {
                "id": 3,
                "dimension": "Knowledge",
                "question": "您对AIGC领域的产品有什么理解？",
                "follow_up": "您认为AIGC产品的核心竞争力是什么？"
            },
            {
                "id": 4,
                "dimension": "Ability",
                "question": "您如何平衡用户需求和技术可行性？",
                "follow_up": "遇到需求冲突时您是如何处理的？"
            },
            {
                "id": 5,
                "dimension": "Skill",
                "question": "请谈谈您在用户研究和数据分析方面的经验。",
                "follow_up": "您通常使用哪些工具和方法？"
            },
            {
                "id": 6,
                "dimension": "Personality",
                "question": "在跨部门协作中，您如何推动项目进展？",
                "follow_up": "遇到阻力时您是如何解决的？"
            },
            {
                "id": 7,
                "dimension": "Ability",
                "question": "请描述一次产品迭代优化的经历。",
                "follow_up": "您是如何衡量优化效果的？"
            },
            {
                "id": 8,
                "dimension": "Motivation",
                "question": "为什么选择产品经理这个职业？",
                "follow_up": "您的职业发展目标是什么？"
            },
            {
                "id": 9,
                "dimension": "Value",
                "question": "您认为好的产品应该具备哪些特质？",
                "follow_up": "您如何看待产品的商业价值和用户价值？"
            },
            {
                "id": 10,
                "dimension": "Motivation",
                "question": "您对我们的产品方向有什么想法？",
                "follow_up": "您希望在这个岗位上实现什么？"
            }
        ],
        "interview_strategy": "重点考察产品思维、用户洞察、项目管理能力和AIGC领域的理解。"
    }

def generate_media_editor_questions():
    """新媒体编辑问题"""
    return {
        "questions": [
            {
                "id": 1,
                "dimension": "Knowledge",
                "question": "请介绍一下您在新媒体内容创作方面的经验。",
                "follow_up": "您主要创作过哪些类型的内容？"
            },
            {
                "id": 2,
                "dimension": "Skill",
                "question": "请描述一个您认为成功的内容营销案例。",
                "follow_up": "这个案例的传播效果如何？"
            },
            {
                "id": 3,
                "dimension": "Knowledge",
                "question": "您对金融投资领域有多少了解？",
                "follow_up": "您通常从哪些渠道获取财经资讯？"
            },
            {
                "id": 4,
                "dimension": "Skill",
                "question": "在内容创作中，您如何保证信息的准确性？",
                "follow_up": "您有哪些信息验证的方法？"
            },
            {
                "id": 5,
                "dimension": "Ability",
                "question": "您如何根据不同平台调整内容策略？",
                "follow_up": "各个平台的用户特点有什么不同？"
            },
            {
                "id": 6,
                "dimension": "Personality",
                "question": "在快节奏的工作环境中，您如何保持创作灵感？",
                "follow_up": "您有什么提高工作效率的方法？"
            },
            {
                "id": 7,
                "dimension": "Ability",
                "question": "请谈谈您在用户互动和社群运营方面的经验。",
                "follow_up": "您是如何提高用户参与度的？"
            },
            {
                "id": 8,
                "dimension": "Motivation",
                "question": "为什么选择新媒体运营这个方向？",
                "follow_up": "您的职业规划是什么？"
            },
            {
                "id": 9,
                "dimension": "Value",
                "question": "您认为优质的财经内容应该具备哪些特点？",
                "follow_up": "如何平衡专业性和通俗性？"
            },
            {
                "id": 10,
                "dimension": "Motivation",
                "question": "您对海外投资内容创作有什么想法？",
                "follow_up": "您认为这个领域有哪些机会？"
            }
        ],
        "interview_strategy": "重点考察内容创作能力、财经知识基础、用户运营技能和行业敏感度。"
    }

def generate_default_questions():
    """默认通用问题"""
    return {
        "questions": [
            {
                "id": 1,
                "dimension": "Knowledge",
                "question": "请简单介绍一下您自己和您的专业背景。",
                "follow_up": "可以详细谈谈您的学习经历"
            },
            {
                "id": 2,
                "dimension": "Skill",
                "question": "请描述一个您最近完成的项目或工作任务。",
                "follow_up": "在这个项目中您遇到了什么挑战？"
            },
            {
                "id": 3,
                "dimension": "Ability",
                "question": "您认为自己最大的优势是什么？",
                "follow_up": "能举个具体的例子说明吗？"
            },
            {
                "id": 4,
                "dimension": "Personality",
                "question": "请描述一下您的工作风格和性格特点。",
                "follow_up": "同事们通常如何评价您？"
            },
            {
                "id": 5,
                "dimension": "Motivation",
                "question": "为什么选择应聘这个职位？",
                "follow_up": "您的职业规划是什么？"
            },
            {
                "id": 6,
                "dimension": "Value",
                "question": "您理想的工作环境是什么样的？",
                "follow_up": "您如何看待团队合作？"
            },
            {
                "id": 7,
                "dimension": "Knowledge",
                "question": "请谈谈您对行业发展趋势的看法。",
                "follow_up": "您是如何保持专业知识更新的？"
            },
            {
                "id": 8,
                "dimension": "Skill",
                "question": "请描述一次您解决复杂问题的经历。",
                "follow_up": "您的解决思路是什么？"
            },
            {
                "id": 9,
                "dimension": "Ability",
                "question": "面对压力时，您通常如何应对？",
                "follow_up": "能分享一个具体的例子吗？"
            },
            {
                "id": 10,
                "dimension": "Motivation",
                "question": "您希望在新工作中获得什么？",
                "follow_up": "您能为公司带来什么价值？"
            }
        ],
        "interview_strategy": "通过多维度问题全面了解候选人的专业能力、个人特质和发展潜力。"
    }

def find_resume_path(candidate_name):
    """根据候选人姓名查找简历文件路径"""
    from pathlib import Path
    import os
    
    # 获取当前脚本的目录
    current_dir = Path(__file__).parent
    
    # 简历文件夹映射
    resume_folders = [
        "Python工程师服务器端开发",
        "C端产品经理-AIGC领域", 
        "金融海外投资新媒体内容文案编辑运营"
    ]
    
    # 尝试多个可能的路径
    possible_base_paths = [
        current_dir.parent / "resouse",  # ../resouse/
        current_dir / ".." / "resouse",  # ../resouse/
        Path("resouse"),  # ./resouse/
        Path(".") / "resouse"  # ./resouse/
    ]
    
    for base_path in possible_base_paths:
        for folder in resume_folders:
            folder_path = base_path / folder
            if folder_path.exists():
                print(f"检查文件夹: {folder_path}")
                for pdf_file in folder_path.glob("*.pdf"):
                    print(f"检查文件: {pdf_file.stem} vs {candidate_name}")
                    if candidate_name in pdf_file.stem:
                        print(f"找到匹配文件: {pdf_file}")
                        return str(pdf_file)
    
    print(f"未找到候选人 {candidate_name} 的简历文件")
    return None

def get_job_description(position_code):
    """获取职位描述"""
    # 这里可以从数据库或配置文件获取职位描述
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

def save_interview_questions(candidate, questions_data):
    """保存面试问题到数据库"""
    import uuid
    
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 创建面试会话问题表（用于存储具体面试会话的问题）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interview_session_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                candidate_name TEXT,
                candidate_email TEXT,
                questions_json TEXT,
                strategy TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        session_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO interview_session_questions (session_id, candidate_name, candidate_email, questions_json, strategy)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            candidate.name,
            candidate.email,
            json.dumps(questions_data["questions"], ensure_ascii=False),
            questions_data.get("interview_strategy", "")
        ))
        
        conn.commit()
        return session_id
        
    finally:
        conn.close()

@app.get("/api/interview/{session_id}/questions")
async def get_interview_questions(session_id: str):
    """获取面试问题"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT questions_json, strategy, candidate_name, candidate_email
            FROM interview_session_questions 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        
        if result:
            questions = json.loads(result[0])
            return {
                "session_id": session_id,
                "questions": questions,
                "strategy": result[1],
                "candidate_name": result[2],
                "candidate_email": result[3]
            }
        else:
            raise HTTPException(status_code=404, detail="面试问题未找到")
            
    finally:
        conn.close()

@app.post("/api/interview/{session_id}/answer")
async def submit_answer(session_id: str, answer_data: dict):
    """提交面试回答并获取AI评分"""
    try:
        question_id = answer_data.get("question_id")
        question_text = answer_data.get("question")
        answer_text = answer_data.get("answer")
        dimension = answer_data.get("dimension")
        
        # 获取候选人信息
        candidate_name = get_candidate_name_by_session(session_id)
        
        # 使用LLM评估回答
        evaluation = llm_service.evaluate_answer(question_text, answer_text, dimension)
        
        # 保存回答和评分到数据库
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        
        try:
            # 创建回答表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interview_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    question_id INTEGER,
                    question_text TEXT,
                    answer_text TEXT,
                    dimension TEXT,
                    score INTEGER,
                    feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                INSERT INTO interview_answers 
                (session_id, question_id, question_text, answer_text, dimension, score, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_id, question_id, question_text, answer_text, 
                dimension, evaluation["score"], evaluation["feedback"]
            ))
            
            conn.commit()
            
        finally:
            conn.close()
        
        # 更新CSV文件中的评分
        if candidate_name:
            try:
                from csv_handler import csv_handler
                csv_handler.update_candidate_score(candidate_name, dimension, evaluation["score"])
            except Exception as e:
                print(f"更新CSV评分失败: {e}")
        
        return {
            "evaluation": evaluation,
            "message": "回答提交成功"
        }
        
    except Exception as e:
        print(f"处理面试回答失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理回答失败: {str(e)}")

def get_candidate_name_by_session(session_id):
    """根据会话ID获取候选人姓名"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT candidate_name 
            FROM interview_session_questions 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Exception as e:
        print(f"获取候选人姓名失败: {e}")
        return None
    finally:
        conn.close()

@app.post("/api/ai-chat")
async def ai_chat(message_data: dict):
    """AI数据分析助手对话"""
    try:
        user_message = message_data.get("message", "")
        context = message_data.get("context", {})
        
        if not user_message:
            raise HTTPException(status_code=400, detail="消息内容不能为空")
        
        # 调用AI聊天服务
        result = ai_chat_service.chat_with_ai(user_message, context)
        
        return {
            "response": result["response"],
            "timestamp": result["timestamp"],
            "success": True
        }
        
    except Exception as e:
        print(f"AI聊天失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI聊天失败: {str(e)}")

@app.post("/api/generate-report")
async def generate_analytics_report(report_data: dict):
    """生成数据分析报告"""
    try:
        report_type = report_data.get("type", "comprehensive")
        
        # 生成报告
        result = ai_chat_service.generate_analytics_report(report_type)
        
        return {
            "report": result["report"],
            "report_type": result["report_type"],
            "generated_at": result["generated_at"],
            "success": True
        }
        
    except Exception as e:
        print(f"生成报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")

@app.post("/api/candidates/{candidate_name}/finalize-scores")
async def finalize_candidate_scores(candidate_name: str, score_data: dict):
    """完成面试后，最终确定候选人各维度评分"""
    try:
        total_score = score_data.get("total_score", 0)
        dimension_scores = score_data.get("dimension_scores", {})
        
        # 更新CSV文件
        from csv_handler import csv_handler
        
        # 更新各维度评分（如果CSV中还没有的话）
        for dimension, score in dimension_scores.items():
            csv_handler.update_candidate_score(candidate_name, dimension, score)
        
        # 计算并更新总分
        calculated_total = csv_handler.calculate_total_score(candidate_name)
        
        return {
            "message": "评分更新成功",
            "candidate_name": candidate_name,
            "total_score": calculated_total,
            "dimension_scores": dimension_scores
        }
        
    except Exception as e:
        print(f"更新最终评分失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新评分失败: {str(e)}")

class EmailReportRequest(BaseModel):
    recipient: str
    subject: str
    message: str
    reportType: str = "comprehensive"

@app.post("/api/send-report-email")
async def send_report_email(email_data: EmailReportRequest):
    """发送报告邮件"""
    try:
        # 生成报告
        report_result = ai_chat_service.generate_analytics_report(email_data.reportType)
        
        if 'error' in report_result:
            raise HTTPException(status_code=500, detail="报告生成失败")
        
        # 格式化邮件内容
        email_content = format_email_content(
            email_data.message,
            report_result['report'],
            email_data.reportType
        )
        
        # 使用QQ邮箱发送真实邮件
        success = send_real_email(
            email_data.recipient,
            email_data.subject,
            email_content
        )
        
        if success:
            return {
                "success": True,
                "message": f"报告已成功发送到 {email_data.recipient}",
                "sent_at": datetime.now().isoformat(),
                "report_type": email_data.reportType
            }
        else:
            raise HTTPException(status_code=500, detail="邮件发送失败")
            
    except Exception as e:
        print(f"发送报告邮件失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

def format_email_content(user_message, report_content, report_type):
    """格式化邮件内容"""
    
    report_type_names = {
        'comprehensive': '综合分析报告',
        'summary': '摘要报告',
        'candidate_analysis': '候选人分析报告',
        'position_comparison': '职位对比报告'
    }
    
    type_name = report_type_names.get(report_type, '分析报告')
    
    email_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>招聘数据分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .report {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .footer {{ background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI招聘系统 - {type_name}</h1>
    </div>
    
    <div class="content">
        <p>{user_message}</p>
        
        <div class="report">
            <h2>分析报告</h2>
            <pre style="white-space: pre-wrap; font-family: inherit;">{report_content}</pre>
        </div>
        
        <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>如有任何问题，请联系HR部门。</p>
    </div>
    
    <div class="footer">
        <p>此邮件由AI招聘系统自动生成 | © 2025 AI招聘系统</p>
    </div>
</body>
</html>
    """
    
    return email_html

def send_real_email(recipient, subject, content):
    """使用QQ邮箱发送真实邮件"""
    
    print(f"发送邮件:")
    print(f"收件人: {recipient}")
    print(f"主题: {subject}")
    print(f"内容长度: {len(content)} 字符")
    
    try:
        # 使用邮件服务发送HTML邮件
        success = email_service.send_report_email(
            recipient_email=recipient,
            candidate_name="候选人",  # 可以从上下文获取
            report_content=content
        )
        
        if success:
            print("邮件发送成功!")
            
            # 记录发送日志
            log_file = Path("../frontend/data/email_log.txt")
            log_file.parent.mkdir(exist_ok=True)
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"收件人: {recipient}\n")
                f.write(f"主题: {subject}\n")
                f.write(f"状态: 发送成功\n")
                f.write(f"内容: {content[:200]}...\n")
        else:
            print("邮件发送失败!")
            
        return success
        
    except Exception as e:
        print(f"邮件发送异常: {e}")
        return False

@app.get("/api/candidates/top")
async def get_top_candidates():
    """获取评分最高的候选人"""
    try:
        candidates = excel_loader.load_candidates()
        top_candidates = excel_loader.get_top_candidates(candidates, limit=5)
        return top_candidates
    except Exception as e:
        print(f"获取最佳候选人失败: {e}")
        return []

@app.get("/api/candidates/recent")
async def get_recent_candidates():
    """获取最新的候选人"""
    try:
        candidates = excel_loader.load_candidates()
        recent_candidates = excel_loader.get_recent_candidates(candidates, limit=5)
        return recent_candidates
    except Exception as e:
        print(f"获取最新候选人失败: {e}")
        return []

@app.get("/api/jobs")
async def get_jobs():
    """获取职位列表 - 使用真实Excel数据"""
    try:
        jobs = excel_loader.load_jobs()
        return jobs
    except Exception as e:
        print(f"加载职位数据失败: {e}")
        return []

# 邮件发送相关的数据模型
class EmailRequest(BaseModel):
    recipient: str
    candidate_name: str
    report_content: str
    email_type: str = "report"  # report, invitation

class InvitationRequest(BaseModel):
    recipient: str
    candidate_name: str
    interview_time: str
    interview_link: str

@app.post("/api/email/send-report")
async def send_report_email_api(email_request: EmailRequest):
    """发送分析报告邮件"""
    try:
        success = email_service.send_report_email(
            recipient_email=email_request.recipient,
            candidate_name=email_request.candidate_name,
            report_content=email_request.report_content
        )
        
        if success:
            return {"success": True, "message": "报告邮件发送成功"}
        else:
            return {"success": False, "message": "邮件发送失败"}
            
    except Exception as e:
        print(f"发送报告邮件失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

@app.post("/api/email/send-invitation")
async def send_invitation_email_api(invitation_request: InvitationRequest):
    """发送面试邀请邮件"""
    try:
        success = email_service.send_interview_invitation(
            recipient_email=invitation_request.recipient,
            candidate_name=invitation_request.candidate_name,
            interview_time=invitation_request.interview_time,
            interview_link=invitation_request.interview_link
        )
        
        if success:
            return {"success": True, "message": "面试邀请邮件发送成功"}
        else:
            return {"success": False, "message": "邮件发送失败"}
            
    except Exception as e:
        print(f"发送面试邀请邮件失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

@app.post("/api/email/test")
async def test_email():
    """测试邮件发送功能"""
    try:
        test_content = """
这是一封测试邮件，用于验证QQ邮箱SMTP服务是否正常工作。

测试内容包括：
• 邮件服务器连接
• 身份验证
• 邮件发送
• 中文编码

如果您收到这封邮件，说明邮件服务配置成功！
        """
        
        success = email_service.send_report_email(
            recipient_email="1509008060@qq.com",  # 发送给自己测试
            candidate_name="测试候选人",
            report_content=test_content
        )
        
        if success:
            return {"success": True, "message": "测试邮件发送成功"}
        else:
            return {"success": False, "message": "测试邮件发送失败"}
            
    except Exception as e:
        print(f"测试邮件发送失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试邮件发送失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)