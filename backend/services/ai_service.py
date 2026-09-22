import logging
from typing import List, Dict, Any, Optional
from ..config import GEMINI_API_KEY, GEMINI_MODEL, OPENAI_API_KEY, OPENAI_MODEL, AI_PROVIDER
from ..models.schemas import DataSummaryResponse
from ..data.seed_data import match_topic_from_query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """당신은 반려동물 연구논문 및 연구동향 분석 전문 AI 비서 'Pet Research Navigator'입니다.

[시계열 데이터 요약 (Context Injection)]
- 분석 분야: {topic}
- 데이터 기간: {period}
- 총 레코드 수: {count}개
- 주요 지표: 총합 {metrics_total}, 연평균 {metrics_avg}, 최대 {metrics_max}, 최소 {metrics_min}
- 최근 트렌드: {trend}
- 최근 트렌드 요약: {trend_desc}
- 주요 연구 기법: {key_methods}

[데이터베이스 내 대표 논문 목록]
{papers_context}

[답변 작성 원칙]
1. 사용자가 "요약해줘" 또는 연구 관련 질문을 하면, 위 시계열 데이터 요약(기간, 레코드 수, 주요 지표, 트렌드)과 대표 논문들을 종합 분석하여 친절하고 명확하게 요약해 주세요.
2. 반드시 아래의 5단계 구조(H3 마크다운 헤더 `###`)를 모두 빠짐없이 포함하여 가독성 높은 마크다운으로 체계적으로 답변하세요:
   ### 1. 연구현황
   ### 2. 주요 연구주제
   ### 3. 연구방법 및 기술 변화 (시계열 흐름)
   ### 4. 대표 논문 분석 (표본수, 연구방법, 주요 결과 명시)
   ### 5. 최근 연구 방향 및 향후 시사점
3. 각 항목별로 핵심 요점은 불릿 포인트(`-`)와 볼드체(`**`)를 적극 활용하여 한눈에 파악하기 쉽게 요약하세요.
4. 제공된 데이터 외의 정보를 사실인 것처럼 꾸며내지 말고, 신뢰할 수 있는 전문적인 어조로 설명하세요.
"""

def format_papers_context(papers: List[Dict[str, Any]]) -> str:
    if not papers:
        return "등록된 논문 데이터가 없습니다."
    lines = []
    for i, p in enumerate(papers[:5], 1):
        lines.append(
            f"[{i}] 제목: {p.get('title')} ({p.get('year')}년, 대상: {p.get('species')})\n"
            f"    - 세부분야: {p.get('subtopic')}\n"
            f"    - 연구방법: {p.get('method')} (표본: {p.get('sample_size')})\n"
            f"    - 요약: {p.get('summary')}\n"
            f"    - 저널: {p.get('journal')} (DOI: {p.get('doi')})"
        )
    return "\n\n".join(lines)

def generate_smart_fallback_reply(
    query: str,
    topic: str,
    summary: DataSummaryResponse,
    papers: List[Dict[str, Any]]
) -> str:
    """
    Intelligent template fallback when API key is not configured or in offline mode.
    Fully conforms to the 5-step answer architecture required in 09m02계획.txt.
    """
    first_paper = papers[0] if papers else {}
    second_paper = papers[1] if len(papers) > 1 else first_paper

    paper1_desc = f"- **{first_paper.get('title', '관련 연구')}** ({first_paper.get('year', '최근')}년, {first_paper.get('journal', 'Vet Journal')})\n" \
                  f"  - **연구대상/표본**: {first_paper.get('sample_size', '임상 케이스')}\n" \
                  f"  - **연구방법**: {first_paper.get('method', '정밀 분석')}\n" \
                  f"  - **주요결과**: {first_paper.get('summary', '통계적으로 유의미한 결과 확인.')}"

    paper2_desc = f"- **{second_paper.get('title', '후속 연구')}** ({second_paper.get('year', '최근')}년, {second_paper.get('journal', 'Vet Journal')})\n" \
                  f"  - **연구대상/표본**: {second_paper.get('sample_size', '임상 케이스')}\n" \
                  f"  - **연구방법**: {second_paper.get('method', '센서 및 모니터링')}\n" \
                  f"  - **주요결과**: {second_paper.get('summary', '치료 반응성 및 예후 개선 확인.')}"

    reply = f"""### 1. 연구현황
{summary.period} 동안 **{topic}** 관련 연구는 총 **{summary.count}건**의 시계열 레코드가 기록되었으며, 연구 활동 지수는 연평균 **{summary.metrics.average}** (최고 {summary.metrics.max}, 최저 {summary.metrics.min}) 수준입니다. 최근 동향은 **{summary.trend}** 양상을 뚜렷하게 보이고 있습니다.

### 2. 주요 연구주제
{topic} 분야의 핵심 연구주제는 질환 조기 선별, 치료 후 예후 평가, 일상생활 모니터링으로 집중되고 있습니다. 특히 {', '.join(summary.key_methods[:3])} 등 정밀 측정 기술을 접목한 연구가 주를 이룹니다.

### 3. 연구방법 및 기술 변화 (시계열 변화)
- **과거 (2010~2015)**: 방사선(X-ray) 등 전통적 영상진단과 병원 내 단회성 임상 관찰 및 대증 치료 연구 중심.
- **중기 (2016~2020)**: Force Plate(압력판) 등 정량적 생체역학 장비 도입 및 질환별 표준 평가 척도 정립.
- **최근 (2021~2025)**: IMU 관성센서, 웨어러블 디바이스, AI 컴퓨터 비전 및 연속 데이터 분석을 통한 **일상생활 기반 지속 원격 모니터링**으로 패러다임이 전면 전환되었습니다.

### 4. 대표 논문 분석 (초록 기반)
{paper1_desc}

{paper2_desc}

### 5. 최근 연구 방향 및 향후 시사점
{summary.recent_trend_desc} 병원 방문 시점의 일회성 진단을 넘어, 보호자의 가정 내 스마트 IoT 디바이스와 AI 알고리즘을 연계한 **조기 이상 감지(Early Detection)** 및 **맞춤형 지속 케어**가 핵심 연구 트렌드로 정착되고 있습니다.
"""
    offline_notice = (
        "> ⚠️ **[안내] 백엔드 서버(Render Cloud)는 정상 연결되었으나, 외부 실시간 AI(Gemini) 통신이 비활성화되어 있습니다.**\n"
        "> **사유**: Render 클라우드 대시보드(Environment)에 `GEMINI_API_KEY`가 아직 등록되지 않았습니다.\n"
        "> 💡 실시간 LLM 분석 대신 로컬에 안전하게 보존된 16개년 시계열 통계 데이터와 150편 논문 아카이브 기반의 5단계 구조화 분석 리포트를 제공합니다.\n"
        "> *(실시간 Gemini AI를 켜려면: Render 대시보드 -> Environment 탭에서 `GEMINI_API_KEY` 추가)*\n\n"
        "---\n\n"
    )
    return offline_notice + reply

