from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from ..models.schemas import PaperResponse
from ..services.firestore_service import get_all_papers, get_paper

router = APIRouter(prefix="/api/papers", tags=["Research Papers (연구논문 아카이브)"])

@router.get("", response_model=List[PaperResponse], summary="논문 목록 및 검색")
def list_papers(
    topic: Optional[str] = Query(None, description="연구 주제 필터"),
    year: Optional[int] = Query(None, description="발행 연도 필터"),
    search: Optional[str] = Query(None, description="키워드/제목/초록 검색어")
):
    """구조화된 반려동물 연구논문 데이터를 검색하고 필터링합니다."""
    return get_all_papers(topic=topic, year=year, search=search)

@router.get("/{id}", response_model=PaperResponse, summary="특정 논문 상세 조회")
def get_single_paper(id: str):
    """논문 세부 정보(초록, 연구방법, 표본수, DOI 등)를 조회합니다."""
    paper = get_paper(id)
    if not paper:
        raise HTTPException(status_code=404, detail="해당 논문을 찾을 수 없습니다.")
    return paper
