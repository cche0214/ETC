# ETC-BigData-Platform
Highway ETC big data management and monitoring system built with Hadoop, Spark, Flink, and HBase.

  2025-11-30 项目规划
  1. 初步探索
    1.1 数据预处理：原始的数据很脏，每个月份的数据名称不一样，每个数据格式内部的内容也很乱，第一次只是简单清洗，应该根据需要对字段进行严格的清洗，这个需要确定。
    1.2 数据存储：现在的做法是简单清理数据得到12月和1月的两张大表，然后我只实现了用KafKa把每一条读入消息队列，然后Flink放入Hbase里面，Hbase的存储逻辑是需要设计row-key的，我目前设计的row-key不是很能达到我的要求，这个需要讨论；同时也可以用Flink放到MyCat中间件，存到MySQL里面，这里需要设计分库分表，需要讨论；最后是用Flink放到Redis里面，这个我没学过，可以再多了解一下，但是它可以用来做实时大屏。
    1.3 接口：目前我的电脑三台虚拟机node1 node2 node3的ip分别是192.168.88.131 192.168.88.132 192.168.88.133，然后我的电脑设置了域名映射可以ping通，其他人的电脑行不行？Hbase提供thrift接口，监听在8085，是给Flask调用Hbase使用的，前端用Vue对接Flask在我本地的8080接口来访问，这是目前实现的。然后就是MySQL我测试了把数据简单放在node1上面，通过node1的3306接口来访问，可以实现SQLAgent，当然这个后期要加强内容。
  2. 项目需求
    2.1 交互式访问：设置好MyCat的分片规则之后，KafKa生产数据，Flink接入MyCat然后根据规则把数据写入MySQL之后，通过langchain SQLAgent调用DeepSeek api来实现交互式查询。
    2.2 可视化大屏，动态展示实时信息，要求每半分钟一次对结果进行刷新：这个是说用Redis内存数据库来实现，但是我暂时还没了解，也可能可以用其他的。
    2.3 实时套牌车检测：这个的实现形式还没有考虑，不知道放在哪一个部分，实验给的例子是用Flink来计算分析，然后交给前端报警
    2.4 车流预警算法，对收费站车流进行实时预警并显示：这个考虑是用CNN+LSTM+Attention来实现预测，就是预测HBase里面的数据，当然是要预处理的，所以在实现算法之前要看看需要哪些字段。
  3. 一些其他问题
    3.1 给了一个CloudLab，其实就是国外的一些高性能计算机组成的集群，我们可以租用，但是在上面需要重新配置Hadoop Flink啥的，我就没搞，目前都是用的自己的虚拟机，然后去年他们用的是华为云的ECS？这个我不了解，没用过
