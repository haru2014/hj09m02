"""
Seed data generator for Pet Research Navigator.
Generates:
1. 112 time-series research records (7 categories x 16 years: 2010~2025)
2. 154 structured veterinary research papers (22 papers x 7 categories)
3. Keyword dictionary for topic matching
"""

from datetime import datetime
from typing import List, Dict, Any

TOPICS = [
    {
        "id": "joint",
        "name": "관절",
        "full_name": "근골격·관절",
        "description": "퇴행성관절염(OA), 슬개골탈구, 고관절이형성, 십자인대파열, 보행분석, 재활치료",
        "keywords": ["관절", "근골격", "슬개골", "탈구", "고관절", "십자인대", "보행", "파행", "재활", "골관절염", "joint", "osteoarthritis", "oa", "patellar", "hip", "dysplasia", "cruciate", "gait", "imu", "force plate", "lameness"]
    },
    {
        "id": "behavior",
        "name": "행동",
        "full_name": "행동·인지",
        "description": "분리불안, 공격성, 공포·공황, 상동행동, 환경풍부화, 인지기능장애(치매)",
        "keywords": ["행동", "불안", "분리불안", "공격", "공포", "스트레스", "짖음", "훈련", "환경풍부화", "치매", "behavior", "anxiety", "separation", "aggression", "fear", "compulsive", "enrichment", "stress", "phobia"]
    },
    {
        "id": "skin",
        "name": "피부",
        "full_name": "피부·알레르기",
        "description": "아토피 피부염, 알레르기 식이반응, 외이염, 세균·진균 감염, 가려움증 완화",
        "keywords": ["피부", "아토피", "알레르기", "가려움", "소양증", "외이염", "귀염증", "피부염", "피부장벽", "탈모", "skin", "atopic", "dermatitis", "allergy", "pruritus", "otitis", "microbiome", "barrier", "apoquel", "cytopoint"]
    },
    {
        "id": "disease",
        "name": "질병",
        "full_name": "내과·질병",
        "description": "당뇨병, 쿠싱증후군, 만성신부전(CKD), 췌장염, 염증성장질환(IBD), 간질환",
        "keywords": ["질병", "내과", "신부전", "당뇨", "쿠싱", "췌장염", "장질환", "간부전", "감염", "면역", "disease", "internal", "kidney", "renal", "ckd", "diabetes", "cushing", "pancreatitis", "ibd", "endocrine"]
    },
    {
        "id": "cardiology",
        "name": "심장",
        "full_name": "심장·호흡",
        "description": "이첨판폐쇄부전증(MMVD), 비대성심근증(HCM), 심부전, 폐고혈압, 만성기침",
        "keywords": ["심장", "호흡", "심부전", "이첨판", "판막", "폐고혈압", "기침", "심잡음", "hcm", "mmvd", "cardiology", "heart", "failure", "mitral", "valve", "cardiomyopathy", "murmur", "echocardiography"]
    },
    {
        "id": "nutrition",
        "name": "영양",
        "full_name": "영양·비만",
        "description": "체중 관리, 처방식 영양소 비율, 장내 마이크로바이옴, 식이보충제, 대사증후군",
        "keywords": ["영양", "비만", "다이어트", "체중", "사료", "처방식", "유산균", "마이크로바이옴", "보충제", "식이", "nutrition", "obesity", "weight", "diet", "microbiome", "metabolism", "supplement", "feed", "gut"]
    },
    {
        "id": "geriatric",
        "name": "노령",
        "full_name": "노령·종양",
        "description": "노령견/묘 케어, 인지기능저하증후군(CDS), 항암치료, 림프종, 비만세포종, 완화의료",
        "keywords": ["노령", "노화", "종양", "암", "인지기능", "치매", "완화의료", "림프종", "항암", "안락사", "geriatric", "aging", "senior", "cancer", "tumor", "cds", "cognitive", "lymphoma", "palliative", "oncology"]
    }
]

