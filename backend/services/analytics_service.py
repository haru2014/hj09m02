from typing import List, Dict, Any, Optional
from ..models.schemas import DataSummaryResponse, SummaryMetrics

def compute_data_summary(items: List[Dict[str, Any]], topic_filter: Optional[str] = None) -> DataSummaryResponse:
    """
    Computes time-series statistical metrics and trend analysis for system prompt context injection.
    """
    if not items:
        return DataSummaryResponse(
            period="데이터 없음",
            count=0,
            metrics=SummaryMetrics(total=0, average=0, max=0, min=0),
            trend="데이터 없음",
            topic=topic_filter,
            topic_distribution={},
            key_methods=[],
            recent_trend_desc="등록된 데이터가 없습니다."
        )

    # Filter items if topic_filter is given
    filtered = items
    if topic_filter and topic_filter != "전체":
        filtered = [item for item in items if item.get("topic") == topic_filter]
        if not filtered:
            filtered = items # Fallback to all items if filtered is empty

    # Extract dates & values
    sorted_items = sorted(filtered, key=lambda x: str(x.get("date", "")))
    values = [float(x.get("value", 0)) for x in sorted_items]
    dates = [str(x.get("date", "")) for x in sorted_items]

    total_val = sum(values)
    count = len(values)
    avg_val = round(total_val / count, 1) if count > 0 else 0
    max_val = max(values) if values else 0
    min_val = min(values) if values else 0

    first_date = dates[0][:7] if dates else ""
    last_date = dates[-1][:7] if dates else ""
    period_str = f"{first_date} ~ {last_date}" if first_date != last_date else first_date

    # Topic distribution
    topic_dist: Dict[str, int] = {}
    for item in items:
        t = item.get("topic", "기타")
        topic_dist[t] = topic_dist.get(t, 0) + 1

    # Trend calculation
    # Compare first 30% with last 30%
    slice_size = max(1, count // 3)
    early_avg = sum(values[:slice_size]) / slice_size if slice_size > 0 else 0
    recent_avg = sum(values[-slice_size:]) / slice_size if slice_size > 0 else 0

    if early_avg > 0:
        growth_pct = round(((recent_avg - early_avg) / early_avg) * 100, 1)
        if growth_pct > 5:
            trend_str = f"지속 상승 (초기 대비 +{growth_pct}%)"
            trend_desc = f"연구 활동량이 꾸준히 증가 추세에 있으며, 특히 최근 연도에 데이터 및 논문 발표 수가 집중되고 있습니다."
        elif growth_pct < -5:
            trend_str = f"하향 조정 ({growth_pct}%)"
            trend_desc = f"초기 집중 연구 시기 대비 최근 연구 발표 빈도가 다소 안정세로 접어들었습니다."
        else:
            trend_str = "안정적 유지 (변동폭 ±5% 이내)"
            trend_desc = f"일정한 연구 수요와 데이터 축적이 지속적으로 유지되고 있습니다."
    else:
        trend_str = "신규 데이터 축적 중"
        trend_desc = "현재 시점부터 데이터가 누적되고 있습니다."

    # Extract key methods from memos
    key_methods = []
    method_keywords = ["IMU", "AI", "보행분석", "Force plate", "영상진단", "X-ray", "초음파", "센서", "웨어러블", "원격모니터링", "유전자", "면역요법", "머신러닝"]
    for m in method_keywords:
        if any(m.lower() in str(x.get("memo", "")).lower() for x in sorted_items):
            key_methods.append(m)

    if not key_methods:
        key_methods = ["임상관찰", "영상진단", "센서 모니터링", "AI 분석"]

    return DataSummaryResponse(
        period=period_str,
        count=count,
        metrics=SummaryMetrics(
            total=round(total_val, 1),
            average=avg_val,
            max=round(max_val, 1),
            min=round(min_val, 1)
        ),
        trend=trend_str,
        topic=topic_filter,
        topic_distribution=topic_dist,
        key_methods=key_methods[:6],
        recent_trend_desc=trend_desc
    )
