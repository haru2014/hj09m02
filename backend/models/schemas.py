from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ==========================================
# Data Item Schemas (CRUD)
# ==========================================

class DataItemBase(BaseModel):
    date: str = Field(..., description="데이터 일자 (YYYY-MM-DD 또는 YYYY)", example="2024-01-01")
    value: float = Field(..., description="측정치 (논문 수, 연구 지수 등)", example=47.0)
    memo: str = Field(..., description="메모 또는 연구 키워드/특이사항", example="AI 보행 분석 및 웨어러블 센서 연구 증가")
    topic: str = Field(default="관절", description="연구 분야 대분류", example="관절")

class DataItemCreate(DataItemBase):
    pass

class DataItemUpdate(BaseModel):
    date: Optional[str] = None
    value: Optional[float] = None
    memo: Optional[str] = None
    topic: Optional[str] = None

class DataItemResponse(DataItemBase):
    id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ==========================================
# Data Summary Schemas (Context Injection)
# ==========================================

class SummaryMetrics(BaseModel):
    total: float
    average: float
    max: float
    min: float

class DataSummaryResponse(BaseModel):
    period: str = Field(..., example="2010 ~ 2025")
    count: int = Field(..., example=112)
    metrics: SummaryMetrics
    trend: str = Field(..., example="상승 (최근 연평균 +14.2%)")
    topic: Optional[str] = None
    topic_distribution: Dict[str, int] = Field(default_factory=dict)
    key_methods: List[str] = Field(default_factory=list)
    recent_trend_desc: str = ""

# ==========================================
# Chat & Conversation Schemas
# ==========================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', 또는 'system'")
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChatRequest(BaseModel):
    message: str = Field(..., example="관절 연구동향 알려줘")
    topic: Optional[str] = Field(None, example="관절")
    conversation_id: Optional[str] = Field(None, description="기존 대화 이어서 진행 시 ID")

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    summary_used: DataSummaryResponse
    suggested_topics: List[str] = Field(default_factory=list)
    related_papers: List[Dict[str, Any]] = Field(default_factory=list)

class ConversationCreate(BaseModel):
    title: str
    topic: str = "일반"
    messages: List[ChatMessage] = Field(default_factory=list)

class ConversationResponse(BaseModel):
    id: str
    title: str
    topic: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str

# ==========================================
# Paper Schemas
# ==========================================

class PaperResponse(BaseModel):
    id: str
    title: str
    year: int
    species: str
    topic: str
    subtopic: str
    method: str
    sample_size: str
    summary: str
    keywords: List[str]
    doi: str
    journal: str
