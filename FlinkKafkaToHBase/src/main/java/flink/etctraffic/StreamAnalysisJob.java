package flink.etctraffic;

import com.alibaba.fastjson.JSONObject;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.StateTtlConfig;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.time.Time;
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
 * ETC 实时流处理任务 (HBase 存储 + Redis 套牌车检测)
 */
public class StreamAnalysisJob {

    public static void main(String[] args) throws Exception {
        System.out.println("==================================================================");
        System.out.println(">>> ETC 综合流处理任务启动 (HBase + Redis Decked Detection) <<<");
        System.out.println("==================================================================");

        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(3);

        Properties props = new Properties();
        props.setProperty("bootstrap.servers", "node1:9092,node2:9092,node3:9092");
        props.setProperty("group.id", "flink_traffic_analysis_group");
        props.setProperty("auto.offset.reset", "latest");

        FlinkKafkaConsumer<String> consumer = new FlinkKafkaConsumer<>(
                "etc_traffic_data",
                new SimpleStringSchema(),
                props);

        DataStream<String> stream = env.addSource(consumer);

        // 1. HBase 存储 (原封不动)
        stream.addSink(new HBaseSinkFunction());

        // 2. 套牌车检测 -> Redis
        stream
            .map(line -> line.split(","))
            .filter(parts -> parts.length >= 15)
            .keyBy(13) // HPHM
            .process(new DeckedVehicleProcessFunction())
            .addSink(new RedisAlertSink());

        env.execute("ETC Traffic Analysis (HBase + Redis)");
    }

    // ... HBaseSinkFunction (copied from KafkaToHBaseJob.java) ...
    public static class HBaseSinkFunction extends RichSinkFunction<String> {
        private Connection connection;
        private BufferedMutator mutator;
        private final String tableName = "etc_traffic_data";
        private final String family = "info";

        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
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
                    System.err.println("ERROR: 字段不足 (" + fields.length + ") - " + value);
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

                System.out.println(">>> Writing RowKey: " + rowKey);

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

            } catch (Exception e) {
                System.err.println("ERROR: 处理失败 - " + value + " | " + e.getMessage());
                e.printStackTrace();
            }
        }
    }

    // ... DeckedVehicleProcessFunction ...
    public static class DeckedVehicleProcessFunction extends KeyedProcessFunction<Tuple, String[], String> {
        private ValueState<Tuple3<String, Long, String>> lastSeenState;

        @Override
        public void open(Configuration parameters) {
            ValueStateDescriptor<Tuple3<String, Long, String>> descriptor = 
                new ValueStateDescriptor<>(
                    "lastSeen", 
                    org.apache.flink.api.common.typeinfo.TypeInformation.of(new org.apache.flink.api.common.typeinfo.TypeHint<Tuple3<String, Long, String>>() {})
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
                    if (!currentKkmc.equals(lastSeen.f0) && Math.abs(currentTime - lastSeen.f1) < 600000) {
                        JSONObject json = new JSONObject();
                        json.put("plate", plate);
                        json.put("msg", "套牌嫌疑: 10分钟内跨越不可达距离");
                        json.put("loc1", lastSeen.f0);
                        json.put("loc2", currentKkmc);
                        json.put("time", value[9]);
                        
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

    // ... RedisAlertSink ...
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
            } catch (Exception e) {
                System.err.println("Redis write error: " + e.getMessage());
            }
        }

        @Override
        public void close() {
            if (pool != null) pool.close();
        }
    }
}