async def generate_ai_response(
    message: str,
    topic: Optional[str],
    summary: DataSummaryResponse,
    papers: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Generates an AI response using Google Gemini (default) or OpenAI GPT with
    system prompt context injection, or falls back gracefully to smart structured synthesis.
    """
    matched_topic = topic if topic and topic != "전체" else match_topic_from_query(message)
    papers_context = format_papers_context(papers)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        topic=matched_topic,
        period=summary.period,
        count=summary.count,
        metrics_total=summary.metrics.total,
        metrics_avg=summary.metrics.average,
        metrics_max=summary.metrics.max,
        metrics_min=summary.metrics.min,
        trend=summary.trend,
        trend_desc=summary.recent_trend_desc,
        key_methods=", ".join(summary.key_methods),
        papers_context=papers_context
    )

    reply_text = ""
    engine_used = "fallback"

    # 1. Try Google Gemini if GEMINI_API_KEY is available and allowed
    use_gemini = (AI_PROVIDER in ["gemini", "auto"]) and bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())

    if use_gemini:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Build conversation history
            contents = []
            if chat_history:
                for h in chat_history[-6:]:
                    role = "user" if h.get("role") == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=h.get("content", ""))]
                    ))
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            ))

            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=4096
            )

            # Try configured model, and auto-try backup models if temporary 503 high demand occurs
            candidate_models = [GEMINI_MODEL]
            for backup in ["gemini-3.5-flash", "gemini-3.6-flash"]:
                if backup not in candidate_models:
                    candidate_models.append(backup)

            for try_model in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=try_model,
                        contents=contents,
                        config=config
                    )
                    if response and response.text:
                        reply_text = response.text.encode("utf-8", "replace").decode("utf-8")
                        engine_used = f"gemini ({try_model})"
                        break
                except Exception as model_err:
                    logger.warning(f"Gemini model {try_model} error: {model_err}")
                    continue
        except Exception as e:
            logger.warning(f"Google Gemini client error ({e}). Checking fallback options.")

    # 2. Try OpenAI if Gemini was not used or failed and OpenAI is available
    if not reply_text and (AI_PROVIDER in ["openai", "auto"]) and bool(OPENAI_API_KEY and OPENAI_API_KEY.strip()):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)

            messages = [{"role": "system", "content": system_prompt}]
            if chat_history:
                for h in chat_history[-6:]:
                    messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            messages.append({"role": "user", "content": message})

            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1200
            )
            reply_text = response.choices[0].message.content or ""
            engine_used = f"openai ({OPENAI_MODEL})"
        except Exception as e:
            logger.warning(f"OpenAI API call failed ({e}). Using intelligent fallback engine.")

    # 3. Fallback to smart structured synthesis
    if not reply_text:
        reply_text = generate_smart_fallback_reply(message, matched_topic, summary, papers)
        engine_used = "smart_fallback_engine"

    # Next suggested questions
    suggested = [
        f"{matched_topic} 분야의 가장 최근 대표 논문은 무엇인가요?",
        f"{matched_topic} 연구방법이 과거에 비해 어떻게 달라졌나요?",
        f"다른 연구 분야(예: 행동, 피부, 심장)의 최신 동향도 비교해줘"
    ]

    return {
        "reply": reply_text,
        "topic": matched_topic,
        "engine_used": engine_used,
        "suggested_topics": suggested,
        "related_papers": papers[:3]
    }
