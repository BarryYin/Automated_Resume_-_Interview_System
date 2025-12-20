from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json

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

@app.get("/")
async def root():
    return {"message": "AI招聘系统API"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# 简单的候选人API
@app.get("/api/candidates")
async def get_candidates():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates LIMIT 10")
    candidates = cursor.fetchall()
    conn.close()
    return {"candidates": candidates}