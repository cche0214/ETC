# 05_流计算 (Stream Processing)

## 1. Flink 任务概览
流计算模块负责实时处理 Kafka 传来的交通数据。
*   **任务入口类**：`flink.etctraffic.StreamAnalysisJobV2`
*   **Flink 版本**：1.10.0 (Java)
*   **并行度**：3 (对应 Kafka 分区数)

## 2. 处理流程 (Pipeline)

### 2.1 Source (输入)
*   **组件**：`FlinkKafkaConsumer`
*   **Topic**：`etc_traffic_data`
*   **Group ID**：`flink_traffic_analysis_group_v2`
*   **Offset 策略**：`latest` (实时消费)

### 2.2 Transformation & Logic

#### A. 数据清洗与解析
*   `SimpleStringSchema` 读取字符串。
*   `map`: 按逗号 `,` 分割 CSV 格式。
*   `filter`: 过滤字段长度不足 15 的脏数据。

#### B. 套牌车实时检测 (Decked Vehicle Detection)
*   **核心算子**：`KeyedProcessFunction`
*   **KeyBy**: `HPHM` (车牌号，索引 13)
*   **State**: `ValueState<Tuple3<Location, Time, Plate>>` (保存该车牌上一次出现的记录)
*   **逻辑**：
    1.  新来一条数据，读取该车牌的状态。
    2.  如果状态存在，计算 `当前时间 - 上次时间`。
    3.  **判定规则**：如果 `diff < 10分钟` 且 `当前地点 != 上次地点` -> **判定为套牌嫌疑** (假设10分钟内无法跨越两个卡口)。
    4.  输出报警信息到 Redis Sink。
    5.  更新状态为当前记录。
    6.  **TTL**: 状态设置 1 小时过期 (StateTtlConfig)，防止内存无限增长。

#### C. 实时流量聚合 (Traffic Flow Stats)
*   **逻辑**：
    *   无需 `KeyBy`，直接在 Sink 中处理以减少 Shuffle 开销（或者在 Sink 前预聚合）。
    *   计算时间桶：`bucketTs = ts - (ts % 5min)`，将时间对齐到最近的 5 分钟整点。
    *   统计维度：按卡口 (`CLEAN_KKMC`)。
    *   输出到 Redis Sink。

### 2.3 Sink (输出)

#### A. HBase Sink
*   实现 `RichSinkFunction`。
*   使用 `BufferedMutator` 批量异步写入。
*   构造 `Put` 对象，写入 RowKey 和列族 `info`。

#### B. Redis Alert Sink
*   连接 Redis。
*   `lpush` 写入报警队列。

#### C. Traffic Flow Sink
*   连接 Redis。
*   `hincrBy` 增加对应卡口、对应时间桶的计数。
*   更新 `Traffic:LatestTime` 以便前端感知进度。

## 3. 部署命令
```bash
# 提交任务到集群
flink run -d -m node1:8081 -c flink.etctraffic.StreamAnalysisJobV2 /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar
```

