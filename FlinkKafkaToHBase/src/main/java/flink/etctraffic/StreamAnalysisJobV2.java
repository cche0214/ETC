package flink.etctraffic;

import com.alibaba.fastjson.JSONObject;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.StateTtlConfig;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.tuple.Tuple;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.util.Collector;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.util.Properties;

/**
 * ETC 实时流处理任务 V2
 * 功能包含：
 * 1. HBase 原始数据存储 (保留)
 * 2. Redis 套牌车实时检测 (保留)
 * 3. Redis 5分钟流量统计 (新增 - 用于 LSTM 预测)
 */
public class StreamAnalysisJobV2 {

    public static void main(String[] args) throws Exception {
        System.out.println("==================================================================");
        System.out.println(">>> ETC 综合流处理任务 V2 启动 (HBase + Decked + TrafficFlow) <<<");
        System.out.println("==================================================================");

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(3);

        Properties props = new Properties();
        props.setProperty("bootstrap.servers", "node1:9092,node2:9092,node3:9092");
        props.setProperty("group.id", "flink_traffic_analysis_group_v2"); // 修改消费者组，避免与旧任务冲突
        props.setProperty("auto.offset.reset", "latest");

        FlinkKafkaConsumer<String> consumer = new FlinkKafkaConsumer<>(
                "etc_traffic_data",
                new SimpleStringSchema(),
                props);

        DataStream<String> stream = env.addSource(consumer);

        // 1. HBase 存储 (原封不动)
        stream.addSink(new HBaseSinkFunction());

        // 2. 套牌车检测 -> Redis (原封不动)
        stream
            .map(line -> line.split(","))
            .filter(parts -> parts.length >= 15)
            .keyBy(13) // HPHM (车牌号)
            .process(new DeckedVehicleProcessFunction())
            .addSink(new RedisAlertSink());

        // 3. [新增] 5分钟流量统计 -> Redis
        // 不需要 keyBy，直接在 Sink 中处理，或者为了并行度也可以先 keyBy(卡口)
        // 这里选择直接 Sink，在 Sink 内部计算时间桶并写入 Redis Hash
        stream
            .map(line -> line.split(","))
            .filter(parts -> parts.length >= 15)
            .addSink(new TrafficFlowSink());

        env.execute("ETC Traffic Analysis V2 (HBase + Decked + Flow)");
    }

    // =========================================================================
    // 1. HBase Sink (保持不变)
    // =========================================================================
    public static class HBaseSinkFunction extends RichSinkFunction<String> {
        private Connection connection;
        private BufferedMutator mutator;
        private final String tableName = "etc_traffic_data";
        private final String family = "info";
        private long count = 0;

        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
            System.out.println(">>> HBase Sink started (Subtask " + getRuntimeContext().getIndexOfThisSubtask() + ")");
            org.apache.hadoop.conf.Configuration config = HBaseConfiguration.create();
            config.set("hbase.zookeeper.quorum", "node1,node2,node3");
            config.set("hbase.zookeeper.property.clientPort", "2181");
            connection = ConnectionFactory.createConnection(config);
            BufferedMutatorParams params = new BufferedMutatorParams(TableName.valueOf(tableName));
            params.writeBufferSize(4 * 1024);
            mutator = connection.getBufferedMutator(params);
        }

        @Override
        public void close() throws Exception {
            super.close();
            if (mutator != null) {
                mutator.flush();
                mutator.close();
            }
            if (connection != null) connection.close();
        }

