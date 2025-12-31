import os
from dotenv import load_dotenv
import urllib.parse

# 加载 .env 文件
load_dotenv()

class Settings:
    # 基础配置
    PROJECT_NAME: str = "ETC Research Agent"
    VERSION: str = "1.0.0"
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    MODEL_NAME: str = "deepseek-chat" # 或 deepseek-reasoner
    
    # 业务数据库 (MySQL Proxy) - 用于 Agent 查询
    TRAFFIC_DB_USER: str = os.getenv("TRAFFIC_DB_USER", "traffic")
    TRAFFIC_DB_PASSWORD: str = os.getenv("TRAFFIC_DB_PASSWORD", "050214@Proxy")
    TRAFFIC_DB_HOST: str = os.getenv("TRAFFIC_DB_HOST", "192.168.88.131")
    TRAFFIC_DB_PORT: str = os.getenv("TRAFFIC_DB_PORT", "3307")
    TRAFFIC_DB_NAME: str = os.getenv("TRAFFIC_DB_NAME", "traffic")
    
    # API 服务地址 (用于生成静态资源链接)
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8001")
    
    @property
    def SQLALCHEMY_TRAFFIC_DATABASE_URI(self) -> str:
        # 注意：密码需要做 URL 编码
        encoded_pwd = urllib.parse.quote(self.TRAFFIC_DB_PASSWORD)
        return f"mysql+mysqlconnector://{self.TRAFFIC_DB_USER}:{encoded_pwd}@{self.TRAFFIC_DB_HOST}:{self.TRAFFIC_DB_PORT}/{self.TRAFFIC_DB_NAME}"

    # 聊天记录数据库 (SQLite) - 用于 Session 管理
    SQLITE_URL: str = "sqlite:///./research-agent.db"

settings = Settings()

