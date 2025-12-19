from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio

from app.database import get_db
from app import crud
from app.schemas import (
    SessionCreate,
    SessionResponse,
    MessageResponse,
    MessageCreate,
    SessionUpdate,
    ChatRequest
)
from app.service import traffic_agent_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

# post => create
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """创建新的聊天会话"""
    session = crud.create_session(db, session_data)
    return session

@router.get("/sessions", response_model=List[SessionResponse])
async def get_sessions(
    db: Session = Depends(get_db)
):
    """获取所有聊天会话"""
    sessions = crud.get_sessions(db)
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取特定会话"""
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 获取会话消息
    messages = crud.get_messages(db, session_id)
    session.messages = messages

    return session

# put => update
@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """更新会话消息"""
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_session = crud.update_session(db, session_id, update_data)
    if not update_session:
        raise HTTPException(status_code=500, detail="Failed to update session")
    
    messages = crud.get_messages(db, session_id)
    update_session.messages = messages
    
    return update_session

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """删除会话"""
    success = crud.delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not delete")
    return {"message": "Session deleted"}

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取会话的所有消息"""
    messages = crud.get_messages(db, session_id)
    return messages

# ==================== 消息处理 ===================

@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    流式发送消息 (适配前端调用)
    前端会 POST 到这个接口，我们返回 StreamingResponse (SSE 格式)
    """
    # 1. 验证会话
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 2. 保存用户消息
    crud.create_message(db, MessageCreate(
        role="user",
        content=chat_request.content, # 前端传的是 content
        session_id=session_id
    ))
    
    # 3. 获取历史消息 (用于构建上下文)
    history_msgs = crud.get_messages(db, session_id)
    # 排除刚刚插入的这条
    history_context = [
        {"role": m.role, "content": m.content} 
        for m in history_msgs[:-1] 
    ]

    # 4. 定义生成器
    async def event_generator():
        full_response = ""
        try:
            # 调用 Agent 服务
            async for chunk_dict in traffic_agent_service.astream_chat(
                user_input=chat_request.content,
                chat_history=history_context
            ):
                # chunk_dict 是 {'type': '...', 'content': '...'}
                if chunk_dict['type'] == 'message':
                    full_response += chunk_dict['content']
                
                # 构造 SSE 格式
                # data: {"type": "thought", "content": "..."}
                yield f"data: {json.dumps(chunk_dict, ensure_ascii=False)}\n\n"
            
            # 5. 对话结束，保存 AI 回复到数据库
            # 注意：只有在没有错误且有回复内容时才保存
            if full_response:
                crud.create_message(db, MessageCreate(
                    role="assistant",
                    content=full_response,
                    session_id=session_id
                ))
            
            # 发送结束标记
            yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_data = {"type": "error", "content": f"系统错误: {str(e)}"}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream" 
    )
