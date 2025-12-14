import happybase
import redis
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

# 配置信息
HBASE_THRIFT_HOST = "192.168.88.131"
HBASE_THRIFT_PORT = 8085
TABLE_NAME = 'etc_traffic_data'

REDIS_HOST = "192.168.88.131"
REDIS_PORT = 6379
REDIS_PASSWORD = "050214@Redis"

# MySQL (ShardingSphere-Proxy) 配置
MYSQL_HOST = "192.168.88.131"
MYSQL_PORT = 3307
MYSQL_USER = "root"
MYSQL_PASSWORD = "050214@Proxy"
MYSQL_DB = "traffic"

# Redis Key 常量
REDIS_KEY_DECKED = "Traffic:Alert:Decked"
REDIS_KEY_LATEST_TIME = "Traffic:LatestTime"
REDIS_KEY_FLOW_PREFIX = "Traffic:Flow:"

# 监测卡口列表
MONITOR_STATIONS = [
    "G3-K731-省际卡口", "S325-K63-市际卡口", "G104-K873-省际卡口",
    "S323-K96-市际卡口", "G518-K358-省际卡口", "S250-K1-省际卡口",
    "G104-K744-省际卡口", "G235-K10-市际卡口", "G206-K816-省际卡口",
    "G310-K310-省际卡口", "S253-K0-省际卡口", "S252-K56-省际卡口",
    "S505-K10-市际卡口", "S324-K201-市际卡口", "X308-K19-市际卡口",
    "G311-K207-省际卡口", "S323-K10-市际卡口", "S251-K5-省际卡口",
    "G237-K148-省际卡口"
]

def get_hbase_conn():
    """获取 HBase 连接 (带超时)"""
    return happybase.Connection(HBASE_THRIFT_HOST, port=HBASE_THRIFT_PORT, timeout=5000)

def get_redis_conn():
    """获取 Redis 连接"""
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)

# 创建 MySQL 引擎 (连接池)
# 使用 pymysql 驱动
# 注意：密码中包含特殊字符（如 @）时需要进行 URL 编码
mysql_engine = create_engine(
    f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4",
    pool_size=10,
    pool_recycle=3600,
    echo=False  # 设置为 True 可打印 SQL 语句用于调试
)

# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)

def get_db_session():
    """获取 MySQL Session (用于依赖注入或上下文管理)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