2025-11-30 项目规划
1. 初步探索
1.1 数据预处理：原始的数据很脏，每个月份的数据名称不一样，每个数据格式内部的内容也很乱，第一次只是简单清洗，应该根据需要对字段进行严格的清洗，这个需要确定。
1.2 数据存储：现在的做法是简单清理数据得到12月和1月的两张大表，然后我只实现了用KafKa把每一条读入消息队列，然后Flink放入Hbase里面，Hbase的存储逻辑是需要设计row-key的，我目前设计的row-key不是很能达到我的要求，这个需要讨论；同时也可以用Flink放到MyCat中间件，存到MySQL里面，这里需要设计分库分表，需要讨论；最后是用Flink放到Redis里面，这个我没学过，可以再多了解一下，但是它可以用来做实时大屏。
1.3 接口：目前我的电脑三台虚拟机node1 node2 node3的ip分别是192.168.88.131 192.168.88.132 192.168.88.133，然后我的电脑设置了域名映射可以ping通，其他人的电脑行不行？Hbase提供thrift接口，监听在8085，是给Flask调用Hbase使用的，前端用Vue对接Flask在我本地的8080接口来访问，这是目前实现的。然后就是MySQL我测试了把数据简单放在node1上面，通过node1的3306接口来访问，可以实现SQLAgent，当然这个后期要加强内容。
2. 项目需求
2.1 交互式访问：设置好MyCat的分片规则之后，KafKa生产数据，Flink接入MyCat然后根据规则把数据写入MySQL之后，通过langchain SQLAgent调用DeepSeek api来实现交互式查询。
2.2 可视化大屏，动态展示实时信息，要求每半分钟一次对结果进行刷新：这个是说用Redis内存数据库来实现，但是我暂时还没了解，也可能可以用其他的。
2.3 实时套牌车检测：这个的实现形式还没有考虑，不知道放在哪一个部分，实验给的例子是用Flink来计算分析，然后交给前端报警
2.4 车流预警算法，对收费站车流进行实时预警并显示：这个考虑是用CNN+LSTM+Attention来实现预测，就是预测HBase里面的数据，当然是要预处理的，所以在实现算法之前要看看需要哪些字段。
3. 一些其他问题
3.1 给了一个CloudLab，其实就是国外的一些高性能计算机组成的集群，我们可以租用，但是在上面需要重新配置Hadoop Flink啥的，我就没搞，目前都是用的自己的虚拟机，然后去年他们用的是华为云的ECS？这个我不了解，没用过

目前的一些启动指令：
在 node1, node2, node3 分别执行:
    zkServer.sh start（status端口2181 stop） kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties（后台启动方式）
(在 NameNode 节点，通常是 node1)：
    start-dfs.sh start-yarn.sh  start-hbase.sh hbase-daemon.sh start thrift -p 8085
目前的停止指令：
kafka-server-stop.sh hbase-daemon.sh stop thrift stop-hbase.sh stop-yarn.sh stop-dfs.sh zkServer.sh stop

2025-12-2
了解数据，数据太脏了
八个字段 第一个唯一id 第二个行政区划 第三个具体卡口 第四个行车方向（1和2） 第五个过车时间（2023/12/1 0:08:00） 第六个号牌种类（有几个选项，也有缺失值，然后有点脏 02 01 52 51 13 22 -） 第七个具体车牌（4+3结构，有脏数据，这个要具体洗洗） 第八个车牌类型（品牌 车型 年款，有很多缺失值）
以上是根据20231201分析出来的，后面肯定有脏数据

以23-12-1的数据为例，确定清洗原则
1.唯一id，分析缺失值（无），不管
2.行政区划，就是七个县，分析缺失值（无），不管
3.具体卡口，给出映射规则，原始数据很乱，把他扩展成了更好的格式
    ROAD_ID（道路编号）	K_INDEX（K值）	BOUNDARY_LEVEL（边界级别，省级或者市级）	BOUNDARY_DETAIL（具体是哪里和哪里的卡口）		BOUNDARY_LABEL（属于哪个界）	CLEAN_KKMC（生成的编号 道路编号-K值-级别）
补充一点高速公路的知识：
高速公路的编号唯一确定一条高速/公路
K值的含义是，距离这条公路的起点开始，已经行驶了多少公里
所以根据编号+K值就可以唯一确定一个卡口，不需要这么多复杂字段
每个卡口有具体的字段，分成省中间，市之间
把鹿梁县的县道标记为X308，都在文件里面标出来了
4.行车方向：按照行车方向划分，取值为2的都是睢宁县，这个是个业务逻辑我觉得 所以 方向为2的数据只有两个具体的卡口名称
5.过车时间：加入TS时间戳字段和MQ MySQL可读字段 前者构建row-key的时候可以使用
                 GCSJ        GCSJ_TS              GCSJ_MQ
