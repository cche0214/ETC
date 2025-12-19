from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

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
