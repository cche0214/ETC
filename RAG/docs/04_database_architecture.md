# 04_数据库架构 (Database Architecture)

## 1. 架构总览
系统采用了混合存储架构 (Polyglot Persistence)，根据数据热度和查询场景选择不同的数据库。

| 数据库 | 角色 | 部署节点 | 端口 | 用途 |
| :--- | :--- | :--- | :--- | :--- |
| **MySQL** | 结构化存储 | node1, node2, node3 | 3306 | 存储清洗后的业务数据，供 SQL Agent 查询 |
| **HBase** | 宽表存储 | node1 (Master), node2, 3 | 16000/8085(Thrift) | 存储全量原始/清洗流水，支持高吞吐写入 |
| **Redis** | 缓存/实时 | node1 | 6379 | 存储实时计算结果（流量桶、报警列表） |

## 2. MySQL 分库分表设计
为了应对海量数据查询，MySQL 采用了分库分表策略，并通过 ShardingSphere-Proxy 进行统一路由。

### 2.1 物理部署 (3库)
*   **node1 (traffic_db1)**：存储 `睢宁县`、`丰县`、`高速五大队` 相关数据。
*   **node2 (traffic_db2)**：存储 `新沂市`、`邳州市` 相关数据。
*   **node3 (traffic_db3)**：存储 `铜山县`、`沛县` 相关数据。
*   *注：按行政区划垂直拆分库有利于本地化查询优化。*

### 2.2 逻辑分表 (12表)
在每个物理库内部，为了防止单表过大，根据 **车牌号 (HPHM)** 进行哈希取模分表。
*   **分片键**：`HPHM`
*   **算法**：`hash(HPHM) % 4`
*   **表名模式**：`etc_records_0`, `etc_records_1`, `etc_records_2`, `etc_records_3`
*   **总表数**：3库 × 4表 = 12张真实表。

### 2.3 路由层
*   **中间件**：ShardingSphere-Proxy (运行在 node1)
*   **监听端口**：`3307`
*   **逻辑库名**：`traffic` (或 `etc_traffic_data`)
*   **访问方式**：应用连接 3307 端口，像操作单库单表一样操作 `etc_records`，中间件自动路由。

## 3. HBase Schema 设计
HBase 用于海量历史数据的持久化存储，名为 `etc_traffic_data`。

### 3.1 表结构
*   **Table Name**: `etc_traffic_data`
*   **Column Family**: `info`
*   **预分区 (Pre-splitting)**：`['3','6','9','C','F']` (防止热点写入)

### 3.2 RowKey 设计
为了支持按时间倒序查询（最新的数据最先查到）和按卡口/车牌检索，RowKey 设计如下：
`RowKey = <reverse_ts>-<HPHM>-<CLEAN_KKMC>-<GCXH>`

*   `reverse_ts`: `Long.MAX_VALUE - timestamp`。时间越大，差值越小，在 HBase 排序中越靠前。
*   `HPHM`: 车牌号。
*   `CLEAN_KKMC`: 清洗后的卡口名称。
*   `GCXH`: 唯一流水号（防重）。

## 4. Redis 数据结构
Redis 用于支撑实时大屏和报警。

*   **套牌车报警**：
    *   **Type**: List
    *   **Key**: `Traffic:Alert:Decked`
    *   **Value**: JSON String (包含车牌、两次出现地点、时间差)
    *   **操作**: `LPUSH` (入队), `LTRIM` (保持最新的 50 条)

*   **实时流量统计**：
    *   **Type**: Hash
    *   **Key**: `Traffic:Flow:{CLEAN_KKMC}` (按卡口区分)
    *   **Field**: `timestamp_bucket` (5分钟时间桶的时间戳)
    *   **Value**: `count` (流量计数值)
    *   **操作**: `HINCRBY`
    *   **TTL**: 24小时

