import happybase
import redis

# 配置信息
HBASE_THRIFT_HOST = "192.168.88.131"
HBASE_THRIFT_PORT = 8085
TABLE_NAME = 'etc_traffic_data'

REDIS_HOST = "192.168.88.131"
REDIS_PORT = 6379
REDIS_PASSWORD = "050214@Redis"

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