        @Override
        public void invoke(String value, Context context) throws Exception {
            try {
                String[] fields = value.split(",");
                if (fields.length < 15) {
                    return;
                }

                String gcxh = fields[0];
                String xzqhmc = fields[1];
                String roadId = fields[2];
                String kIndex = fields[3];
                String boundaryLevel = fields[4];
                String boundaryDetail = fields[5];
                String boundaryLabel = fields[6];
                String cleanKkmc = fields[7];
                String fxlx = fields[8];
                String gcsj = fields[9];
                String gcsjTsStr = fields[10];
                String hpzl = fields[11];
                String hpzlLabel = fields[12];
                String hphm = fields[13];
                String brand = fields[14];

                long ts = Long.parseLong(gcsjTsStr);
                String reverseTs = String.valueOf(Long.MAX_VALUE - ts);
                String rowKey = reverseTs + "-" + hphm + "-" + cleanKkmc + "-" + gcxh;

                Put put = new Put(Bytes.toBytes(rowKey));
                byte[] cf = Bytes.toBytes(family);

                put.addColumn(cf, Bytes.toBytes("GCXH"), Bytes.toBytes(gcxh));
                put.addColumn(cf, Bytes.toBytes("XZQHMC"), Bytes.toBytes(xzqhmc));
                put.addColumn(cf, Bytes.toBytes("ROAD_ID"), Bytes.toBytes(roadId));
                put.addColumn(cf, Bytes.toBytes("K_INDEX"), Bytes.toBytes(kIndex));
                put.addColumn(cf, Bytes.toBytes("BOUNDARY_LEVEL"), Bytes.toBytes(boundaryLevel));
                put.addColumn(cf, Bytes.toBytes("BOUNDARY_DETAIL"), Bytes.toBytes(boundaryDetail));
                put.addColumn(cf, Bytes.toBytes("BOUNDARY_LABEL"), Bytes.toBytes(boundaryLabel));
                put.addColumn(cf, Bytes.toBytes("CLEAN_KKMC"), Bytes.toBytes(cleanKkmc));
                put.addColumn(cf, Bytes.toBytes("FXLX"), Bytes.toBytes(fxlx));
                put.addColumn(cf, Bytes.toBytes("GCSJ"), Bytes.toBytes(gcsj));
                put.addColumn(cf, Bytes.toBytes("GCSJ_TS"), Bytes.toBytes(gcsjTsStr));
                put.addColumn(cf, Bytes.toBytes("HPZL"), Bytes.toBytes(hpzl));
                put.addColumn(cf, Bytes.toBytes("HPZL_LABEL"), Bytes.toBytes(hpzlLabel));
                put.addColumn(cf, Bytes.toBytes("HPHM"), Bytes.toBytes(hphm));
                put.addColumn(cf, Bytes.toBytes("BRAND"), Bytes.toBytes(brand));

                mutator.mutate(put);

                count++;
                if (count % 2000 == 0) {
                    System.out.println(">>> HBase Sink (Subtask " + getRuntimeContext().getIndexOfThisSubtask() + "): Saved " + count + " records.");
                }

            } catch (Exception e) {
                // 忽略错误，避免日志刷屏
            }
        }
    }

    // =========================================================================
    // 2. 套牌车检测 ProcessFunction (保持不变)
    // =========================================================================
    public static class DeckedVehicleProcessFunction extends KeyedProcessFunction<Tuple, String[], String> {
        private ValueState<Tuple3<String, Long, String>> lastSeenState;

        @Override
        public void open(Configuration parameters) {
            // 使用 TypeHint 解决泛型擦除问题
            ValueStateDescriptor<Tuple3<String, Long, String>> descriptor = 
                new ValueStateDescriptor<>(
                    "lastSeen", 
                    TypeInformation.of(new TypeHint<Tuple3<String, Long, String>>() {})
                );
            
            StateTtlConfig ttlConfig = StateTtlConfig.newBuilder(Time.hours(1))
                .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
                .setStateVisibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
                .build();
            descriptor.enableTimeToLive(ttlConfig);
            
            lastSeenState = getRuntimeContext().getState(descriptor);
        }

        @Override
        public void processElement(String[] value, Context ctx, Collector<String> out) throws Exception {
            try {
                String currentKkmc = value[7];
                long currentTime = Long.parseLong(value[10]);
                String plate = value[13];

                Tuple3<String, Long, String> lastSeen = lastSeenState.value();

                if (lastSeen != null) {
                    // 10分钟 (600000ms) 内出现在不同卡口
                    if (!currentKkmc.equals(lastSeen.f0) && Math.abs(currentTime - lastSeen.f1) < 600000) {
                        JSONObject json = new JSONObject();
                        json.put("plate", plate);
                        json.put("msg", "套牌嫌疑: 10分钟内跨越不可达距离");
                        json.put("loc1", lastSeen.f0);
                        json.put("loc2", currentKkmc);
                        // 统一存储时间戳 (Long)，方便后端统一格式化
                        json.put("time", Long.parseLong(value[10]));
                        
                        String alertJson = json.toJSONString();
                        System.out.println("!!! 套牌车报警 !!! " + alertJson);
                        out.collect(alertJson);
                    }
                }
                
                if (lastSeen == null || currentTime > lastSeen.f1) {
                    lastSeenState.update(new Tuple3<>(currentKkmc, currentTime, plate));
                }
            } catch (Exception e) { }
        }
    }

    // =========================================================================
    // 3. Redis 报警 Sink (保持不变)
    // =========================================================================
    public static class RedisAlertSink extends RichSinkFunction<String> {
        private transient JedisPool pool;

        @Override
        public void open(Configuration parameters) {
            JedisPoolConfig config = new JedisPoolConfig();
            config.setMaxTotal(5);
            config.setMaxIdle(2);
            pool = new JedisPool(config, "192.168.88.131", 6379, 2000, "050214@Redis");
        }

        @Override
        public void invoke(String value, Context context) {
            try (Jedis jedis = pool.getResource()) {
                jedis.lpush("Traffic:Alert:Decked", value);
                jedis.ltrim("Traffic:Alert:Decked", 0, 49);
                System.out.println(">>> Redis Alert pushed: " + value);
            } catch (Exception e) {
                System.err.println("Redis write error: " + e.getMessage());
            }
        }

        @Override
        public void close() {
            if (pool != null) pool.close();
        }
    }

    // =========================================================================
    // 4. [新增] Redis 流量统计 Sink (时间窗口桶模式)
    // =========================================================================
    public static class TrafficFlowSink extends RichSinkFunction<String[]> {
        private transient JedisPool pool;
        private long count = 0;

        @Override
        public void open(Configuration parameters) {
            System.out.println(">>> Traffic Flow Sink started (Subtask " + getRuntimeContext().getIndexOfThisSubtask() + ")");
            JedisPoolConfig config = new JedisPoolConfig();
            config.setMaxTotal(10); // 流量统计并发可能较高，稍微调大连接池
            config.setMaxIdle(5);
            pool = new JedisPool(config, "192.168.88.131", 6379, 2000, "050214@Redis");
        }

        @Override
        public void invoke(String[] value, Context context) {
            try (Jedis jedis = pool.getResource()) {
                // 1. 获取卡口名称 (CLEAN_KKMC)
                String kkmc = value[7];
                
                // 2. 获取过车时间戳
                long ts = Long.parseLong(value[10]); // GCSJ_TS (毫秒)

                // 3. 计算所属的 5分钟时间桶
                // 算法: ts - (ts % 5分钟毫秒数)
                long bucketSize = 5 * 60 * 1000L;
                long bucketTs = ts - (ts % bucketSize);
                
                // 4. 直接使用时间戳作为 Key (例如 1701388800000)
                String timeBucket = String.valueOf(bucketTs);

                // 5. 构造 Redis Key: Traffic:Flow:{卡口名称}
                String redisKey = "Traffic:Flow:" + kkmc;

                // 6. 执行 HINCRBY (哈希表自增)
                jedis.hincrBy(redisKey, timeBucket, 1);
                
                // 7. 更新全局最新时间 (用于 Flask 前端同步进度)
                // 注意：高并发下频繁 SET 可能会有性能损耗，但为了演示实时性，这里每条都更新
                // 优化建议：实际生产中可以使用 static 变量缓存或采样更新
                jedis.set("Traffic:LatestTime", String.valueOf(ts));

                // 8. (可选) 设置过期时间，例如保留 24 小时
                jedis.expire(redisKey, 24 * 60 * 60);

                count++;
                if (count % 2000 == 0) {
                    System.out.println(">>> Traffic Flow Sink (Subtask " + getRuntimeContext().getIndexOfThisSubtask() + "): Aggregated " + count + " records.");
                }

            } catch (Exception e) {
                System.err.println("Redis flow stats error: " + e.getMessage());
            }
        }

        @Override
        public void close() {
            if (pool != null) pool.close();
        }
    }
}
