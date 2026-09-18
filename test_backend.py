import sys
from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    print("=== 1. FastAPI TestClient 초기화 ===")
    client = TestClient(app)

    print("\n=== 2. 헬스체크 (/api/health) ===")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print(f"Health Status: {health_data}")
    assert health_data["status"] == "online"

    print("\n=== 3. 시계열 데이터 조회 (/api/data) ===")
    res = client.get("/api/data")
    assert res.status_code == 200, f"List data failed: {res.text}"
    items = res.json()
    print(f"총 데이터 포인트 개수: {len(items)}개 (요건: 최소 100개 이상)")
    assert len(items) >= 100, f"데이터 개수 부족: {len(items)} < 100"

    print("\n=== 4. 시계열 요약 API (/api/data/summary) ===")
    res = client.get("/api/data/summary?topic=관절")
    assert res.status_code == 200, f"Summary failed: {res.text}"
    summary = res.json()
    print(f"관절 분야 요약: 기간={summary['period']}, 레코드수={summary['count']}, 평균={summary['metrics']['average']}, 트렌드={summary['trend']}")
    assert summary["count"] > 0
    assert "metrics" in summary
    assert "trend" in summary

    print("\n=== 5. 데이터 CRUD 검증 ===")
    # Create
    new_payload = {
        "date": "2026-06-01",
        "value": 99.5,
        "memo": "AI 기반 맞춤형 동물 헬스케어 테스트 레코드",
        "topic": "관절"
    }
    create_res = client.post("/api/data", json=new_payload)
    assert create_res.status_code == 201, f"Create failed: {create_res.text}"
    created_item = create_res.json()
    item_id = created_item["id"]
    print(f"생성 성공: ID={item_id}, value={created_item['value']}")

    # Update
    update_res = client.put(f"/api/data/{item_id}", json={"value": 105.0, "memo": "수정된 메모"})
    assert update_res.status_code == 200, f"Update failed: {update_res.text}"
    updated_item = update_res.json()
    assert updated_item["value"] == 105.0
    print(f"수정 성공: ID={item_id}, 수정된 value={updated_item['value']}")

    # Delete
    del_res = client.delete(f"/api/data/{item_id}")
    assert del_res.status_code == 200, f"Delete failed: {del_res.text}"
    print(f"삭제 성공: ID={item_id}")

    print("\n=== 6. 논문 아카이브 조회 (/api/papers) ===")
    papers_res = client.get("/api/papers")
    assert papers_res.status_code == 200, f"Papers failed: {papers_res.text}"
    papers = papers_res.json()
    print(f"총 수집 논문 수: {len(papers)}편 (요건: 150편 이상)")
    assert len(papers) >= 150, f"논문 수 부족: {len(papers)} < 150"

    print("\n=== 7. 컨텍스트 주입 AI 챗봇 (/api/chat) ===")
    chat_payload = {
        "message": "반려견 관절 질환의 최신 연구동향과 보행분석 발전 방향을 알려줘",
        "topic": "관절"
    }
    chat_res = client.post("/api/chat", json=chat_payload)
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    print(f"대화 세션 ID: {chat_data['conversation_id']}")
    print(f"AI 응답 미리보기 (앞 200자):\n{chat_data['reply'][:200]}...")
    assert len(chat_data["reply"]) > 50
    assert "summary_used" in chat_data
    conv_id = chat_data["conversation_id"]

    print("\n=== 8. 대화 세션 조회 및 불러오기 (/api/conversations) ===")
    convs_res = client.get("/api/conversations")
    assert convs_res.status_code == 200
    convs = convs_res.json()
    assert len(convs) >= 1
    print(f"저장된 대화 세션 수: {len(convs)}개")

    # Get single conversation
    single_conv = client.get(f"/api/conversations/{conv_id}")
    assert single_conv.status_code == 200
    messages = single_conv.json()["messages"]
    print(f"불러온 대화 세션 메시지 수: {len(messages)}개 (Q&A 보존 확인)")
    assert len(messages) >= 2

    print("\n=== 9. 데이터 내보내기 (/api/data/export) ===")
    export_csv = client.get("/api/data/export?format=csv")
    assert export_csv.status_code == 200
    assert "text/csv" in export_csv.headers["content-type"]
    print("CSV 내보내기 정상 동작 확인 (UTF-8 with BOM)")

    print("\n=======================================================")
    print("[SUCCESS] Backend all core requirements and API passed (100% PASS)!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
