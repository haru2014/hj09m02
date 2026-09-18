import io
import csv
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from ..models.schemas import DataItemCreate, DataItemUpdate, DataItemResponse, DataSummaryResponse
from ..services.firestore_service import (
    get_all_data,
    get_data_item,
    add_data_item,
    update_data_item,
    delete_data_item
)
from ..services.analytics_service import compute_data_summary

router = APIRouter(prefix="/api/data", tags=["Data Management (CRUD & Summary)"])

@router.get("", response_model=List[DataItemResponse], summary="시계열 데이터 목록 조회")
def list_data(topic: Optional[str] = Query(None, description="연구 주제 필터 (예: 관절, 행동 등)")):
    """저장된 시계열 연구 데이터를 조회합니다."""
    return get_all_data(topic=topic)

@router.get("/summary", response_model=DataSummaryResponse, summary="시계열 데이터 요약 (시스템 프롬프트 주입용)")
def get_data_summary(topic: Optional[str] = Query(None, description="요약을 생성할 연구 주제")):
    """기간, 데이터 수, 지표(평균/최대/최소), 최근 트렌드 등 요약 정보를 반환합니다."""
    items = get_all_data(topic=topic)
    return compute_data_summary(items, topic_filter=topic)

@router.get("/export", summary="데이터 내보내기 (CSV/JSON)")
def export_data(
    format: str = Query("csv", pattern="^(csv|json)$", description="내보내기 포맷 (csv 또는 json)"),
    topic: Optional[str] = Query(None, description="주제 필터")
):
    """시계열 데이터를 CSV 또는 JSON 파일로 다운로드합니다 (보너스 과제)."""
    items = get_all_data(topic=topic)

    if format == "json":
        content = json.dumps(items, ensure_ascii=False, indent=2)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=pet_research_data_{topic or 'all'}.json"}
        )

    # CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "date", "topic", "value", "memo", "created_at"])
    for item in items:
        writer.writerow([
            item.get("id", ""),
            item.get("date", ""),
            item.get("topic", ""),
            item.get("value", 0),
            item.get("memo", ""),
            item.get("created_at", "")
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig") # BOM for Excel Korean support
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=pet_research_data_{topic or 'all'}.csv"}
    )

@router.get("/{id}", response_model=DataItemResponse, summary="특정 데이터 항목 조회")
def read_data_item(id: str):
    item = get_data_item(id)
    if not item:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터를 찾을 수 없습니다.")
    return item

@router.post("", response_model=DataItemResponse, status_code=201, summary="새 데이터 추가")
def create_data_item(payload: DataItemCreate):
    """(date, value, memo, topic) 구조의 새 데이터를 추가합니다."""
    created = add_data_item(payload.model_dump())
    return created

@router.put("/{id}", response_model=DataItemResponse, summary="데이터 수정")
def update_existing_data(id: str, payload: DataItemUpdate):
    """기존 데이터 항목을 수정합니다."""
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="수정할 내용이 전달되지 않았습니다.")
    updated = update_data_item(id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터를 찾을 수 없습니다.")
    return updated

@router.delete("/{id}", summary="데이터 삭제")
def delete_existing_data(id: str):
    """데이터 항목을 삭제합니다."""
    success = delete_data_item(id)
    if not success:
        raise HTTPException(status_code=404, detail="해당 ID의 데이터를 찾을 수 없습니다.")
    return {"status": "success", "message": f"데이터 {id}가 성공적으로 삭제되었습니다."}
