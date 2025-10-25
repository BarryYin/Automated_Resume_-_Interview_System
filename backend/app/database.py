from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# 数据库配置
DATABASE_URL = "sqlite:///./recruitment.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

# 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()