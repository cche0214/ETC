# 08_部署与运维手册 (Deployment & Ops)

## 1. 集群环境
*   **操作系统**: CentOS Linux release 7.7.1908 (Core)
*   **节点规划**:
    *   **node1 (192.168.88.131)**: Master, NameNode, HMaster, Kafka, Redis, MyCat/Proxy
    *   **node2 (192.168.88.132)**: Slave, DataNode, RegionServer, Kafka
    *   **node3 (192.168.88.133)**: Slave, DataNode, RegionServer, Kafka

## 2. 端口清单
| 服务 | 端口 | 说明 |
| :--- | :--- | :--- |
| **HDFS NameNode** | 9870 | HDFS Web UI |
| **YARN ResourceManager** | 8088 | YARN Web UI |
| **Flink Dashboard** | 8081 | Flink 集群监控 |
| **HBase Thrift** | 8085 | 供 Python/Flask 客户端连接 |
| **HBase Master** | 16010 | HBase Web UI |
| **Zookeeper** | 2181 | 协调服务 |
| **Kafka** | 9092 | 消息队列服务 |
| **MySQL** | 3306 | 原始数据库端口 |
| **ShardingProxy** | 3307 | 分库分表代理端口 (对外暴露) |
| **Redis** | 6379 | 缓存服务 |
| **Agent API** | 8001 | 智能问答后端 |

## 3. 启动流程 (按顺序)
在 **node1** 执行以下命令：

1.  **基础集群 (Hadoop + ZK)**:
    ```bash
    zkServer.sh start  # (需在三台机器分别执行)
    start-dfs.sh
    start-yarn.sh
    ```

2.  **Kafka**:
    ```bash
    # 在三台机器分别执行
    kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties
    ```

3.  **HBase**:
    ```bash
    start-hbase.sh
    hbase-daemon.sh start thrift -p 8085 # 开启 Thrift 接口
    ```

4.  **Flink**:
    ```bash
    /export/server/flink/bin/start-cluster.sh
    ```

5.  **中间件**:
    ```bash
    redis-server /export/server/redis-6.2.6/redis.conf
    /export/server/shardingsphere-proxy/bin/start.sh
    ```

6.  **提交 Flink 任务**:
    ```bash
    flink run -d -m node1:8081 -c flink.etctraffic.StreamAnalysisJobV2 /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar
    ```

## 4. 停止流程
1.  停止 Flink Cluster.
2.  停止 HBase (先停 Thrift, 再停 HBase).
3.  停止 Kafka.
4.  停止 Hadoop (YARN, DFS).
5.  停止 Zookeeper.

## 5. 常见运维操作
*   **重置 HBase 表**:
    ```ruby
    hbase shell
    > truncate 'etc_traffic_data'
    ```
*   **重置 Kafka Topic**:
    ```bash
    kafka-topics.sh --delete --topic etc_traffic_data ...
    kafka-topics.sh --create --topic etc_traffic_data ...
    ```
*   **查看 Agent 日志**:
    FastAPI 默认输出到控制台，建议使用 `nohup` 或 `Supervisor` 托管。

