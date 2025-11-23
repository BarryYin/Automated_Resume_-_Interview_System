from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from llm_service import llm_service
from ai_chat_service import ai_chat_service
from email_service import email_service
from excel_data_loader import excel_loader
from resume_parser import resume_parser

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

# 用户认证相关模型
class UserLogin(BaseModel):
    email: str
    password: str
    user_type: str = "candidate"  # candidate 或 admin

class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    user_type: str = "candidate"  # candidate 或 admin

class InterviewSession(BaseModel):
    candidate_id: int
    session_id: str
    status: str = "进行中"
    score: Optional[float] = None
    
class InterviewQuestion(BaseModel):
    question: str
    answer: Optional[str] = None

class CandidateStatusUpdate(BaseModel):
    status: str

class JobCreate(BaseModel):
    title: str
    department: str
    salaryMin: int
    salaryMax: int
    description: Optional[str] = ""
    requirements: Optional[str] = ""

class CandidateCreate(BaseModel):
    name: str
    email: str
    phone: Optional[str] = ""
    education: Optional[str] = ""
    experience: Optional[str] = ""
    skills: Optional[str] = ""
    current_position: Optional[str] = ""
    expected_salary: Optional[str] = ""
    summary: Optional[str] = ""
    invitation_code: Optional[str] = None

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
            phone TEXT,
            education TEXT,
            experience TEXT,
            skills TEXT,
            current_position TEXT,
            expected_salary TEXT,
            summary TEXT,
            resume_file_path TEXT,
            invitation_code TEXT,
            status TEXT DEFAULT '待面试',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 检查并添加缺失的列
    cursor.execute('PRAGMA table_info(candidates)')
    columns = [column[1] for column in cursor.fetchall()]
    
    # 添加新字段
    new_columns = {
        'phone': 'TEXT',
        'education': 'TEXT', 
        'experience': 'TEXT',
        'skills': 'TEXT',
        'current_position': 'TEXT',
        'expected_salary': 'TEXT',
        'summary': 'TEXT',
        'resume_file_path': 'TEXT',
        'status': 'TEXT DEFAULT "待面试"',
        'updated_at': 'TIMESTAMP'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            try:
                cursor.execute(f'ALTER TABLE candidates ADD COLUMN {col_name} {col_type}')
                print(f"Added {col_name} column to candidates table")
            except Exception as e:
                print(f"Column {col_name} might already exist: {e}")
    
    # 更新updated_at字段
    cursor.execute('UPDATE candidates SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL')
    
    # 候选人状态变更日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate_status_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            old_status TEXT,
            new_status TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    ''')
    
    # 职位表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            salary_min INTEGER,
            salary_max INTEGER,
            description TEXT,
            requirements TEXT,
            status TEXT DEFAULT '招聘中',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT DEFAULT 'candidate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # AI反馈表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate_ai_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            strengths TEXT,
            improvements TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
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

# 用户认证API
@app.post("/api/auth/register")
async def register_user(user: UserRegister):
    """用户注册"""
    import hashlib
    import secrets
    
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="邮箱已被注册")
        
        # 生成密码哈希
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', user.password.encode(), salt.encode(), 100000)
        password_hash_hex = salt + password_hash.hex()
        
        # 插入用户
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, user_type)
            VALUES (?, ?, ?, ?)
        ''', (user.name, user.email, password_hash_hex, user.user_type))
        
        conn.commit()
        user_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "注册成功",
            "user": {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "user_type": user.user_type
            }
        }
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
    except Exception as e:
        print(f"注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    finally:
        conn.close()

@app.post("/api/auth/login")
async def login_user(user: UserLogin):
    """用户登录"""
    import hashlib
    import secrets
    import jwt
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 查找用户
        cursor.execute('''
            SELECT id, name, email, password_hash, user_type 
            FROM users 
            WHERE email = ?
        ''', (user.email,))
        
        db_user = cursor.fetchone()
        
        if not db_user:
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
        
        user_id, name, email, stored_hash, db_user_type = db_user
        
        # 验证用户类型
        if user.user_type != db_user_type:
            if user.user_type == "admin" and db_user_type != "admin":
                raise HTTPException(status_code=401, detail="该账号不是管理员账号")
            elif user.user_type == "candidate" and db_user_type != "candidate":
                raise HTTPException(status_code=401, detail="该账号不是候选人账号")
        
        # 验证密码
        salt = stored_hash[:32]  # 前32个字符是salt
        stored_password_hash = stored_hash[32:]  # 后面是密码哈希
        
        password_hash = hashlib.pbkdf2_hmac('sha256', user.password.encode(), salt.encode(), 100000)
        
        if password_hash.hex() != stored_password_hash:
            raise HTTPException(status_code=401, detail="邮箱或密码错误")
        
        # 生成JWT token
        secret_key = "your-secret-key-here"  # 在生产环境中应该使用环境变量
        payload = {
            "user_id": user_id,
            "email": email,
            "user_type": db_user_type,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        
        return {
            "success": True,
            "message": "登录成功",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "user_type": db_user_type
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
    finally:
        conn.close()

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
    """获取候选人列表 - 合并Excel数据和数据库面试数据"""
    try:
        # 从Excel加载真实候选人数据
        candidates = excel_loader.load_candidates()
        
        # 连接数据库
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        
        for candidate in candidates:
            candidate_name = candidate.get('name')
            candidate_email = candidate.get('email')
            
            # 1. 查询数据库中的面试评分（优先使用数据库数据）
            cursor.execute('''
                SELECT 
                    isq.session_id,
                    COUNT(ia.id) as answer_count,
                    AVG(ia.score) as avg_score,
                    MAX(ia.created_at) as last_answer_time
                FROM interview_session_questions isq
                LEFT JOIN interview_answers ia ON isq.session_id = ia.session_id
                WHERE isq.candidate_name = ? OR isq.candidate_email = ?
                GROUP BY isq.session_id
                ORDER BY last_answer_time DESC
                LIMIT 1
            ''', (candidate_name, candidate_email))
            
            db_interview = cursor.fetchone()
            
            # 如果数据库中有面试会话记录，说明候选人已经面试
            if db_interview and db_interview[0]:  # 有会话记录
                session_id, answer_count, avg_score, last_answer_time = db_interview
                
                # 只要有面试会话记录，就认为已完成面试
                # 不管回答了多少个问题，只要提交了就算完成
                if answer_count > 0:  # 有回答记录
                    candidate['status'] = '已完成'
                    candidate['score'] = int(avg_score) if avg_score else None
                    candidate['interview_date'] = last_answer_time.split()[0] if last_answer_time else candidate.get('interview_date')
                    candidate['db_interview'] = True
                    candidate['answer_count'] = answer_count
                else:
                    # 有会话但没有回答，保持原状态
                    candidate['db_interview'] = False
                    candidate['answer_count'] = 0
            else:
                candidate['db_interview'] = False
                candidate['answer_count'] = 0
            
            # 2. 查询该候选人的面试问题
            cursor.execute('''
                SELECT questions_json, strategy, created_at, updated_at
                FROM interview_questions
                WHERE candidate_name = ? OR candidate_email = ?
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (candidate_name, candidate_email))
            
            result = cursor.fetchone()
            
            if result:
                questions_json, strategy, created_at, updated_at = result
                candidate['interview_questions'] = json.loads(questions_json) if questions_json else []
                candidate['interview_strategy'] = strategy
                candidate['questions_generated_at'] = updated_at or created_at
                candidate['has_questions'] = True
            else:
                candidate['interview_questions'] = []
                candidate['interview_strategy'] = ''
                candidate['questions_generated_at'] = None
                candidate['has_questions'] = False
        
        conn.close()
        
        # 确保数据可以JSON序列化
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

@app.put("/api/candidates/{candidate_id}/status")
async def update_candidate_status(candidate_id: int, status_update: CandidateStatusUpdate):
    """更新候选人状态"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 首先尝试从数据库查找候选人
        cursor.execute("SELECT id, name, status FROM candidates WHERE id = ?", (candidate_id,))
        db_candidate = cursor.fetchone()
        
        if db_candidate:
            # 候选人在数据库中存在，直接更新
            old_status = db_candidate[2]
            cursor.execute('''
                UPDATE candidates 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (status_update.status, candidate_id))
            
            candidate_name = db_candidate[1]
        else:
            # 候选人不在数据库中，从Excel数据查找并插入
            candidates = excel_loader.load_candidates()
            excel_candidate = None
            
            for candidate in candidates:
                if candidate.get('id') == candidate_id:
                    excel_candidate = candidate
                    break
            
            if not excel_candidate:
                raise HTTPException(status_code=404, detail="候选人未找到")
            
            # 插入候选人到数据库
            cursor.execute('''
                INSERT INTO candidates (id, name, email, invitation_code, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (
                excel_candidate['id'],
                excel_candidate['name'],
                excel_candidate['email'],
                excel_candidate.get('invitation_code', ''),
                status_update.status
            ))
            
            candidate_name = excel_candidate['name']
            old_status = excel_candidate.get('status', '已完成')
        
        conn.commit()
        
        # 记录状态变更日志
        cursor.execute('''
            INSERT INTO candidate_status_log (candidate_id, old_status, new_status, changed_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (candidate_id, old_status, status_update.status))
        
        conn.commit()
        
        return {
            "success": True,
            "message": f"候选人 {candidate_name} 的状态已更新为 {status_update.status}",
            "candidate_id": candidate_id,
            "new_status": status_update.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"更新候选人状态失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"状态更新失败: {str(e)}")
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

class GenerateQuestionsRequest(BaseModel):
    candidate_id: int
    candidate_name: str
    candidate_email: str
    position: str
    position_code: Optional[str] = None
    feedback: Optional[str] = None  # 管理员的修改意见

@app.post("/api/candidates/{candidate_id}/generate-questions")
async def generate_candidate_questions(candidate_id: int, request: GenerateQuestionsRequest):
    """为指定候选人生成或重新生成面试问题"""
    try:
        print(f"为候选人 {request.candidate_name} (ID: {candidate_id}) 生成面试问题")
        
        # 查找简历文件
        resume_path = find_resume_path(request.candidate_name)
        resume_text = ""
        
        if resume_path:
            try:
                resume_text = llm_service.extract_text_from_pdf(resume_path)
                print(f"成功读取简历: {resume_path}")
            except Exception as e:
                print(f"读取简历失败: {e}")
        
        # 获取职位描述
        job_description = get_job_description(request.position_code or "1001")
        
        # 构建候选人信息
        candidate_data = {
            'name': request.candidate_name,
            'email': request.candidate_email,
            'position': request.position
        }
        
        # 如果有管理员反馈，添加到提示中
        if request.feedback:
            # 使用LLM根据反馈重新生成问题
            questions_data = llm_service.regenerate_questions_with_feedback(
                candidate_data, resume_text, job_description, request.feedback
            )
        else:
            # 正常生成问题
            questions_data = llm_service.generate_interview_questions(
                candidate_data, resume_text, job_description
            )
        
        # 保存到interview_questions表
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        
        try:
            # 创建表（如果不存在）
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
            
            # 检查是否已存在
            cursor.execute('''
                SELECT id FROM interview_questions 
                WHERE candidate_name = ? OR candidate_email = ?
            ''', (request.candidate_name, request.candidate_email))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE interview_questions 
                    SET questions_json = ?, strategy = ?, resume_path = ?, 
                        position_code = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_name = ? OR candidate_email = ?
                ''', (
                    json.dumps(questions_data["questions"], ensure_ascii=False),
                    questions_data.get("interview_strategy", ""),
                    resume_path or "",
                    request.position_code or "1001",
                    request.candidate_name,
                    request.candidate_email
                ))
                print(f"更新了候选人 {request.candidate_name} 的面试问题")
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO interview_questions 
                    (candidate_name, candidate_email, position_code, questions_json, strategy, resume_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    request.candidate_name,
                    request.candidate_email,
                    request.position_code or "1001",
                    json.dumps(questions_data["questions"], ensure_ascii=False),
                    questions_data.get("interview_strategy", ""),
                    resume_path or ""
                ))
                print(f"保存了候选人 {request.candidate_name} 的面试问题")
            
            conn.commit()
            
            return {
                "success": True,
                "message": "面试问题生成成功",
                "questions": questions_data["questions"],
                "strategy": questions_data.get("interview_strategy", ""),
                "generated_at": datetime.now().isoformat()
            }
            
        finally:
            conn.close()
        
    except Exception as e:
        print(f"生成面试问题失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成面试问题失败: {str(e)}")

@app.get("/api/candidates/{candidate_id}/questions")
async def get_candidate_questions(candidate_id: int):
    """获取候选人的面试问题"""
    try:
        # 从Excel数据获取候选人信息
        candidates = excel_loader.load_candidates()
        candidate_data = next((c for c in candidates if c.get('id') == candidate_id), None)
        
        if not candidate_data:
            raise HTTPException(status_code=404, detail="候选人未找到")
        
        candidate_name = candidate_data.get('name')
        candidate_email = candidate_data.get('email')
        
        # 查询面试问题
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT questions_json, strategy, created_at, updated_at, position_code
            FROM interview_questions
            WHERE candidate_name = ? OR candidate_email = ?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (candidate_name, candidate_email))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            questions_json, strategy, created_at, updated_at, position_code = result
            return {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "questions": json.loads(questions_json) if questions_json else [],
                "strategy": strategy,
                "position_code": position_code,
                "created_at": created_at,
                "updated_at": updated_at,
                "has_questions": True
            }
        else:
            return {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "questions": [],
                "strategy": "",
                "position_code": None,
                "has_questions": False
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取面试问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取面试问题失败: {str(e)}")

def generate_questions_by_name(candidate_name, position_code):
    """根据候选人姓名生成针对性问题"""
    
    # 候选人姓名到岗位代码的映射
    candidate_position_mapping = {
        "田忠": "1001",      # Python工程师
        "栾平": "1001",      # Python工程师
        "包涵": "1002",      # C端产品经理
        "乔志天": "1002",    # C端产品经理
        "高飞虎": "1003",    # 新媒体编辑
        "龙小天": "1003"     # 新媒体编辑
    }
    
    # 如果传入的position_code为空或不正确，从映射表中查找
    if not position_code or position_code == "1001":
        position_code = candidate_position_mapping.get(candidate_name, position_code)
    
    print(f"候选人 {candidate_name} 的岗位代码: {position_code}")
    
    # 为特定候选人生成个性化问题
    
    # 乔志天 - C端产品经理-AIGC领域
    if candidate_name == "乔志天":
        return {
            "questions": [
                {
                    "id": 1,
                    "dimension": "Knowledge",
                    "question": "请介绍一下您对AIGC领域的理解，特别是在C端产品应用方面的认知。",
                    "follow_up": "您认为AIGC技术会给C端产品带来哪些变革？"
                },
                {
                    "id": 2,
                    "dimension": "Skill",
                    "question": "请描述一个您主导的C端产品从0到1的完整过程。",
                    "follow_up": "在这个过程中，您是如何进行用户需求分析和产品定位的？"
                },
                {
                    "id": 3,
                    "dimension": "Ability",
                    "question": "在产品设计中，您如何平衡用户体验和技术实现的可行性？",
                    "follow_up": "能举个具体的例子说明您是如何做权衡的吗？"
                },
                {
                    "id": 4,
                    "dimension": "Knowledge",
                    "question": "您对当前主流的AIGC产品（如ChatGPT、Midjourney等）有什么看法？",
                    "follow_up": "如果让您设计一款AIGC产品，您会从哪个切入点开始？"
                },
                {
                    "id": 5,
                    "dimension": "Skill",
                    "question": "请谈谈您在用户研究和数据分析方面的经验和方法。",
                    "follow_up": "您通常使用哪些工具和指标来评估产品表现？"
                },
                {
                    "id": 6,
                    "dimension": "Personality",
                    "question": "在跨部门协作中，您如何推动产品需求的落地？",
                    "follow_up": "遇到技术团队和设计团队意见不一致时，您是如何处理的？"
                },
                {
                    "id": 7,
                    "dimension": "Motivation",
                    "question": "是什么吸引您选择AIGC领域的产品经理这个方向？",
                    "follow_up": "您的职业发展规划是什么？"
                },
                {
                    "id": 8,
                    "dimension": "Ability",
                    "question": "请描述一次产品迭代优化的经历，以及如何通过数据验证优化效果。",
                    "follow_up": "这次优化给产品带来了什么具体的改进？"
                },
                {
                    "id": 9,
                    "dimension": "Value",
                    "question": "您认为一个优秀的C端产品应该具备哪些核心特质？",
                    "follow_up": "在产品设计中，您如何平衡商业价值和用户价值？"
                },
                {
                    "id": 10,
                    "dimension": "Motivation",
                    "question": "您对我们公司的AIGC产品方向有什么想法和建议？",
                    "follow_up": "您希望在这个岗位上实现什么目标？"
                }
            ],
            "interview_strategy": "重点考察候选人对AIGC领域的理解、产品思维、用户洞察能力和跨部门协作能力。"
        }
    
    # 高飞虎 - 金融海外投资新媒体内容文案编辑运营
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
    
    # 其他候选人根据岗位代码匹配问题
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

@app.get("/api/candidates/{candidate_id}/ai-feedback")
async def generate_candidate_feedback(candidate_id: int, regenerate: bool = False):
    """使用AI生成候选人的优势亮点和待改进项（带缓存）"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 首先检查是否已有缓存的反馈
        if not regenerate:
            cursor.execute('''
                SELECT strengths, improvements, generated_at
                FROM candidate_ai_feedback
                WHERE candidate_id = ?
                ORDER BY generated_at DESC
                LIMIT 1
            ''', (candidate_id,))
            
            cached = cursor.fetchone()
            if cached:
                print(f"使用缓存的AI反馈，生成时间: {cached[2]}")
                return {
                    "strengths": json.loads(cached[0]) if cached[0] else [],
                    "improvements": json.loads(cached[1]) if cached[1] else [],
                    "cached": True,
                    "generated_at": cached[2]
                }
        
        print(f"生成新的AI反馈，候选人ID: {candidate_id}")
        # 获取候选人信息
        candidates = excel_loader.load_candidates()
        candidate_data = next((c for c in candidates if c.get('id') == candidate_id), None)
        
        if not candidate_data:
            raise HTTPException(status_code=404, detail="候选人未找到")
        
        candidate_name = candidate_data.get('name')
        candidate_email = candidate_data.get('email')
        position = candidate_data.get('position', '未知职位')
        
        # 获取面试记录
        cursor.execute('''
            SELECT session_id, questions_json, strategy, created_at
            FROM interview_session_questions
            WHERE candidate_name = ? OR candidate_email = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (candidate_name, candidate_email))
        
        session = cursor.fetchone()
        
        if not session:
            return {
                "strengths": ["候选人尚未完成面试"],
                "improvements": ["建议完成AI面试以获得详细评估"]
            }
        
        session_id = session[0]
        
        # 获取问答记录
        cursor.execute('''
            SELECT question_text, answer_text, dimension, score, feedback
            FROM interview_answers
            WHERE session_id = ?
            ORDER BY question_id
        ''', (session_id,))
        
        answers = cursor.fetchall()
        
        if not answers:
            return {
                "strengths": ["候选人尚未回答面试问题"],
                "improvements": ["建议完成面试问答以获得详细评估"]
            }
        
        # 构建AI提示
        qa_summary = ""
        dimension_scores = {}
        
        for answer in answers:
            q_text, a_text, dimension, score, feedback = answer
            qa_summary += f"\n维度：{dimension}\n问题：{q_text}\n回答：{a_text}\n评分：{score}分\n评价：{feedback}\n"
            
            if dimension not in dimension_scores:
                dimension_scores[dimension] = []
            dimension_scores[dimension].append(score)
        
        # 计算各维度平均分
        avg_scores = {dim: sum(scores)/len(scores) for dim, scores in dimension_scores.items()}
        
        prompt = f"""
请作为专业的HR评估专家，基于候选人的面试表现，生成优势亮点和待改进项。

候选人信息：
- 姓名：{candidate_name}
- 应聘职位：{position}

面试表现：
{qa_summary}

各维度平均分：
{chr(10).join([f'- {dim}: {score:.1f}分' for dim, score in avg_scores.items()])}

请生成：
1. 优势亮点（3-5条）：具体、客观、有说服力
2. 待改进项（2-4条）：建设性、可操作

要求：
- 基于实际回答内容和评分
- 语言简洁专业
- 突出关键点
- 避免空泛表述

请按以下JSON格式返回：
{{
    "strengths": ["优势1", "优势2", "优势3"],
    "improvements": ["改进建议1", "改进建议2"]
}}
"""
        
        try:
            response = llm_service.client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {"role": "system", "content": "你是一位专业的HR评估专家，擅长分析候选人表现并提供建设性反馈。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # 解析JSON响应
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # 如果没有找到JSON，尝试解析文本
                result = parse_feedback_text(content)
            
            # 保存到数据库
            save_ai_feedback(cursor, candidate_id, result)
            conn.commit()
            
            return {
                **result,
                "cached": False,
                "generated_at": datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"AI生成反馈失败: {e}")
            # 返回基于评分的基础反馈
            result = generate_basic_feedback(avg_scores, position)
            
            # 也保存基础反馈
            save_ai_feedback(cursor, candidate_id, result)
            conn.commit()
            
            return {
                **result,
                "cached": False,
                "generated_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"生成候选人反馈失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成反馈失败: {str(e)}")
    finally:
        conn.close()

def save_ai_feedback(cursor, candidate_id, feedback):
    """保存AI反馈到数据库"""
    try:
        # 创建表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidate_ai_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL,
                strengths TEXT,
                improvements TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id)
            )
        ''')
        
        # 插入反馈
        cursor.execute('''
            INSERT INTO candidate_ai_feedback (candidate_id, strengths, improvements)
            VALUES (?, ?, ?)
        ''', (
            candidate_id,
            json.dumps(feedback.get('strengths', []), ensure_ascii=False),
            json.dumps(feedback.get('improvements', []), ensure_ascii=False)
        ))
        
        print(f"AI反馈已保存到数据库，候选人ID: {candidate_id}")
        
    except Exception as e:
        print(f"保存AI反馈失败: {e}")

def parse_feedback_text(content):
    """解析文本格式的反馈"""
    strengths = []
    improvements = []
    
    lines = content.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if '优势' in line or 'strengths' in line.lower():
            current_section = 'strengths'
        elif '改进' in line or 'improvements' in line.lower():
            current_section = 'improvements'
        elif line.startswith(('-', '•', '*', '1.', '2.', '3.', '4.', '5.')):
            # 移除列表标记
            item = re.sub(r'^[-•*\d.]\s*', '', line)
            if current_section == 'strengths':
                strengths.append(item)
            elif current_section == 'improvements':
                improvements.append(item)
    
    return {
        "strengths": strengths[:5] if strengths else ["表达清晰，态度积极"],
        "improvements": improvements[:4] if improvements else ["可以更加深入地展开回答"]
    }

def generate_basic_feedback(avg_scores, position):
    """生成基础反馈（当AI调用失败时）"""
    strengths = []
    improvements = []
    
    # 根据评分生成反馈
    for dimension, score in avg_scores.items():
        if score >= 70:
            dim_name = {
                'Knowledge': '专业知识扎实',
                'Skill': '实操技能优秀',
                'Ability': '综合能力突出',
                'Personality': '性格特质良好',
                'Motivation': '求职动机明确',
                'Value': '价值观契合'
            }.get(dimension, f'{dimension}表现良好')
            strengths.append(dim_name)
        elif score < 50:
            dim_name = {
                'Knowledge': '专业知识需要加强',
                'Skill': '实操技能有待提升',
                'Ability': '综合能力需要培养',
                'Personality': '可以更好地展现个人特质',
                'Motivation': '建议更明确职业目标',
                'Value': '需要更深入了解企业文化'
            }.get(dimension, f'{dimension}需要改进')
            improvements.append(dim_name)
    
    if not strengths:
        strengths = [f"对{position}职位有一定了解", "态度积极，愿意学习"]
    
    if not improvements:
        improvements = ["可以更加深入地展开回答", "建议增加具体案例说明"]
    
    return {
        "strengths": strengths[:5],
        "improvements": improvements[:4]
    }

@app.get("/api/candidates/{candidate_id}/interview-records")
async def get_candidate_interview_records(candidate_id: int):
    """获取候选人的面试对话记录"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        # 首先获取候选人信息
        cursor.execute("SELECT name, email FROM candidates WHERE id = ?", (candidate_id,))
        candidate = cursor.fetchone()
        
        if not candidate:
            # 尝试从Excel数据中查找
            candidates = excel_loader.load_candidates()
            candidate_data = next((c for c in candidates if c.get('id') == candidate_id), None)
            if not candidate_data:
                raise HTTPException(status_code=404, detail="候选人未找到")
            candidate_name = candidate_data.get('name')
            candidate_email = candidate_data.get('email')
        else:
            candidate_name, candidate_email = candidate
        
        # 查找该候选人的面试会话
        cursor.execute('''
            SELECT session_id, questions_json, strategy, created_at
            FROM interview_session_questions
            WHERE candidate_name = ? OR candidate_email = ?
            ORDER BY created_at DESC
        ''', (candidate_name, candidate_email))
        
        sessions = cursor.fetchall()
        
        if not sessions:
            return {
                "candidate_id": candidate_id,
                "candidate_name": candidate_name,
                "sessions": [],
                "message": "该候选人暂无面试记录"
            }
        
        # 获取每个会话的问答记录
        interview_records = []
        
        for session in sessions:
            session_id, questions_json, strategy, created_at = session
            
            # 解析问题列表
            import json
            questions = json.loads(questions_json) if questions_json else []
            
            # 获取该会话的所有回答
            cursor.execute('''
                SELECT question_id, question_text, answer_text, dimension, score, feedback, created_at
                FROM interview_answers
                WHERE session_id = ?
                ORDER BY question_id
            ''', (session_id,))
            
            answers = cursor.fetchall()
            
            # 组合问题和回答
            qa_pairs = []
            for answer in answers:
                q_id, q_text, a_text, dimension, score, feedback, answer_time = answer
                
                # 找到对应的问题详情
                question_detail = next((q for q in questions if q.get('id') == q_id), None)
                
                qa_pairs.append({
                    "question_id": q_id,
                    "question": q_text,
                    "answer": a_text,
                    "dimension": dimension,
                    "score": score,
                    "feedback": feedback,
                    "follow_up": question_detail.get('follow_up', '') if question_detail else '',
                    "answered_at": answer_time
                })
            
            interview_records.append({
                "session_id": session_id,
                "interview_date": created_at,
                "strategy": strategy,
                "total_questions": len(questions),
                "answered_questions": len(answers),
                "qa_pairs": qa_pairs
            })
        
        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "total_sessions": len(interview_records),
            "sessions": interview_records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取面试记录失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取面试记录失败: {str(e)}")
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
    """获取职位列表 - 合并Excel数据和数据库数据"""
    try:
        # 从Excel加载基础数据
        excel_jobs = excel_loader.load_jobs()
        
        # 从数据库加载新创建的职位
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, department, salary_min, salary_max, 
                   description, requirements, status, created_at
            FROM jobs 
            ORDER BY created_at DESC
        ''')
        
        db_jobs = []
        for row in cursor.fetchall():
            db_jobs.append({
                'id': row[0] + 1000,  # 避免与Excel数据ID冲突
                'title': row[1],
                'department': row[2],
                'salary': f"¥{row[3]:,} - ¥{row[4]:,}",
                'salary_min': row[3],
                'salary_max': row[4],
                'description': row[5] or '',
                'requirements': row[6] or '',
                'status': row[7],
                'publish_date': row[8].split(' ')[0] if row[8] else '',
                'candidate_count': 0,  # 可以后续统计
                'recruiter': 'HR部门',
                'recruiter_email': 'hr@company.com'
            })
        
        conn.close()
        
        # 合并数据，数据库中的职位排在前面
        all_jobs = db_jobs + excel_jobs
        return all_jobs
        
    except Exception as e:
        print(f"加载职位数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.post("/api/jobs")
async def create_job(job: JobCreate):
    """创建新职位"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO jobs (title, department, salary_min, salary_max, description, requirements)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job.title,
            job.department,
            job.salaryMin,
            job.salaryMax,
            job.description,
            job.requirements or f"{job.title}职位要求待完善"
        ))
        
        conn.commit()
        job_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "职位创建成功",
            "job_id": job_id,
            "job": {
                "id": job_id + 1000,
                "title": job.title,
                "department": job.department,
                "salary": f"¥{job.salaryMin:,} - ¥{job.salaryMax:,}",
                "status": "招聘中"
            }
        }
        
    except Exception as e:
        print(f"创建职位失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建职位失败: {str(e)}")
    finally:
        conn.close()

@app.post("/api/candidates")
async def create_candidate(candidate: CandidateCreate):
    """创建新候选人"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO candidates (
                name, email, phone, education, experience, skills, 
                current_position, expected_salary, summary, invitation_code
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            candidate.name,
            candidate.email,
            candidate.phone,
            candidate.education,
            candidate.experience,
            candidate.skills,
            candidate.current_position,
            candidate.expected_salary,
            candidate.summary,
            candidate.invitation_code
        ))
        
        conn.commit()
        candidate_id = cursor.lastrowid
        
        return {
            "success": True,
            "message": "候选人创建成功",
            "candidate_id": candidate_id
        }
        
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    except Exception as e:
        print(f"创建候选人失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建候选人失败: {str(e)}")
    finally:
        conn.close()

@app.post("/api/candidates/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """解析上传的简历文件"""
    try:
        # 检查文件类型
        allowed_types = ['.pdf', '.docx', '.doc']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_types)}"
            )
        
        # 检查文件大小 (限制为10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        
        # 解析简历
        result = resume_parser.parse_resume_file(file_content, file.filename)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"简历解析失败: {e}")
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")

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

class InterviewInviteRequest(BaseModel):
    recipient: str
    candidate_name: str = "候选人"
    subject: str
    interview_time: str
    content: str
    email_type: str = "interview_invite"



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

@app.post("/api/email/send-invite")
async def send_interview_invite_api(invite_request: InterviewInviteRequest):
    """发送面试邀请邮件（新版本）"""
    try:
        # 生成面试链接
        interview_link = f"http://localhost:3000/interview?email={invite_request.recipient}&time={invite_request.interview_time}"
        
        # 使用自定义内容发送邮件
        success = email_service.send_custom_interview_invitation(
            recipient_email=invite_request.recipient,
            candidate_name=invite_request.candidate_name,
            subject=invite_request.subject,
            interview_time=invite_request.interview_time,
            content=invite_request.content,
            interview_link=interview_link
        )
        
        if success:
            return {"success": True, "message": f"面试邀请已发送到 {invite_request.recipient}"}
        else:
            return {"success": False, "message": "邮件发送失败"}
            
    except Exception as e:
        print(f"发送面试邀请失败: {e}")
        raise HTTPException(status_code=500, detail=f"邮件发送失败: {str(e)}")

class StatusNotificationRequest(BaseModel):
    recipient: str
    candidate_name: str
    status: str
    email_type: str = "status_notification"

@app.post("/api/email/send-notification")
async def send_status_notification_api(notification_request: StatusNotificationRequest):
    """发送状态通知邮件"""
    try:
        success = email_service.send_status_notification(
            recipient_email=notification_request.recipient,
            candidate_name=notification_request.candidate_name,
            status=notification_request.status
        )
        
        if success:
            return {"success": True, "message": f"状态通知邮件已发送到 {notification_request.recipient}"}
        else:
            return {"success": False, "message": "邮件发送失败"}
            
    except Exception as e:
        print(f"发送状态通知邮件失败: {e}")
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    uvicorn.run(app, host="0.0.0.0", port=8002)