0  2023/12/1 0:02  1701388920000  2023-12-01 00:02:00
6.号牌种类02 01 52 51 13 22 - ：修改-为未知，保证为两位数
| HPZL 代码 | 含义      | 分类说明        |
| ------- | ------- | ----------- |
| **01**  | 大型汽车    | 大货车、大客车     |
| **02**  | 小型汽车    | 小轿车、SUV、面包车 |
| **13**  | 外籍汽车    | 外国 + 外交车    |
| **22**  | 港澳车辆    | 港车北上 / 澳车北上 |
| **51**  | 挂车      | Trailer     |
| **52**  | 教练车     | “学”字车       |
| **-**   | 缺失/无法识别 | 改写成未知  |
7.具体车牌：类似苏CD7***是规范格式 不符合的直接丢掉，因为这个字段其实指向很明显，没有这个其他业务根本没有必要分析
    正则脱敏：^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽粤青藏川宁琼][A-HJ-NP-Z][A-HJ-NP-Z0-9][A-Z0-9][A-Z0-9*]{3}$
8.车牌类型:最后是变成BRAND MODEL YEAR三个字段
CLPPXH 字段解析规则：
按 “-” 分割，第一段为品牌（去掉“牌”）
第二段为车型，如不存在则 NULL
第三段及之后内容用于提取年款
出现 “ ” 时只保留 “ ” 前部分
年款可能包含多个年份，使用 “_” 分隔，取第一项
若年款包含 “未知”“unknown”“进口车” 等，则 YEAR=未知
若模型包含 “未知”“unknown”“进口车” 等，则 MODEL=未知
车型中有一个特殊字符 Π1 变成车型 派1


2023 12 
2023-12-11-final.csv 	00:00:23	16:57:54 ⚠️ 缺失晚间数据
2023-12-12-final.csv  10:21:38	23:53:09 ⚠️ 原始缺失
2023-12-13-final.csv 10:25:35	23:59:35 ⚠️ 缺失早间数据
2024 01 
1月3日 00:00 - 11:43 ⚠️ 缺失下午和晚间数据 (12:00 - 24:00)
1月4日 09:51 - 23:59 ⚠️ 缺失早间数据 (00:00 - 09:50)
1月6日 00:00 - 16:23 ⚠️ 缺失晚间数据 (16:30 - 24:00)
1月7日 07:41 - 23:43 ⚠️ 缺失早间数据 (00:00 - 07:40)
1月13日 2024-01-10 00:00 - 23:59 ❌ 严重异常：数据日期为1月10日
1月14日 08:46 - 23:59 ⚠️ 缺失早间数据 (00:00 - 08:45)

今天主要是清洗


2025-12-3
今天需要明确分库分表和row-key，然后最好能在本地测试一下，
首先现在的数据有这些字段：
GCXH：过车序号，唯一并且填充数据以F开头
XZQHMC：行政区划名称，总共有七个县，睢宁县 邳州市 丰县 高速五大队 沛县 铜山县 新沂市
*============*
ROAD_ID：高速的编号
K_INDEX：高速卡口的K值
BOUNDARY_LEVEL:卡口的等级 省级PROVINCE 市级CITY
BOUNDARY_DETAIL：卡口属于哪两个地区之间 江苏-山东
BOUNDARY_LABEL:卡口属于哪个交界 苏鲁界
CLEAN_KKMC:S250-K1-省际卡口 唯一表示一个卡口 可以用于统计
*============*
FXLX：方向，取值为2的都是睢宁县，这个是个业务逻辑我觉得 
*============*
GCSJ：过车时间，清洗之后每个时间范围就是文件名称范围
GCSJ_TS：过车时间转化出的时间戳，用于设计row-key
2023-12-01 00:02:03
→ 转换为 Unix timestamp = 1701388923
→ 乘以 1000 = 1701388923000
GCSJ_MQ：过车时间的MySQL友好格式，给deepseek分析用
*============*
HPZL：号牌种类 02 01 52 51 13 22 未知 七种取值
HPZL_LABEL：号牌种类的映射 大型汽车 小型汽车 外籍汽车 港澳车辆 挂车 教练车 未知
HPHM：具体号牌号码，清理成 苏CD7*** 的格式
BRAND：车的品牌，只保留了这个字段够用了