# Topic Keyword Map
KEYWORD_TO_TOPIC: Dict[str, str] = {}
for t in TOPICS:
    for kw in t["keywords"]:
        KEYWORD_TO_TOPIC[kw.lower()] = t["name"]

def match_topic_from_query(query: str) -> str:
    """Returns matched topic name or default '관절'."""
    q_clean = query.lower().strip()
    for kw, topic_name in KEYWORD_TO_TOPIC.items():
        if kw in q_clean:
            return topic_name
    return "관절"

# Method evolution per era
ERA_METHODS = {
    "early": {
        "관절": "X-ray 영상진단 및 촉진, 외과적 수술 후 임상관찰 중심",
        "행동": "설문지 기반 행동평가 및 페로몬 요법 검증",
        "피부": "피부 소파 검사 및 경구 스테로이드 치료 반응 평가",
        "질병": "혈액 생화학 검사 및 기존 인슐린 투약 프로토콜",
        "심장": "청진 및 흉부 방사선 심비대 지수(VHS) 측정",
        "영양": "단순 칼로리 제한 식이 및 체중 감량률 측정",
        "노령": "임상 증상 기반 노화 평가 및 보존적 대증 치료"
    },
    "mid": {
        "관절": "Force plate(압력판) 보행분석 및 재활 물리치료 도입",
        "행동": "C-BARQ 표준 행동 평가 도구 및 환경풍부화 실험",
        "피부": "알레르기 항원 특이 면역요법 및 JAK 억제제 초기 연구",
        "질병": "연속 혈당 측정(CGM) 및 조기 신손상 바이오마커(SDMA) 도입",
        "심장": "심장초음파 도플러 검사 및 혈중 NT-proBNP 바이오마커 분석",
        "영양": "장내 미생물총(16S rRNA) 변화 분석 및 오메가-3 지방산 연구",
        "노령": "CDS 전용 인지평가 척도 및 신경보호 영양소 연구"
    },
    "recent": {
        "관절": "IMU 관성센서·AI 컴퓨터비전 보행분석 및 원격 모니터링",
        "행동": "AI 음성/영상 기반 이상행동 자동 감지 및 스마트 홈케어",
        "피부": "단일클론항체(생물학적 제제) 및 피부 마이크로바이옴 표적 치료",
        "질병": "CGMS 연속 데이터 AI 분석 및 표적 면역치료 프로토콜",
        "심장": "스마트 청진기·AI 심전도(ECG) 분석 및 조기 심부전 예측 모델",
        "영양": "맞춤형 정밀 영양학, 대사체학(Metabolomics) 기반 식단 설계",
        "노령": "AI 기반 다중질환 모니터링 및 암 조기 혈액 액체생검 연구"
    }
}

def generate_seed_timeseries() -> List[Dict[str, Any]]:
    """
    Generates 112 time-series records: 7 topics x 16 years (2010~2025).
    """
    items = []
    years = list(range(2010, 2026))

    # Base starting publication counts in 2010 and growth rates
    base_counts = {
        "관절": (10, 1.13),
        "행동": (8, 1.14),
        "피부": (12, 1.11),
        "질병": (15, 1.10),
        "심장": (11, 1.12),
        "영양": (7, 1.15),
        "노령": (6, 1.16),
    }

    for topic in ["관절", "행동", "피부", "질병", "심장", "영양", "노령"]:
        start_val, rate = base_counts[topic]
        current_val = float(start_val)
        for i, year in enumerate(years):
            # Gradual non-linear growth with minor fluctuations
            fluctuation = (1.0 + ((i % 3) - 1) * 0.03)
            val = round(current_val * fluctuation, 1)
            current_val = current_val * rate

            if year <= 2014:
                memo = f"{year}년 {topic} 연구: {ERA_METHODS['early'][topic]}"
            elif year <= 2020:
                memo = f"{year}년 {topic} 연구: {ERA_METHODS['mid'][topic]}"
            else:
                memo = f"{year}년 {topic} 연구: {ERA_METHODS['recent'][topic]}"

            items.append({
                "id": f"data_{topic}_{year}",
                "date": f"{year}-01-01",
                "value": val,
                "memo": memo,
                "topic": topic,
                "created_at": datetime(year, 1, 1).isoformat()
            })

    return items

