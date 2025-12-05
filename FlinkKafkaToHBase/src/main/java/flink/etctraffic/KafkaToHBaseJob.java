package flink.etctraffic;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;

import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.TableName;
import org.apache.hadoop.hbase.client.BufferedMutator;
import org.apache.hadoop.hbase.client.BufferedMutatorParams;
import org.apache.hadoop.hbase.client.Connection;
import org.apache.hadoop.hbase.client.ConnectionFactory;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.util.Bytes;

import java.util.Properties;

public class KafkaToHBaseJob {

    public static void main(String[] args) throws Exception {
        // 在 Client 端打印提示信息
        System.out.println("==================================================================");
        System.out.println(">>> ETC 实时流计算任务启动 (ETC Traffic Stream Job Starting) <<<");
        System.out.println(">>> 正在连接 Kafka (node1:9092) 并准备写入 HBase... <<<");
        System.out.println("==================================================================");

        // 1. 获取执行环境
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        // 设置并行度为 3，与 Kafka 分区数保持一致，实现 1:1 高效消费
        env.setParallelism(3);

        // 2. 配置 Kafka Consumer
        Properties props = new Properties();
        // Kafka 集群地址
        props.setProperty("bootstrap.servers", "node1:9092,node2:9092,node3:9092");
        // 消费者组 ID
        props.setProperty("group.id", "flink_hbase_group");
        // 从最新数据开始消费
        props.setProperty("auto.offset.reset", "latest");

        FlinkKafkaConsumer<String> consumer = new FlinkKafkaConsumer<>(
                "etc_traffic_data",
                new SimpleStringSchema(),
                props);

        // 3. 读取数据
        DataStream<String> stream = env.addSource(consumer);

        // 4. 写入 HBase (使用 BufferedMutator 进行批量写入)
        stream.addSink(new HBaseSinkFunction());

        // 5. 执行任务
        env.execute("ETC Traffic Real-time Analysis Job");
    }

    /**
     * 自定义 HBase Sink
     * 使用 BufferedMutator 实现客户端缓冲写入，提高吞吐量
     */
    public static class HBaseSinkFunction extends RichSinkFunction<String> {
        private Connection connection;
        private BufferedMutator mutator; // 替代 Table，用于批量写入
        private final String tableName = "etc_traffic_data";
        private final String family = "info";

        @Override
        public void open(Configuration parameters) throws Exception {
            super.open(parameters);
            // 1. 创建 HBase 配置
            org.apache.hadoop.conf.Configuration config = HBaseConfiguration.create();
            config.set("hbase.zookeeper.quorum", "node1,node2,node3");
            config.set("hbase.zookeeper.property.clientPort", "2181");
            
            // 2. 创建全局连接 (一个 Task Slot 复用一个 Connection)
            // Connection 对象是重量级的，但在 HBase 2.x 中是线程安全的，这里我们在 open 中初始化
            connection = ConnectionFactory.createConnection(config);
            
            // 3. 创建 BufferedMutator (用于异步批量写入)
            // 设置写缓存大小为 4KB (原 2MB)，以便在数据量较小时也能快速刷写到 HBase
            BufferedMutatorParams params = new BufferedMutatorParams(TableName.valueOf(tableName));
            params.writeBufferSize(4 * 1024); // 4KB 缓存
            mutator = connection.getBufferedMutator(params);
        }

        @Override
        public void close() throws Exception {
            super.close();
            // 关闭时强制刷写剩余数据
            if (mutator != null) {
                mutator.flush();
                mutator.close();
            }
            if (connection != null) connection.close();
        }

        @Override
        public void invoke(String value, Context context) throws Exception {
            try {
                // CSV 解析逻辑...
                String[] fields = value.split(",");
                // 字段数从 16 变为 15 (移除了 GCSJ_MQ)
                if (fields.length < 15) {
                    System.err.println("ERROR: 字段不足 (" + fields.length + ") - " + value);
                    return;
                }

                // 提取字段 (注意索引变化)
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

                // 构造 RowKey
                long ts = Long.parseLong(gcsjTsStr);
                String reverseTs = String.valueOf(Long.MAX_VALUE - ts);
                String rowKey = reverseTs + "-" + hphm + "-" + cleanKkmc + "-" + gcxh;

                // --- 打印日志 (Web UI 可见) ---
                System.out.println(">>> Writing RowKey: " + rowKey);

                // --- 执行 HBase 写入 (Mutator) ---
                Put put = new Put(Bytes.toBytes(rowKey));
                byte[] cf = Bytes.toBytes(family);

                // 添加列 (保持原样)
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

                // 这里的 mutate 不会立即发送 RPC，而是先放入本地缓冲区
                // 等缓冲区满了(2MB)或者调用 flush() 时才发送
                mutator.mutate(put);

            } catch (Exception e) {
                System.err.println("ERROR: 处理失败 - " + value + " | " + e.getMessage());
                e.printStackTrace();
            }
        }
    }
}
