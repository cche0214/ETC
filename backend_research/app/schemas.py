from graphlib import TopologicalSorter
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic_core.core_schema import str_schema

# 消息基类
class MessageBase(BaseModel):
    role: str
    content: str
    session_id: str

    # 允许从ORM实例（SQLAlchemy模型）创建Pydantic模型
    model_config = ConfigDict(from_attributes=True)

# 消息创建请求
class MessageCreate(MessageBase):
    pass

# 消息响应
class MessageResponse(MessageBase):
    id: str
    created_at: datetime

class SessionBase(BaseModel):
    title: Optional[str] = "新对话"

    # 允许从ORM实例创建
    model_config = ConfigDict(from_attributes=True)

# 会话创建请求
class SessionCreate(SessionBase):
    pass

# 会话更新请求
class SessionUpdate(SessionBase):
    pass

# 会话响应
class SessionResponse(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

# 聊天请求 - 修改字段名以匹配 api.py 和前端
class ChatRequest(BaseModel):
    content: str
    session_id: Optional[str] = None
    stream: Optional[bool] = False

# 聊天响应
class ChatResponse(BaseModel):
    session_id: str
    message: MessageResponse
    is_complete: bool = True

# 流式响应块
class ChatStreamChunk(BaseModel):
    content: str
    is_final: bool = False
    tool_calls: Optional[List[Dict[str, Any]]] = None
