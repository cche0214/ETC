from sqlalchemy import create_engine
from .models import Base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///./research-agent.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit = False, 
    autoflush=False, 
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 可以多次被调用：
# 1. 首次调用创建数据库数据表
# 2. 之后调用不会重复创建
def create_tables():
    Base.metadata.create_all(bind=engine)