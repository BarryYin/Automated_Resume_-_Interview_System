from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
from datetime import datetime

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
    """获取候选人列表"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM candidates ORDER BY created_at DESC")
    candidates = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": c[0],
            "name": c[1], 
            "email": c[2],
            "invitation_code": c[3],
            "created_at": c[4]
        } for c in candidates
    ]

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
    """获取仪表板统计数据"""
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    # 活跃职位数
    cursor.execute("SELECT COUNT(DISTINCT invitation_code) FROM candidates WHERE invitation_code IS NOT NULL")
    active_positions = cursor.fetchone()[0]
    
    # 候选人数
    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]
    
    # 已完成面试数
    cursor.execute("SELECT COUNT(*) FROM interview_sessions WHERE status = '已完成'")
    completed_interviews = cursor.fetchone()[0]
    
    # 平均分数
    cursor.execute("SELECT AVG(score) FROM interview_sessions WHERE score IS NOT NULL")
    avg_score = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "active_positions": active_positions,
        "total_candidates": total_candidates, 
        "completed_interviews": completed_interviews,
        "average_score": round(avg_score, 1)
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)