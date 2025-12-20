# 03_后端架构 (Backend Architecture)

## 1. 服务概览
后端架构经历了从传统的 Flask MVC 模式向基于 FastAPI 的 AI Agent 模式的演进，目前共存或过渡中。

### 1.1 核心服务 (`backend_research`)
这是目前 AI Agent 的主要载体，基于 FastAPI 构建。
*   **路径**：`backend_research/app/`
*   **启动命令**：`uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload`
*   **主要依赖**：`FastAPI`, `SQLAlchemy`, `LangChain`, `Uvicorn`.

### 1.2 传统服务 (`backend`)
早期的业务后端，主要用于简单的 CRUD 和对接 HBase。
*   **路径**：`backend/app/`
*   **框架**：Flask
*   **主要职责**：提供给大屏的固定数据接口，直接读取 HBase 或 Redis。

## 2. 核心模块详解 (`backend_research`)

### 2.1 API 层 (`api.py`)
提供 RESTful 接口，处理 HTTP 请求。
*   `POST /api/chat/sessions`：创建会话。
*   `POST /api/chat/sessions/{id}/messages`：发送消息（核心交互接口，支持 SSE 流式返回）。
*   `GET /sessions`：获取历史会话列表。

### 2.2 业务逻辑层 (`service.py`)
核心 Agent 逻辑所在地。
*   **TrafficAgentService 类**：
    *   **Intent Recognition (Router)**：`_check_intent` 方法，区分 `sql` (查库)、`chat` (闲聊) 和 `rag` (检索)。
    *   **SQL Agent**：基于 `LangChain` 的 `create_sql_agent`，利用 `SQLDatabaseToolkit` 操作 MySQL。
    *   **LLM**：配置了 `ChatOpenAI` 客户端连接 DeepSeek API。
    *   **System Prompt**：定义了严格的 SQL 生成规则（MySQL 方言、只读权限、中文解释）。

### 2.3 数据访问层 (`crud.py`, `database.py`)
*   使用 `SQLAlchemy` ORM 管理会话历史 (`Session`, `Message` 模型)。
*   注意：Agent 查询的 **业务数据** (MySQL) 和存储聊天记录的 **应用数据** (SQLite/MySQL) 可能是分离的。Agent 通过 `SQLDatabase.from_uri` 连接业务库。

### 2.4 模型层 (`models.py`, `schemas.py`)
*   **Pydantic Schemas**：用于 API 输入输出校验 (`ChatRequest`, `SessionResponse`).
*   **SQLAlchemy Models**：定义聊天记录的表结构。

## 3. 预测与分析模块
*   **路径**：`backend/prediction/`
*   **模型**：LSTM 模型 (`.h5` 文件)，用于车流量预测。
*   **逻辑**：读取 Redis 中的历史流量数据（滑动窗口，如过去9个时间步），预测未来流量。

## 4. 接口规范
*   **通信协议**：HTTP/1.1 (常规请求), SSE (流式对话).
*   **数据格式**：JSON.
*   **错误处理**：统一的异常捕获与 HTTP 状态码返回，Agent 层有专门的 OutputParser 容错机制。

