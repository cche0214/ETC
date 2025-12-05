from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

# =============== 1. 初始化模型 ===============
model = init_chat_model(
    model="deepseek:deepseek-chat",
    temperature=0.1
)

# =============== 2. 连接 MySQL ===============
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(
    "mysql+mysqlconnector://root:asd1234569kj%40@localhost:3306/traffic"
)

print(f"数据库类型: {db.dialect}")
print(f"数据表: {db.get_usable_table_names()}")

# =============== 3. 创建 SQL 工具包 ===============
from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=model)

tools = toolkit.get_tools()
for tool in tools:
    print(f"可用工具：{tool.name}: {tool.description}")

# =============== 4. 定义 SQL Prompt（照抄官方示例） ===============
system_prompt = f"""
你是一个 SQL 数据分析智能体，使用语言模型生成 SQL 查询并分析结果。

数据库方言：{db.dialect}

规则：
1. 必须生成语法正确的 SQL 查询。
3. 不要查询所有列，只查必要列。
4. 不允许执行 INSERT / UPDATE / DELETE / DROP。
5. 如果 SQL 执行出错，你需要重新写一个。
6. 提问时，先了解有哪些表，再推断用哪个字段。

你的最终任务是：给出问题的正确 SQL，并根据结果给出中文答案。
"""

# =============== 5. 构建智能体（与示例完全一致） ===============
from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)

# =============== 6. 执行你的问题 ===============
question = "12月一个月内经过的车辆中，号牌是沃尔沃牌类型的有多少辆？"

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