刚刚突然想到，三个要求刚好对应三种计算模式
批处理：离线计算，预测
流式处理：实时计算，套牌车检测
交互式查询：交互式查询，deepseek

他们分别处理离线数据 流式数据 预处理的离线数据
如果是这样子的话 流处理只负责给hbase不就好了？
分库分表之后 放入mysql里面给deepseek，因为交互式查询是预处理的 离线 数据 哈哈

今天相当于啥也没干啊我操，感觉还是直接上Cloudlab的机器吧
Flink太老了老是出问题，得配一个互相适配的版本
妈的又要安装环境

业务逻辑？
数据大屏：
    数据总览：车辆总数（总体数据） 跨省流动 跨市县流动（BOUNDARY_LEVEL字段）

    ![alt text](image.png)

Flink:
/export/server/flink/bin/start-cluster.sh
/export/server/flink/bin/stop-cluster.sh

*=================*
2025-12-4 
*=================*
今天开始配置CloudLab三台真实机器的环境
我突然悟了，这三台机器一直都是没关闭的啊，所以不用一直启动集群关闭集群，把东西配好放上面就行了
之前一直没用，现在显示距离我申请都跑了20天了，
然后他是Ubuntu系统，之前学习的包括虚拟机都是CentOS，有点区别但不多
之前安装的Flink都是1.10老的要死，借此机会重新对于每个软件的版本记录一下


不行………… 工作量太大了很浪费时间…………
操作系统：Ubuntu 22.04
MySQL：5.7.41 UTF8MB4编码
JDK：8u351 1.8.0_351
Python:3.10.12
Pip:22.0.0
Mycat:1.6.7.6 在/export/server/mycat1下面 8066端口访问
    重点关注conf下面的schema.xml rule.xml server.xml

找到了宝藏软件zerotier 原理是把需要的电脑放到同一个局域网里面 给加入虚拟网卡 各自虚拟网卡的ip就在同一字段下
别管安全性了 我自己都快不安全了

现在有了小组合作的方法 我需要从更高维度看一下这个项目了
*================*
2025-12-5
我操今天终于明白了 我之前一直担心 我如果kafka加入数据了但是没有消费 后面不就有重叠的吗
他是这个原理：加入我测试输入了100条数据 消费群组id=1的假设消费了50条，那么属于它的offset的就是50
如果我正式上数据 还是用的这个主题的话 那么新的消费群组id=2会维护它自己的offset 并且从当前消息队列的最新开始读数据（101）开始

KafKa相关：
kafka-topics.sh --list --bootstrap-server node1:9092    查看有哪些主题
kafka-topics.sh --describe --bootstrap-server node1:9092 --topic etc_traffic_data   查看特定主题的分区和副本状态
kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc-traffic-data --from-beginning --max-messages 10 查看历史数据

查看有哪些消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --list
删除指定的消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --delete --group flink-hbase-group（消费者组名称）


删除主题kafka-topics.sh --delete --bootstrap-server node1:9092 --topic etc_traffic_data（topic名称）

创建主题： kafka-topics.sh --create --bootstrap-server node1:9092 --replication-factor 3 --partitions 3 --topic etc_traffic_data

以后主题都是这个 etc_traffic_data 方便测试

运行生产者之后
kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc_traffic_data --from-beginning
查看实时消息 先打开 先打开！！

kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc_traffic_data --from-beginning --max-messages 10
查看前十条消息而不是一直滚动 用来说明消息字段的

Kakfa2.4 flink1.10 hbase2.3 互相兼容

