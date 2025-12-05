import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# ======== 初始化模型 ========
model = init_chat_model(
    model="deepseek:deepseek-chat",
    temperature=0.1
)

# ======== MySQL 连接（node1） ========
node1_ip = "192.168.88.131"   # <<< 这里改成你的 node1 IP
mysql_port = 3306             # <<< 如果你改过端口，这里也要改

password = urllib.parse.quote("050214@Mysql")

db = SQLDatabase.from_uri(
    f"mysql+mysqlconnector://root:{password}@{node1_ip}:{mysql_port}/traffic"
)

# ======== 工具包 ========
toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

# ======== Prompt ========
system_prompt = f"""
你是一个 SQL 数据分析智能体，使用语言模型生成 SQL 查询并分析结果。

数据库方言：{db.dialect}

严格规则：
1. 必须生成语法正确的 SQL。
2. 必须只读，不允许执行 INSERT、DELETE、UPDATE、DROP。
3. 查询最多返回 5 行 unless 用户要求更多。
4. SQL 出错必须重新生成。
5. 回答必须包含中文解释。
6. 你是中国矿业大学大数据存储实验开发的专用交互式查询助手。

"""

# ======== 创建 Agent ========
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)

# ======== Streamlit UI ========
st.title("🚦交通数据 AI 分析系统")
st.write("输入一个数据库问题，AI 将自动生成 SQL 并给出分析结果。")

user_input = st.text_input("请输入问题：", "")

if st.button("提交"):
    if user_input.strip() == "":
        st.warning("请输入问题！")
    else:
        st.write("分析中")

        # 流式输出
        for step in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            stream_mode="values",
        ):
            msg = step["messages"][-1].content
            st.write(msg)

        st.success("✅ 完成！")
