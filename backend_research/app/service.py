from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings
from typing import List, Dict, AsyncGenerator
import json

def _handle_error(error) -> str:
    """
    容错处理：如果 LLM 的输出无法被解析（例如缺少 Final Answer 前缀），
    则尝试提取其原始输出作为回答。
    """
    error_str = str(error)
    # LangChain 的 OutputParserException 通常包含原始输出
    if "Could not parse LLM output:" in error_str:
        return error_str.split("Could not parse LLM output:")[-1].strip(" `")
    return f"抱歉，处理结果时出现错误: {error_str}"

class TrafficAgentService:
    def __init__(self):
        # 1. 初始化 LLM (DeepSeek 兼容 OpenAI 协议)
        self.llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            temperature=0.1,  # SQL 生成需要低温度
            streaming=True    # 开启流式
        )
        
        # 2. 初始化数据库连接
        # 使用 lazy loading 防止启动时连接失败导致整个应用崩溃
        self._db = None
        
        # 4. 系统提示词 (System Prompt) - 复用 ui.py 中的提示词并加以完善
        self.system_message = """你是一个 SQL 数据分析智能体，使用语言模型生成 SQL 查询并分析结果。
数据库方言: MySQL

严格规则：
1. 必须生成语法正确的 SQL。
2. 必须只读，不允许执行 INSERT、DELETE、UPDATE、DROP。
3. 查询最多返回 5 行 unless 用户要求更多。
4. SQL 出错必须重新生成。
5. 回答必须包含中文解释。
6. 你是中国矿业大学大数据存储实验开发的专用交互式查询助手。
7. 分析结果时，请结合上下文，给出有见地的结论。
"""

    @property
    def db(self):
        if self._db is None:
            self._db = SQLDatabase.from_uri(settings.SQLALCHEMY_TRAFFIC_DATABASE_URI)
        return self._db

    def create_agent_executor(self):
        """
        创建并返回一个 Agent 执行器
        """
        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        
        # 使用 agent_executor_kwargs 传递错误处理函数
        return create_sql_agent(
            llm=self.llm,
            toolkit=toolkit,
            agent_type="zero-shot-react-description", 
            verbose=True,
            prefix=self.system_message,
            top_k=5,
            agent_executor_kwargs={"handle_parsing_errors": _handle_error}
        )

    async def astream_chat(self, user_input: str, chat_history: List[Dict] = []) -> AsyncGenerator[Dict, None]:
        """
        异步流式对话
        :param user_input: 当前用户问题
        :param chat_history: 历史对话列表 [{'role': 'user', 'content': '...'}, ...]
        :return: 生成字典流 {'type': 'thought'|'message'|'error', 'content': '...'}
        """
        try:
            agent_executor = self.create_agent_executor()
            
            # 简单拼接历史记录作为上下文
            context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]]) # 取最近3轮
            full_prompt = f"参考历史对话:\n{context_str}\n\n当前问题: {user_input}" if context_str else user_input
            
            # 执行流式生成
            async for chunk in agent_executor.astream(
                {"input": full_prompt},
            ):
                # 处理不同类型的 chunk
                if "actions" in chunk:
                    for action in chunk["actions"]:
                        yield {"type": "thought", "content": f"🤖 正在思考: 查询数据库 ({action.tool})..."}
                        
                if "steps" in chunk:
                     yield {"type": "thought", "content": "📊 查询完成: 正在分析结果..."}

                if "output" in chunk:
                    yield {"type": "message", "content": chunk["output"]}
                    
        except Exception as e:
            yield {"type": "error", "content": f"❌ 发生错误: {str(e)}"}

# 单例模式
traffic_agent_service = TrafficAgentService()