*==========*
设计row-key 今天刚讲别太长 我管他！
String reverseTs = String.valueOf(Long.MAX_VALUE - gcsjTs);
String rowkey = reverseTs + "-" + hphm + "-" + cleanKkmc + "-" + gcxh;
<reverse_ts>-<HPHM>-<CLEAN_KKMC>-<GCXH>
表示在这个点的这辆车经过了这个卡口加上唯一序号

我的Flink当时安装的版本很老了
mvn archetype:generate `
  -DarchetypeGroupId=org.apache.flink `
  -DarchetypeArtifactId=flink-quickstart-java `
  -DarchetypeVersion=1.10.0 `
  -DgroupId=flink.etctraffic `
  -DartifactId=FlinkKafkaToHBase `
  -Dversion=1.0-SNAPSHOT `
  -Dpackage=flink.etctraffic `
  -DinteractiveMode=false
尝试这个命令
创建项目之后 修改pom.xml
编写代码 现在没实现套牌检查还
写完之后打包mvn clean package -DskipTests
传Flink开头的jar包给node1

/export/server/flink/bin/stop-cluster.sh
/export/server/flink/bin/start-cluster.sh
启动flink standalon
flink run -m node1:8081 -c flink.etctraffic.KafkaToHBaseJob /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar

提交任务
flink run -d -m node1:8081 -c flink.etctraffic.KafkaToHBaseJob /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar
开启flink之后的测试


kafka-consumer-groups.sh --bootstrap-server node1:9092 --describe --group flink_hbase_group（固定叫这个消费者组）



hbase的测试
创建：create 'etc_traffic_data', 'info', {SPLITS => ['3','6','9','C','F']}
查看：describe 'etc_traffic_data'
删除: disable 'etc_traffic_data' drop 'etc_traffic_data'


人工智能他是个位置啊！ChatGPT现在还得练 Gemini真没毛！

现在flink可以读取数据 并且输出日志了，所以接下来实现输入到hbase和检测套牌车就好
总结一下每次测试的清理：
*===========================================*
首先列出消费者组
查看有哪些消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --list
删除指定的消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --delete --group flink_hbase_group（消费者组名称）

查看主题kafka-topics.sh --list --bootstrap-server node1:9092

删除主题kafka-topics.sh --delete --bootstrap-server node1:9092 --topic etc_traffic_data（topic名称）

创建主题： kafka-topics.sh --create --bootstrap-server node1:9092 --replication-factor 3 --partitions 3 --topic etc_traffic_data

以后主题都是这个 etc_traffic_data 方便测试

运行生产者之后
kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc_traffic_data --from-beginning
查看实时消息 先打开 先打开！！

web取消作业
再运行作业记得覆盖mvn clean package
flink run -d -m node1:8081 -c flink.etctraffic.KafkaToHBaseJob /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar
我的机器内存好像要炸了啊我操
现在先看日志端

ok连接上hbase了测试之后
truncate 'etc_traffic_data' 作用是删除内容 原理是先disable drop 再建立表 牛逼

*===================*
简单总结一下把，总算是有了点进展 2025-12-5
今天实现了kafka发送数据 Flink流计算 导入Hbase 整个操作
Flink的版本太老了 和Hbase很不协调 捣鼓了半天
其实主要想总结测试的流程，因为不想弄清楚原理就采用很暴力的方法了

每次打开电脑开始开发，第一件事启动三台虚拟机jps看看进程干不干净
还想吐槽的是，之前都是跟着视频配的各种软件，端口什么的都忘记了，目前一个重要的端口就是Hbase的8085端口，开放thrift给Flaskfangwen

括号里面表示，这个命令的其他用法，查看状态，或者停止
首先打开Zookeeper，端口2181：
    zkServer.sh start（status stop）
然后打开kafka，后台启动：
    kafka-server-start.sh -daemon $KAFKA_HOME/config/server.properties（后台启动方式）
node1节点开启大数据集群：
    start-dfs.sh 
    start-yarn.sh 
node1打开Hbase，必须要先开HDFS再开Hbase，有次忘记了差点没把我搞死
    start-hbase.sh 
