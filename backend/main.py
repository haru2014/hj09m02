from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ALLOWED_ORIGINS, GEMINI_API_KEY, GEMINI_MODEL, OPENAI_MODEL, OPENAI_API_KEY, AI_PROVIDER
from .services.firestore_service import seed_firestore_if_empty, is_firestore_connected
from .api.data import router as data_router
from .api.chat import router as chat_router
from .api.conversations import router as conversations_router
from .api.papers import router as papers_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    seed_firestore_if_empty()
    yield
    # Shutdown actions

app = FastAPI(
    title="Pet Research Navigator API",
    description="반려동물 연구논문 및 시계열 연구동향 AI 비서 백엔드 서비스 (FastAPI + Firestore + Gemini/OpenAI Context Injection)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(data_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(papers_router)

@app.get("/api/info", summary="Root Info")
def root():
    return {
        "service": "Pet Research Navigator API",
        "description": "반려동물 연구논문·연구동향 AI 비서 API 서비스",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health", summary="헬스체크 및 슬립 상태 안내")
def health_check():
    """
    Render 무료 티어의 슬립(콜드스타트) 완화 및 서버 상태 확인용 헬스체크 엔드포인트.
    """
    active_engine = "smart_fallback_engine"
    active_model = "template"
    if (AI_PROVIDER in ["gemini", "auto"]) and (GEMINI_API_KEY and GEMINI_API_KEY.strip()):
        active_engine = "gemini"
        active_model = GEMINI_MODEL
    elif (AI_PROVIDER in ["openai", "auto"]) and (OPENAI_API_KEY and OPENAI_API_KEY.strip()):
        active_engine = "openai"
        active_model = OPENAI_MODEL

    import os
    is_cloud = bool(os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID") or os.getenv("PORT", "8000") != "8000")
    
    if is_firestore_connected():
        db_name = "firestore"
        db_label = "Firebase Firestore"
    elif is_cloud:
        db_name = "cloud_store"
        db_label = "Render Cloud"
    else:
        db_name = "local_store"
        db_label = "Local Dev"

    return {
        "status": "online",
        "database": db_name,
        "database_label": db_label,
        "is_cloud": is_cloud,
        "is_firestore": is_firestore_connected(),
        "ai_engine": active_engine,
        "model": active_model,
        "cold_start_tip": "Render 무료 인스턴스 슬립 해제 완료 (정상 응답 중)"
    }

# Mount frontend for local unified preview if frontend directory exists
from pathlib import Path
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

