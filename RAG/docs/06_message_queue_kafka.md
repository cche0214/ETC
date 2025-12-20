# 06_消息队列 (Message Queue)

## 1. Kafka 架构
Kafka 作为整个系统的“大动脉”，负责解耦数据生产端和消费端。

*   **版本**：Kafka 2.4.1 (Scala 2.12)
*   **集群节点**：node1, node2, node3 (9092端口)
*   **依赖**：Zookeeper (node1:2181)

## 2. Topic 配置
*   **名称**：`etc_traffic_data`
*   **分区数 (Partitions)**：3 (对应 3 个 Broker，实现负载均衡)
*   **副本数 (Replication Factor)**：3 (高可用，允许挂掉 2 个节点)
*   **创建命令**：
    ```bash
    kafka-topics.sh --create --bootstrap-server node1:9092 --replication-factor 3 --partitions 3 --topic etc_traffic_data
    ```

## 3. 生产者 (Producer)
由于真实环境的数据接入困难，本项目使用 Python 脚本模拟实时数据流。

*   **脚本**：`kafka/windows_csv_producer.py`
*   **运行环境**：Windows (开发机)
*   **数据源**：`data_all/` 目录下的清洗后 CSV 文件 (`*_fixed.csv`)。
*   **发送逻辑**：
    *   连接集群 `node1:9092, node2:9092, node3:9092`。
    *   按行读取 CSV。
    *   模拟延迟：`time.sleep(0.05)` 控制发送速率，模拟真实车流。
    *   **异步回调**：设置 `on_send_success` 和 `on_send_error` 监控发送状态。

## 4. 消费者 (Consumer)
主要消费者是 Flink 集群。
*   **Group ID**: `flink_traffic_analysis_group_v2`
*   **Offset Reset**: `latest` (只处理启动后新到达的数据，避免处理历史积压)。
*   **Offset 机制**：Kafka 自动维护 Consumer Group 的 Offset，确保 Flink 重启后能接续（如果配置了 Checkpoint，Flink 会自行管理 Offset）。

## 5. 常用运维命令
*   **查看 Topic 列表**：`kafka-topics.sh --list --bootstrap-server node1:9092`
*   **查看消费进度 (Lag)**：`kafka-consumer-groups.sh --bootstrap-server node1:9092 --describe --group flink_traffic_analysis_group_v2`
*   **消费控制台实时查看**：
    ```bash
    kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc_traffic_data --from-beginning --max-messages 10
    ```