开启thrift端口
    hbase-daemon.sh start thrift -p 8085
现在flink走起来了，所以也要开启flink，这个应该是Standalone模式，我没用YARN
当然了，我没配环境变量，要写全部的路径
    /export/server/flink/bin/stop-cluster.sh
    /export/server/flink/bin/start-cluster.sh

然后打开Hbase shell，命令是hbase shell
list输入有哪些表 统一用'etc_traffic_data'
每次重新跑实验，就用
    truncate 'etc_traffic_data' 
作用是删除内容 原理是先disable drop 再建立表 牛逼
查看表的最上面一条：
scan 'etc_traffic_data', {LIMIT=>1, FORMATTER=>'toString'}


kafka重点关注消息主题和消费者组
主题如果不卡的话 统一用'etc_traffic_data'
消费者组是由代码搞的 统一用'flink_hbase_group'
查看主题
kafka-topics.sh --list --bootstrap-server node1:9092
删除主题
kafka-topics.sh --delete --bootstrap-server node1:9092 --topic etc_traffic_data（topic名称）
创建主题
kafka-topics.sh --create --bootstrap-server node1:9092 --replication-factor 3 --partitions 3 --topic etc_traffic_data
查看有哪些消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --list
删除指定的消费者组
kafka-consumer-groups.sh --bootstrap-server node1:9092 --delete --group flink_hbase_group（消费者组名称）

kafka-consumer-groups.sh --bootstrap-server node1:9092 --delete --group flink_traffic_analysis_group_v2

每次测试完，首先删除消费者组，然后删除主题，再新建主题，哈哈
测试的时候要新打开一个页面监听主题消息情况
kafka-console-consumer.sh --bootstrap-server node1:9092 --topic etc_traffic_data --from-beginning


Flink任务首先cmd到FlinkKaffaToHBase目录，修改代码之后
mvn clean package
重新生成tar包，覆盖/export/code目录下面的就可以
flink run -d -m node1:8081 -c flink.etctraffic.KafkaToHBaseJob /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar

加入了套牌车的命令
flink run -d -m node1:8081 -c flink.etctraffic.StreamAnalysisJob /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar

加入流量预测的命令
flink run -d -m node1:8081 -c flink.etctraffic.StreamAnalysisJobV2 /export/code/FlinkKafkaToHBase-1.0-SNAPSHOT.jar
给集群提交任务
可以通过Web看集群情况，url是node1:8081

实验做完之后目前的停止指令：
kafka-server-stop.sh 
hbase-daemon.sh stop thrift 
stop-hbase.sh 
stop-yarn.sh 
stop-dfs.sh 
zkServer.sh stop
可以先关flink再一个个停止
/export/server/flink/bin/stop-cluster.sh
*===============================================*

前端:Vue Vue Element
后端:Flask SpringBoot
数据库：HBase MySQL Mycat


*==========================================*
2025-12-6 今天开始Redis Remote Dictionary Server 远程词典服务
内存数据库 NoSQL 读取速度快
基于此 开发Flink套牌车检测和18个站点的分钟流量统计
redis-3.2.12-2.el7.x86_64
默认安装在/usr/local/bin目录下面
自己给我配好了环境变量 不错不错

启动：redis-server

redis-server redis.conf 在安装目录/export/server/redis-6.2.6目录下面以配置文件设置启动

端口：6379 版本6.2.6
密码：050214@Redis

Redis的key 项目名:业务名:类型:id
Hash key field value

*==========================*
套牌车：Flink的State机制 keyBy(车牌号) 按照车牌号开辟独立存储空间
针对套牌车检测，我们使用 keyBy(车牌号)。
一旦进行了 keyBy，Flink 就会为每一个车牌号在内存（或 RocksDB）中开辟一块独立的存储空间。

