import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..models.schemas import ConversationCreate, ConversationResponse
from ..services.firestore_service import (
    get_all_conversations,
    get_conversation,
    save_conversation,
    delete_conversation
)

router = APIRouter(prefix="/api/conversations", tags=["Conversations (대화 기록)"])

@router.get("", response_model=List[ConversationResponse], summary="대화 목록 조회")
def list_conversations():
    """저장된 전체 대화 세션 목록을 조회합니다."""
    return get_all_conversations()

@router.get("/{id}", response_model=ConversationResponse, summary="특정 대화 전체 메시지 조회 (대화 불러오기 UX)")
def get_single_conversation(id: str):
    """선택한 대화의 전체 메시지 이력을 조회하여 화면에 재표시할 수 있도록 합니다."""
    conv = get_conversation(id)
    if not conv:
        raise HTTPException(status_code=404, detail="해당 대화 세션을 찾을 수 없습니다.")
    return conv

@router.post("", response_model=ConversationResponse, status_code=201, summary="새 대화 세션 저장")
def create_conversation(payload: ConversationCreate):
    """신규 대화 세션을 수동으로 생성 또는 저장합니다."""
    now_iso = datetime.utcnow().isoformat()
    new_conv = {
        "id": f"conv_{uuid.uuid4().hex[:8]}",
        "title": payload.title,
        "topic": payload.topic,
        "messages": [m.model_dump() for m in payload.messages],
        "created_at": now_iso,
        "updated_at": now_iso
    }
    saved = save_conversation(new_conv)
    return saved

@router.delete("/{id}", summary="대화 세션 삭제")
def delete_single_conversation(id: str):
    """대화 세션을 삭제합니다."""
    success = delete_conversation(id)
    if not success:
        raise HTTPException(status_code=404, detail="해당 대화 세션을 찾을 수 없습니다.")
    return {"status": "success", "message": f"대화 세션 {id}가 성공적으로 삭제되었습니다."}
