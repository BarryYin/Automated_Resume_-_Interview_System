from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Candidate(Base):
    """候选人模型"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    invitation_code = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联面试会话
    interview_sessions = relationship("InterviewSession", back_populates="candidate")

class InterviewSession(Base):
    """面试会话模型"""
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(20), default="进行中")  # 进行中, 已完成, 已中断
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 关联
    candidate = relationship("Candidate", back_populates="interview_sessions")
    qa_records = relationship("InterviewQA", back_populates="session")

class InterviewQA(Base):
    """面试问答记录模型"""
    __tablename__ = "interview_qa"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("interview_sessions.session_id"))
    question_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    ai_score = Column(Float, nullable=True)  # AI评分
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联
    session = relationship("InterviewSession", back_populates="qa_records")

class Position(Base):
    """职位模型"""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    status = Column(String(20), default="active")  # active, inactive, closed
    created_at = Column(DateTime, default=datetime.utcnow)