def generate_seed_papers() -> List[Dict[str, Any]]:
    """
    Generates 154 structured veterinary research papers (22 papers per 7 topics).
    """
    papers = []
    
    # Paper templates per topic
    topic_paper_templates = {
        "관절": [
            ("반려견 퇴행성관절염에서 IMU 관성센서를 이용한 보행 대칭성 정량 평가", 2024, "dog", "osteoarthritis", "IMU Gait Analysis", "반려견 42두", "IMU 센서 부착 후 비대칭 지수 측정 결과 방사선 등급과 유의미한 상관성 확인.", ["IMU", "보행분석", "골관절염", "센서"], "10.1016/j.jvs.2024.01.012", "Veterinary Surgery"),
            ("컴퓨터 비전 기반 마커리스 반려견 보행 추적을 통한 슬개골 탈구 조기 선별", 2025, "dog", "patellar luxation", "Computer Vision AI", "반려견 68두", "2D 스마트폰 영상만으로 슬개골 탈구 2~3기 보행 이상을 91.4% 정확도로 감지.", ["AI", "컴퓨터비전", "슬개골탈구", "선별검사"], "10.3390/vetsci12020089", "Veterinary Sciences"),
            ("Force Plate 압력판을 활용한 대형견 고관절이형성증 외과수술 전후 체중부하 비교", 2018, "dog", "hip dysplasia", "Force Plate", "반려견 30두", "수술 12주 후 최고수직지면반발력(PVF)이 정상 대조군의 88% 수준까지 회복됨을 입증.", ["고관절이형성", "Force Plate", "체중부하", "재활"], "10.1111/vsu.12940", "Veterinary Surgery"),
            ("노령묘 퇴행성관절질환(DJD) 평가를 위한 가정 내 웨어러블 활동량 센서 유용성", 2023, "cat", "osteoarthritis", "Wearable Accelerometer", "반려묘 35두", "목걸이형 센서로 수면/활동 사이클을 측정하여 진통제 투여 전후 유의한 활동성 개선 포착.", ["고양이", "웨어러블", "DJD", "가정모니터링"], "10.1177/1098612X2311890", "J Feline Med Surg"),
            ("반려견 전방십자인대 파열 후 수중 러닝머신 재활 치료가 근육량 및 보행에 미치는 영향", 2020, "dog", "cruciate ligament", "Hydrotherapy & Kinematics", "반려견 24두", "수중 보행 8주 프로토콜 적용 시 대퇴부 둘레 및 지면반발력 회복 속도가 35% 단축.", ["십자인대", "수중재활", "근골격", "보행분석"], "10.1292/jvms.20-0112", "J Vet Med Sci"),
            ("반려견 골관절염 관리를 위한 줄기세포 유래 엑소좀 관절강내 주사의 임상적 효능", 2024, "dog", "osteoarthritis", "Regenerative Therapy", "반려견 20두", "관절강 내 1회 주사 후 6개월간 파행 점수 감소 및 염증 바이오마커 유의적 감소.", ["엑소좀", "재생의학", "골관절염", "통증완화"], "10.3389/fvets.2024.1350", "Front Vet Sci"),
            ("반려견의 파행 등급 평가에서 수의사와 스마트폰 비디오 분석 AI의 일치도 연구", 2025, "dog", "lameness", "AI Video Analysis", "반려견 110두", "AI 평가 결과와 전문 수의사 5인의 시각적 파행 점수 간 Cohen kappa 계수 0.86 달성.", ["AI", "파행평가", "원격진료", "비디오분석"], "10.1016/j.tvjl.2025.106001", "The Veterinary Journal"),
            ("스마트 보행 매트를 이용한 소형견 슬개골 탈구 등급별 정적·동적 족저압 분석", 2021, "dog", "patellar luxation", "Pressure Mat System", "반려견 55두", "내측 슬개골 탈구 등급 상승에 따라 후지 외측 편향 하중이 통계적으로 유의하게 증가.", ["슬개골탈구", "족저압", "보행매트", "생체역학"], "10.4142/jvs.2021.22.e45", "Journal of Veterinary Science"),
            ("반려견 관절낭염 진단에서 초음파와 자기공명영상(MRI)의 민감도 비교", 2016, "dog", "synovitis", "Ultrasound vs MRI", "반려견 18두", "고해상도 초음파 검사가 초기 활액막 증식증 평가에서 MRI와 대등한 진단 일치도 보임.", ["영상진단", "초음파", "MRI", "관절염"], "10.1111/vru.12356", "Veterinary Radiology"),
            ("가정 내 IoT 체중계와 스마트 보행 감지기를 활용한 관절염 노령견의 원격 치료 추적", 2024, "dog", "osteoarthritis", "IoT Remote Monitoring", "반려견 40두", "병원 방문 없이 일상생활 중 일별 기립 시간 및 보행 속도 변화를 자동 추적 완료.", ["IoT", "원격모니터링", "노령견", "골관절염"], "10.1038/s41598-024-58900", "Scientific Reports")
        ],
        "행동": [
            ("반려견 분리불안 시 심박변이도(HRV)와 코르티솔 분비의 시간대별 상관관계", 2023, "dog", "separation anxiety", "ECG Sensor & Salivary Cortisol", "반려견 36두", "보호자 외출 직후 15분간 교감신경계 활성도가 정점을 기록하며 코르티솔 급상승 확인.", ["분리불안", "HRV", "스트레스", "생체신호"], "10.1016/j.applanim.2023.1059", "Applied Animal Behaviour"),
            ("음성 인식 AI를 이용한 반려견 분리불안 특이 하울링 및 짖음 패턴 자동 분류", 2024, "dog", "separation anxiety", "Acoustic AI Model", "반려견 50두 음원", "불안 음성과 일반 경계 짖음을 94.2% 정확도로 실시간 분류하는 신경망 모델 개발.", ["AI음성분석", "하울링", "분리불안", "스마트케어"], "10.3390/ani14050789", "Animals"),
            ("반려묘 환경풍부화 프로토콜이 실내묘 스트레스 행동 및 요로계 질환(FIC)에 미치는 영향", 2021, "cat", "feline stress", "Environmental Enrichment", "반려묘 45두", "수직 공간 및 먹이퍼즐 제공 6주 후 특발성 방광염 재발률 48% 감소 확인.", ["고양이", "환경풍부화", "FIC", "스트레스"], "10.1177/1098612X211002", "J Feline Med Surg"),
            ("보호자-반려견 애착 유형과 반려견 공격 행동 발현 간의 다변량 분석", 2019, "dog", "aggression", "C-BARQ Survey & Behavioral Test", "반려견 250두", "불안정 회피형 애착 보호자 집단에서 낯선 사람 및 동종에 대한 공격성 발현율 유의적 증가.", ["공격성", "C-BARQ", "애착유형", "동물행동"], "10.1016/j.jveb.2019.04.005", "J Vet Behav"),
            ("웨어러블 가속도 센서를 이용한 고양이 야간 상동행동 및 불안 증세 조기 감지", 2024, "cat", "compulsive behavior", "Wearable Accelerometer", "반려묘 28두", "과도한 그루밍 및 야간 배회 패턴을 89% 민감도로 사전에 탐지하여 행동치료 개입 지원.", ["고양이", "웨어러블", "그루밍", "상동행동"], "10.3389/fvets.2024.1378", "Front Vet Sci"),
            ("클리커 트레이닝과 양의 강화 훈련이 유기견 입양 후 사회화 적응에 미치는 긍정적 효과", 2022, "dog", "socialization", "Positive Reinforcement Training", "유기견 60두", "처벌 기반 훈련군 대비 학습 습득률 40% 향상 및 공포 반응 지수 급감.", ["긍정강화", "훈련", "사회화", "유기견"], "10.1080/10888705.2022.204", "J Appl Anim Welf Sci")
        ],
        "피부": [
            ("반려견 아토피 피부염에서 피부 마이크로바이옴 불균형과 표피 장벽 기능의 상관성", 2023, "dog", "atopic dermatitis", "16S rRNA Metagenomics", "반려견 52두", "아토피 발병 부위에서 Staphylococcus pseudintermedius 우점도 증가 및 세라마이드 농도 저하.", ["아토피", "마이크로바이옴", "피부장벽", "세균총"], "10.1111/vde.13150", "Veterinary Dermatology"),
            ("반려견 알레르기 가려움증 치료에서 오클라시티닙과 로키베트맙의 12주 임상 효과 비교", 2022, "dog", "pruritus", "Randomized Controlled Trial", "반려견 80두", "두 제제 모두 CADESI-4 점수를 60% 이상 유의미하게 감소시켰으며 내약성 우수.", ["Apoquel", "Cytopoint", "가려움", "알레르기"], "10.1186/s12917-022-033", "BMC Vet Res"),
            ("스마트폰 고해상도 카메라 및 딥러닝을 활용한 반려견 피부 병변 5종 자동 감별", 2025, "dog", "skin lesions", "Deep Learning Vision", "임상 이미지 4,500장", "농피증, 진균증, 알레르기 피부염, 지루증, 흑색극세포증 감별 분류 정확도 92.8%.", ["AI진단", "피부병변", "딥러닝", "원격스크리닝"], "10.1016/j.vetmic.2025.109", "Vet Microbiol"),
            ("고양이 호산구성 육아종 복합체(EGC)의 면역조절 요법 및 알레르기 항원 회피 요법", 2020, "cat", "eosinophilic granuloma", "Immunomodulation & Elimination", "반려묘 30두", "저알레르기 가수분해 식이 전환과 사이클로스포린 병용 시 8주 내 완전 관해율 73%.", ["고양이피부", "EGC", "가수분해식이", "면역요법"], "10.1177/1098612X2094", "J Feline Med Surg"),
            ("피부 국소 세라마이드·지방산 제제 도포가 아토피 반려견의 경피수분손실도(TEWL) 개선에 미치는 영향", 2019, "dog", "barrier repair", "Transepidermal Water Loss", "반려견 34두", "4주간 도포 후 TEWL 값이 평균 28% 감소하여 피부 장벽 회복 확인.", ["TEWL", "피부장벽", "세라마이드", "아토피"], "10.1111/vde.12780", "Veterinary Dermatology")
        ],
        "질병": [
            ("반려견 당뇨병 환자에서 연속혈당측정기(CGMS) 기반 인슐린 정밀 투약 프로토콜", 2024, "dog", "diabetes mellitus", "Flash Glucose Monitoring", "반려견 40두", "CGMS 적용 군에서 저혈당 쇼크 발생률 75% 감소 및 혈중 프락토사민 유의미 안정화.", ["당뇨", "CGMS", "인슐린", "혈당관리"], "10.1111/jvim.17050", "J Vet Intern Med"),
            ("고양이 만성신부전(CKD) 2~3기 조기 진단을 위한 혈중 SDMA 및 요중 바이오마커 연구", 2022, "cat", "chronic kidney disease", "SDMA Biomarker ELISA", "반려묘 70두", "크레아티닌 수치 상승 전 평균 11개월 앞서 신기능 저하를 조기 포착 가능함을 입증.", ["신부전", "SDMA", "CKD", "조기진단"], "10.1177/1098612X22108", "J Feline Med Surg"),
            ("반려견 급성 췌장염 진단에서 정량적 cPLI와 복부 초음파 검사의 예후 예측도 분석", 2021, "dog", "pancreatitis", "Spec cPL & Ultrasound Scoring", "반려견 65두", "cPLI 농도와 초음파 췌장 에코 이상 점수의 결합이 입원 기간 및 생존율 예측에 유의.", ["췌장염", "cPLI", "초음파", "예후인자"], "10.1111/jvim.16120", "J Vet Intern Med"),
            ("시계열 혈액 검사 데이터를 활용한 개 부신피질기능항진증(쿠싱증후군) AI 진단 모델", 2025, "dog", "hyperadrenocorticism", "Machine Learning Prediction", "임상 케이스 420건", "ALP, 콜레스테롤, 요비중 복합 시계열 분석을 통해 진단 민감도 94.6% 달성.", ["쿠싱증후군", "머신러닝", "부신질환", "예측모델"], "10.3389/fvets.2025.140", "Front Vet Sci")
        ],
        "심장": [
            ("소형견 이첨판폐쇄부전증(MMVD) B2기에서 피모벤단 조기 투여의 심비대 지연 효과", 2023, "dog", "mitral valve disease", "Echocardiography Doppler", "반려견 85두", "피모벤단 조기 투약 시 울혈성 심부전 발병 시점을 평균 15개월 지연시키는 장기 추적 결과.", ["MMVD", "심장병", "피모벤단", "심부전지연"], "10.1111/jvim.16800", "J Vet Intern Med"),
            ("스마트 전자청진기와 딥러닝을 활용한 반려견 심잡음(Murmur) 등급 자동 판독 시스템", 2024, "dog", "heart murmur", "Digital Stethoscope & CNN", "반려견 150두 음향", "심잡음 1~6등급 분류 정확도 91.2% 및 심장초음파 연계 진단 보조 성능 검증.", ["스마트청진기", "심잡음", "딥러닝", "심장검진"], "10.1016/j.jvc.2024.02.001", "J Vet Cardiol"),
            ("고양이 비대성심근증(HCM) 무증상 선별을 위한 혈중 NT-proBNP 신속 진단 키트의 유용성", 2022, "cat", "hypertrophic cardiomyopathy", "Biomarker ELISA", "반려묘 92두", "NT-proBNP 100 pmol/L 초과 시 심근 비대증 양성 예측도 93.5% 기록.", ["고양이심장", "HCM", "NT-proBNP", "선별검사"], "10.1177/1098612X22110", "J Feline Med Surg"),
            ("반려견 울혈성 심부전 환자의 가정 내 안정 시 호흡수(SRR) 스마트폰 앱 기반 원격 모니터링", 2025, "dog", "congestive heart failure", "Mobile App Remote Health", "반려견 55두", "호흡수 급증 감지를 통해 폐수종 조기 재입원율을 42% 감소시키는 임상 성과 달성.", ["심부전", "호흡수", "원격모니터링", "폐수종"], "10.1016/j.tvjl.2025.106", "The Veterinary Journal")
        ],
        "영양": [
            ("반려견 비만 관리에서 고단백·고섬유소 처방 식이와 장내 미생물총 다양성 변화", 2023, "dog", "obesity management", "16S rRNA Microbiome Analysis", "반려견 48두", "체중 15% 감량 성공군에서 비만 관련 Firmicutes/Bacteroidetes 비율이 유의미하게 정상화.", ["비만", "다이어트", "마이크로바이옴", "처방식"], "10.3390/microorganisms1108", "Microorganisms"),
            ("스마트 IoT 식판을 활용한 반려견 섭식 속도 및 섭취량 정밀 측정과 급체 예방 효과", 2024, "dog", "feeding behavior", "IoT Smart Feeder System", "반려견 35두", "평균 식사 시간을 3.8배 연장시키고 위장관 가스 팽만 증상을 60% 완화.", ["스마트식판", "IoT", "섭식행동", "소화기건강"], "10.3390/ani14060850", "Animals"),
            ("오메가-3 지방산(EPA/DHA) 보충이 신장 및 심장 복합 질환 반려견의 혈중 지질 개선에 미치는 영향", 2021, "dog", "dietary supplement", "Nutritional Intervention Trial", "반려견 42두", "항염증 지방산 지수 증가 및 소변 단백질 배출률(UPC) 24% 감소 확인.", ["오메가3", "영양제", "신장건강", "심장영양"], "10.1111/jpn.13520", "J Anim Physiol Anim Nutr"),
            ("고양이 체중 감량 프로그램 중 L-카르니틴 첨가가 제지방량(Lean Body Mass) 보존에 미치는 효과", 2022, "cat", "feline obesity", "Body Composition DEXA", "반려묘 26두", "칼로리 제한 중에도 골격근 손실 없이 체지방만 선택적으로 연소됨을 DEXA 스캔으로 증명.", ["고양이비만", "L카르니틴", "근육보존", "DEXA"], "10.1186/s12917-022-034", "BMC Vet Res")
        ],
        "노령": [
            ("반려견 인지기능장애증후군(치매, CDS) 환자에서 중쇄지방산(MCT) 식이가 뇌 기능에 미치는 개선 효과", 2023, "dog", "cognitive dysfunction", "Cognitive Testing & MRI", "노령견 38두", "MCT 오일 보충 90일 후 방향감각 상실 및 수면장애 행동 점수 44% 개선 입증.", ["치매", "CDS", "노령견", "MCT식이"], "10.1111/jvim.16720", "J Vet Intern Med"),
            ("노령 반려동물의 수면 패턴 및 야간 배회 모니터링을 위한 침대 매트리스 압력 센서 시스템", 2024, "both", "geriatric sleep monitoring", "Pressure Sensor Array", "노령견/묘 45두", "야간 불안 및 관절 통증으로 인한 잦은 뒤척임을 93% 정확도로 비침습 측정 성공.", ["노령동물", "수면모니터링", "압력센서", "원격돌봄"], "10.3390/s24082500", "Sensors"),
            ("반려견 림프종 조기 진단을 위한 혈액 순환 종양 DNA(ctDNA) 차세대 염기서열분석(NGS)", 2024, "dog", "lymphoma oncology", "Liquid Biopsy NGS", "반려견 60두", "조직 생검 전 혈액 2ml만으로 림프종 특이 돌연변이를 95% 민감도로 검출.", ["종양", "액체생검", "림프종", "차세대염기서열"], "10.1186/s12917-024-040", "BMC Vet Res"),
            ("노령묘 복합 만성질환 관리를 위한 삶의 질(QoL) 다차원 평가 척도 유효성 검증", 2021, "cat", "geriatric quality of life", "QoL Questionnaire & Biomarkers", "노령묘 110두", "보호자 평가와 신체 충실 지수의 표준화된 결합을 통해 완화치료 계획 수립에 기여.", ["노령묘", "삶의질", "QoL", "완화의료"], "10.1177/1098612X21102", "J Feline Med Surg")
        ]
    }

    paper_id_counter = 1
    years_pool = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

    for topic_name, base_list in topic_paper_templates.items():
        # Each topic gets 22 papers (total 7 x 22 = 154 papers)
        for idx in range(22):
            template = base_list[idx % len(base_list)]
            base_title, orig_year, species, subtopic, method, sample_size, summary, keywords, doi, journal = template
            
            # Distribute across years 2010 ~ 2025
            year = years_pool[idx % len(years_pool)]
            # If variant, slightly tweak title for realism
            if idx >= len(base_list):
                variant_suffix = f" (연구 심화 {idx - len(base_list) + 1}보)"
                title = f"{base_title}{variant_suffix}"
            else:
                title = base_title

            papers.append({
                "id": f"paper_{paper_id_counter:03d}",
                "title": title,
                "year": year,
                "species": species,
                "topic": topic_name,
                "subtopic": subtopic,
                "method": method,
                "sample_size": sample_size,
                "summary": summary,
                "keywords": keywords,
                "doi": f"{doi}.v{idx+1}",
                "journal": journal
            })
            paper_id_counter += 1

    return papers
