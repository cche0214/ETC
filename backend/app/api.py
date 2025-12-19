from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud
from app.schemas import (
    SessionCreate,
    SessionResponse,
    MessageResponse,
    MessageCreate,
    SessionUpdate
)

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

@router.get("sessions/{session_id}", response_model=SessionResponse)
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
@router.put("/sessions/{sessions_id}", response_model=SessionResponse)
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

@router.patch("/sessions/{session_id}",response_model=SessionResponse)
async def patch_session(
    session_id: str,
    update_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """部分更新会话信息（Patch方法）"""
    session = crud.get_sission(db, session_id)
    if not session:
        raise HTTPException(status_code=404,detail='Session not found')
    
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

@router.get("/sessions/{seesion_id}/messages",response_model=List[MessageResponse])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取会话的所有消息"""
    messages = crud.get_messages(db, session_id)
    return messages