当 苏C12345 的第 1 条数据进来时，Flink 把它存到 苏C12345 的状态空间 里。
当 苏C88888 的数据进来时，Flink 把它存到 苏C88888 的状态空间 里，互不干扰。
当 苏C12345 的第 2 条数据进来时，Flink 会自动去 苏C12345 的状态空间 里把第 1 条数据拿出来，和第 2 条做对比。
这就是 Flink 实现套牌车检测的底层原理：基于 Key 的状态管理。

根据上面的特性 有了一个初步的检测方案
对于每次读取的同一车牌的两个状态 根据车牌keyby
然后计算两个状态之间的差值 如果小于10分钟（我们假设 十分钟之内不可能从任意一个卡口到达另一个卡口）
就认为这辆车是套牌车 把车牌号存入Redis
实际上如果更专业一点，可以继续把这个信息存入Hbase持久化存储
不过我们这里没有搞

接下来就是流量预测 继续分析一下
*===============================*
回顾一下我们这个时间戳是怎么来的：
1701388801000 是 Unix 时间戳（毫秒）。它是计算机世界通用的时间语言。

1. 它是怎么来的？
它的定义是：从 1970年1月1日 00:00:00 UTC 到现在的总毫秒数。

对于北京时间 2023/12/1 00:00:01：

北京时间：2023-12-01 00:00:01
UTC 时间：2023-11-30 16:00:01 (北京是东八区，减8小时)
计算：从 1970年 到 2023-11-30 16:00:01 经过了 1701388801 秒。
毫秒：乘以 1000 -> 1701388801000。

重大乌龙：时间戳你妈逼搞错了被坑了
原始数据都是从0点开始的 比如2023-12-1 00.00.03 问题是 这个零点是北京时间 还是UTC格林威治时间？？？？？？？？？

一开始的生成时间戳的逻辑 根本没有管这个，直接把

左边是格林威治时间 右边是北京时间 所以其实右边的才是正确的妈的
但是我的数据里面都是左边的 所以现在修改flink把他减去八个小时
1701388801000 / 1701360001000


Done: Unpacking the User's Queries
这是一个非常经典且容易绕晕的概念。别急，我用最通俗的例子给你讲清楚。

1. 什么是“Unix 时间戳”？
Unix 时间戳是一个绝对值，它不分时区。
它代表：从 1970年1月1日 00:00:00 (UTC 格林威治时间) 到现在的总秒数。

你可以把它想象成一个全球统一的秒表，从那一刻开始一直在走，全世界任何地方看到的这个秒表读数都是一样的。

2. 为什么你会觉得“时间戳分时区”？
因为转换的过程分时区。

假设你的 CSV 里写着：2023-12-01 00:00:01。
这只是一个字符串，没有贴“时区标签”。

情况 A（正确做法）：
你告诉计算机：“这是北京时间的 00:00:01。”
计算机心里想：北京时间 00:00:01 = UTC 时间 昨天 16:00:01。
于是它算出秒表读数：1701360001。

情况 B（你遇到的错误做法）：
生成数据的程序告诉计算机：“这是UTC 时间的 00:00:01。”
计算机心里想：哦，就是 UTC 00:00:01。
于是它算出秒表读数：1701388801。

看到了吗？
同一个字符串 00:00:01，因为你告诉计算机的“时区前提”不同，算出来的“秒表读数（时间戳）”就差了 28800 秒（8小时）。

3. 你的数据应该怎么转？
既然你的 CSV 里的 2023-12-01 00:00:01 代表的是北京时间，那么正确的转换逻辑应该是：

拿到字符串 2023-12-01 00:00:01。
明确告诉转换函数：“这是 Asia/Shanghai 时区”。
函数会自动把这个时间减去 8 小时，换算成 UTC 时间。
最后生成时间戳。

直接修改源文件

今天实现了区间流量统计 把vue接入了交互式查询的接口 方法很暴力 把streamlit生成的网页直接作为一个路由路由进去