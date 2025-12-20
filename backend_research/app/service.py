from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma 
from langchain_community.embeddings import OllamaEmbeddings
from pathlib import Path
from app.config import settings
from typing import List, Dict, AsyncGenerator
import json
import os

def _handle_error(error) -> str:
    """
    容错处理：如果 LLM 的输出无法被解析（例如缺少 Final Answer 前缀），
    则尝试提取其原始输出作为回答。
    """
    error_str = str(error)
    # LangChain 的 OutputParserException 通常包含原始输出
    if "Could not parse LLM output:" in error_str:
        # 分割获取原始输出
        content = error_str.split("Could not parse LLM output:")[-1]
        
        # 移除 LangChain 自动附加的 Troubleshooting 信息
        if "For troubleshooting, visit:" in content:
            content = content.split("For troubleshooting, visit:")[0]
            
        return content.strip(" `")
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
        
        # 3. 初始化 RAG 向量数据库连接
        # 必须与 ingest.py 中的 embedding 模型一致
        self.embeddings = OllamaEmbeddings(
            model="qwen3-embedding:4b" 
        )
        
        # 修复路径逻辑：
        # 当前文件: .../ETC/backend_research/app/service.py
        # parents[0]: app
        # parents[1]: backend_research
        # parents[2]: ETC (项目根目录)
        # 目标路径: .../ETC/RAG/store/chroma_db
        
        current_file = Path(__file__).resolve()
        project_root = current_file.parents[2] # 应该是 ETC 目录
        rag_db_path = project_root / "RAG" / "store" / "chroma_db"
        
        print(f"DEBUG: RAG DB Path computed as: {rag_db_path}")
        print(f"DEBUG: Path exists? {rag_db_path.exists()}")
        
        if not rag_db_path.exists():
            print("WARNING: Vector DB path does not exist! RAG will fail.")

        self.vector_store = Chroma(
            persist_directory=str(rag_db_path),
            embedding_function=self.embeddings
        )
        # 创建检索器，检索最相关的 3 个文档片段
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        
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
8. 最终回答必须以 "Final Answer:" 开头。
9. **重要：请将所有的数据分析、现象解释和结论都放在 "Final Answer:" 之后输出。不要在 Final Answer 之前进行长篇大论的分析，否则这部分内容会被截断。**
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

    async def _check_intent(self, user_input: str) -> str:
        """
        意图识别：判断用户问题是属于 'sql', 'rag' 还是 'chat'
        """
        prompt = f"""
你是一个意图识别助手。请判断以下用户问题的意图。

规则：
1. sql: 如果问题涉及到具体的车流量统计、ETC记录查询、车辆信息、道路拥堵情况等需要查询业务数据库的问题（例如“昨天流量多少”、“查苏Cxxxxx的轨迹”）。
2. rag: 如果问题涉及到系统架构、技术实现、项目背景、部署运维、数据库设计、Flink流计算逻辑等项目本身的知识（例如“Flink怎么检测套牌车”、“数据库怎么分表的”、“Redis用来干什么”）。
3. chat: 如果问题是打招呼、自我介绍、通用知识询问，或者与上述两者无关。

用户问题: "{user_input}"

只返回一个单词：sql, rag, 或 chat
"""
        try:
            # 使用 invoke 而不是 astream，因为我们需要完整的判断结果
            response = await self.llm.ainvoke(prompt)
            intent = response.content.strip().lower()
            # 简单的后处理，防止模型返回多余标点
            if 'sql' in intent: return 'sql'
            if 'rag' in intent: return 'rag' 
            return 'chat'
        except Exception:
            # 如果判断出错，默认回退到 chat 模式，或者保守点回退到 sql
            return 'chat'

    async def astream_chat(self, user_input: str, chat_history: List[Dict] = []) -> AsyncGenerator[Dict, None]:
        """
        异步流式对话
        :param user_input: 当前用户问题
        :param chat_history: 历史对话列表 [{'role': 'user', 'content': '...'}, ...]
        :return: 生成字典流 {'type': 'thought'|'message'|'error', 'content': '...'}
        """
        try:
            # 1. 意图识别
            intent = await self._check_intent(user_input)
            
            # 2. 根据意图分流
            if intent == 'sql':
                # === 分支 A: SQL 数据查询 ===
                yield {"type": "thought", "content": "🤔 识别为数据查询请求，正在启动 SQL 引擎..."}
                
                agent_executor = self.create_agent_executor()
                
                # 简单拼接历史记录作为上下文
                context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-6:]]) 
                full_prompt = f"参考历史对话:\n{context_str}\n\n当前问题: {user_input}" if context_str else user_input
                
                async for chunk in agent_executor.astream(
                    {"input": full_prompt},
                ):
                    if "actions" in chunk:
                        for action in chunk["actions"]:
                            yield {"type": "thought", "content": f"🤖 正在思考: 查询数据库 ({action.tool})..."}
                            
                    if "steps" in chunk:
                         yield {"type": "thought", "content": "📊 查询完成: 正在分析结果..."}

                    if "output" in chunk:
                        yield {"type": "message", "content": chunk["output"]}
            
            elif intent == 'rag':
                # === 分支 B: RAG 知识库问答 (新增) ===
                yield {"type": "thought", "content": "📚 识别为项目知识问答，正在检索知识库..."}
                
                try:
                    # 1. 检索
                    # 这里会调用 Ollama 进行 embedding，可能会稍微慢一点点，视你机器性能而定
                    docs = await self.retriever.ainvoke(user_input)
                    if not docs:
                        yield {"type": "message", "content": "抱歉，知识库中没有找到相关信息。"}
                        return
                        
                    # 2. 增强 (Augment)
                    context_str = "\n\n".join([f"---片段 {i+1}---\n{doc.page_content}" for i, doc in enumerate(docs)])
                    
                    yield {"type": "thought", "content": f"📖 已找到 {len(docs)} 份相关文档，正在生成回答..."}
                    
                    # 3. 生成 (Generate)
                    rag_prompt = f"""
你是一个专业的项目技术顾问。请基于以下检索到的项目文档片段，回答用户的问题。
如果文档中没有相关信息，请诚实回答“我不知道”。不要编造信息。

相关文档片段：
{context_str}

用户问题: {user_input}
"""
                    messages = [{"role": "user", "content": rag_prompt}]
                    
                    async for chunk in self.llm.astream(messages):
                        if chunk.content:
                            yield {"type": "message", "content": chunk.content}
                            
                except Exception as e:
                     yield {"type": "error", "content": f"检索失败: {str(e)}"}

            else:
                # === 分支 C: 普通闲聊 ===
                # 直接调用 LLM，不走 Agent 流程
                yield {"type": "thought", "content": "💬 识别为通用对话..."}
                
                # 构建简单的对话 Prompt
                chat_system_message = """你是中国矿业大学大数据存储实验开发的专用交互式查询助手。
你的核心架构基于“智能路由 (Intent Router)”技术，能够自动判断用户需求并调用不同引擎：

1. 📊 **SQL 数据分析引擎**：当您询问具体的业务数据（如“查询昨天G3高速的车流量”、“苏C12345的行驶轨迹”）时，我会自动生成 SQL 查询 MySQL 数据库。
2. 🧠 **RAG 知识检索引擎**：当您询问项目本身的技术细节（如“数据库是如何分库分表的？”、“Flink怎么检测套牌车？”）时，我会从本地知识库中检索开发文档。
3. 💬 **通用对话引擎**：处理日常问候和自我介绍。

请友好、简洁地回答。当被问及功能时，请自信地介绍你的这三大能力。"""

                messages = [
                    {"role": "system", "content": chat_system_message},
                ]
                # 添加历史记录
                for msg in chat_history[-6:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
                messages.append({"role": "user", "content": user_input})

                async for chunk in self.llm.astream(messages):
                    if chunk.content:
                        yield {"type": "message", "content": chunk.content}
                    
        except Exception as e:
            yield {"type": "error", "content": f"❌ 发生错误: {str(e)}"}

# 单例模式
traffic_agent_service = TrafficAgentService()
