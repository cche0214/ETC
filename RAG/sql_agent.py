from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import AgentExecutor, ZeroShotAgent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import urllib.parse
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载 .env (复用 RAG 的 .env)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ======== 初始化模型 ========
# 使用与 RAG 相同的 DeepSeek 配置
model = init_chat_model(
    model="deepseek:deepseek-chat",
    temperature=0.1,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

# ======== MySQL 连接（ShardingSphere Proxy） ========
# 建议后续将这些硬编码移至 config.py 或环境变量
PROXY_IP = "192.168.88.131"
PROXY_PORT = 3307
PROXY_USER = "traffic"
PROXY_PASSWORD = "050214@Proxy"

encoded_password = urllib.parse.quote(PROXY_PASSWORD)

try:
    db = SQLDatabase.from_uri(
        f"mysql+mysqlconnector://{PROXY_USER}:{encoded_password}@{PROXY_IP}:{PROXY_PORT}/traffic"
    )
    print("✅ SQL Agent: Database connected successfully.")
except Exception as e:
    print(f"❌ SQL Agent: Database connection failed: {e}")
    db = None

# ======== 工具包与 Agent 初始化 ========
agent_executor = None

if db:
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()

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

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])
    agent = ZeroShotAgent.from_llm_and_tools(
        llm=model,
        tools=tools,
        prompt=prompt,
    )
    agent_executor = agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

def run_sql_agent(question: str):
    """
    运行 SQL Agent 处理问题
    """
    if not agent_executor:
        return "抱歉，数据库连接失败，无法执行 SQL 查询。"
    
    try:
        result = agent_executor.invoke({"input": question})
        return result["output"]
    except Exception as e:
        return f"SQL 分析出错: {str(e)}"
