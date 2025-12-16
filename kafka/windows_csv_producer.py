# -*- coding: utf-8 -*-
import os
import time
import glob
from kafka import KafkaProducer
from kafka.errors import KafkaError

# ====================================================
# 配置区域 (请根据实际环境修改)
# 我的大数据集群环境kafka_2.12-2.4.1 flink-1.10.0 hbase-2.3.6 /hadoop-3.3.0 apache-zookeeper-3.5.9-bin
# 三台虚拟机之间可以互相通信 集群的基本环境都配置好了 本地windows机器也做了域名映射
# 三台虚拟机都开启了分片副本 有自己的brokerid
# 这个文件是本地发消息给三台虚拟机的kafka的脚本
# 启动之后会把windows的数据发给etc_traffic_data主题的消息队列里面
# ====================================================

# Kafka 集群地址
# 如果本地无法解析 node1, node2, node3，请修改为 IP 地址，例如 '192.168.1.101:9092'
BOOTSTRAP_SERVERS = ['node1:9092', 'node2:9092', 'node3:9092']

# Kafka Topic 名称
TOPIC_NAME = 'etc_traffic_data'

# CSV 数据根目录
# 假设脚本在 kafka/ 目录下运行，数据在 ../data_all/
# 如果脚本在项目根目录运行，请修改为 'data_all'
# 这里使用相对路径，向上两级找到 data_all (根据脚本所在位置调整)
# 为了稳健性，这里使用绝对路径的拼接方式，假设 data_all 在项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_all')

# 指定需要读取的子目录
TARGET_SUBDIRS = ['202312', '202401']

# 发送延迟 (秒)
SLEEP_TIME = 0.05   #改成0.02
# ====================================================

def create_producer():
    """创建 Kafka Producer 实例"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            # 消息值序列化为 UTF-8 字节
            value_serializer=lambda v: v.encode('utf-8'),
            # 增加一些超时设置，防止网络波动导致报错
            request_timeout_ms=20000,
            api_version_auto_timeout_ms=20000
        )
        print(f"成功连接到 Kafka 集群: {BOOTSTRAP_SERVERS}")
        return producer
    except Exception as e:
        print(f"连接 Kafka 失败: {e}")
        return None

def on_send_success(record_metadata):
    """发送成功回调"""
    print(f"[发送成功] topic: {record_metadata.topic}, partition: {record_metadata.partition}, offset: {record_metadata.offset}")

def on_send_error(excp):
    """发送失败回调"""
    print(f"[发送失败] 错误信息: {excp}")

def process_csv_file(producer, file_path):
    """处理单个 CSV 文件"""
    print(f"\n正在处理文件: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取第一行（表头）并跳过
            header = f.readline()
            if not header:
                print(f"文件为空: {file_path}")
                return

            line_count = 0
            for line in f:
                line = line.strip() # 去除首尾空白符
                if not line:
                    continue # 跳过空行

                # 发送消息
                # 使用异步发送，并添加回调函数
                future = producer.send(TOPIC_NAME, value=line)
                future.add_callback(on_send_success)
                future.add_errback(on_send_error)
                
                line_count += 1
                
                # 模拟实时发送延迟
                time.sleep(SLEEP_TIME)
            
            print(f"文件 {os.path.basename(file_path)} 处理完成，共发送 {line_count} 条数据")
            
            # 确保所有消息都已发送
            producer.flush()

    except Exception as e:
        print(f"处理文件 {file_path} 时发生错误: {e}")

def main():
    """主程序入口"""
    print("=== 开始启动 Kafka 生产者程序 ===")
    
    # 1. 检查数据目录是否存在
    if not os.path.exists(DATA_DIR):
        print(f"错误: 数据目录不存在 -> {DATA_DIR}")
        print("请检查 BASE_DIR 和 DATA_DIR 的配置")
        return

    # 2. 创建 Producer
    producer = create_producer()
    if not producer:
        return

    # 3. 遍历指定目录下的 CSV 文件
    csv_files = []
    for subdir in TARGET_SUBDIRS:
        # 修改：只查找 _fixed.csv 结尾的文件 (已清洗且时间戳已修正)
        search_path = os.path.join(DATA_DIR, subdir, '*_fixed.csv')
        # glob.glob 支持通配符查找
        found_files = glob.glob(search_path)
        csv_files.extend(found_files)
        print(f"在 {subdir} 目录下找到 {len(found_files)} 个已修正的 CSV 文件")

    if not csv_files:
        print("未找到任何 _fixed.csv 文件，请先运行 clean_data_timestamps.py 进行清洗。")
        producer.close()
        return

    print(f"总计找到 {len(csv_files)} 个 CSV 文件，准备开始发送...")
    
    # 4. 逐个处理文件
    try:
        for file_path in csv_files:
            process_csv_file(producer, file_path)
    except KeyboardInterrupt:
        print("\n用户中断程序")
    finally:
        if producer:
            producer.close()
            print("Kafka Producer 已关闭")
    
    print("=== 程序运行结束 ===")

if __name__ == '__main__':
    main()
