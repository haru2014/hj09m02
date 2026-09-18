import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse, ChatMessage
from ..services.firestore_service import (
    get_all_data,
    get_all_papers,
    get_conversation,
    save_conversation
)
from ..services.analytics_service import compute_data_summary
from ..services.ai_service import generate_ai_response
from ..data.seed_data import match_topic_from_query

router = APIRouter(prefix="/api/chat", tags=["AI Chat (Context Injection)"])

@router.post("", response_model=ChatResponse, summary="AI 대화 API (데이터 요약 컨텍스트 주입 및 자동 저장)")
async def chat_endpoint(payload: ChatRequest):
    """
    데이터 기반 AI 채팅 엔드포인트:
    1. 질문 키워드 기반 연구 주제 판별
    2. 시계열 데이터 요약 계산 (/api/data/summary)
    3. 요약 및 논문 데이터를 시스템 프롬프트에 컨텍스트로 주입
    4. GPT 응답 생성
    5. 대화 세션을 conversations 컬렉션에 자동 저장
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")

    # 1. Topic detection
    matched_topic = payload.topic
    if not matched_topic or matched_topic == "전체":
        matched_topic = match_topic_from_query(payload.message)

    # 2. Get data & compute summary
    topic_data = get_all_data(topic=matched_topic)
    summary = compute_data_summary(topic_data, topic_filter=matched_topic)

    # Fetch relevant papers
    papers = get_all_papers(topic=matched_topic)

    # 3. Retrieve chat history if continuing conversation
    chat_history = []
    conv_id = payload.conversation_id
    existing_conv = None

    if conv_id:
        existing_conv = get_conversation(conv_id)
        if existing_conv:
            chat_history = existing_conv.get("messages", [])

    # 4. Generate AI response (Context injected)
    now_iso = datetime.utcnow().isoformat()
    ai_result = await generate_ai_response(
        message=payload.message,
        topic=matched_topic,
        summary=summary,
        papers=papers,
        chat_history=chat_history
    )

    clean_user_content = payload.message.encode("utf-8", "replace").decode("utf-8")
    clean_ai_content = ai_result["reply"].encode("utf-8", "replace").decode("utf-8")

    user_msg = ChatMessage(role="user", content=clean_user_content, timestamp=now_iso)
    ai_msg = ChatMessage(role="assistant", content=clean_ai_content, timestamp=datetime.utcnow().isoformat())

    # 5. Save conversation (Auto-save)
    if not conv_id or not existing_conv:
        conv_id = f"conv_{uuid.uuid4().hex[:8]}"
        title_raw = clean_user_content[:25] + ("..." if len(clean_user_content) > 25 else "")
        title = title_raw.encode("utf-8", "replace").decode("utf-8")
        new_conv = {
            "id": conv_id,
            "title": title,
            "topic": matched_topic,
            "messages": [user_msg.model_dump(), ai_msg.model_dump()],
            "created_at": now_iso,
            "updated_at": now_iso
        }
        save_conversation(new_conv)
    else:
        existing_conv["messages"].append(user_msg.model_dump())
        existing_conv["messages"].append(ai_msg.model_dump())
        existing_conv["updated_at"] = now_iso
        save_conversation(existing_conv)

    return ChatResponse(
        conversation_id=conv_id,
        reply=ai_result["reply"],
        summary_used=summary,
        engine_used=ai_result.get("engine_used", "gemini"),
        suggested_topics=ai_result["suggested_topics"],
        related_papers=ai_result["related_papers"]
    )
