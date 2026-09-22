1. Vercel 배포 환경에서 백엔드 API 404 Not Found 문제 해결

🔴 무엇이 문제였는가?
프론트엔드를 Vercel에 배포했을 때, frontend/config.js에서 백엔드 API 기본 주소를 window.location.origin(Vercel 도메인)으로 폴백하도록 설정되어 있었습니다.
Vercel은 정적 페이지만 호스팅하고 백엔드 API(FastAPI)는 별도의 Render 서버에 배포되어 있었기 때문에, 브라우저가 Vercel 도메인으로 /api/data, /api/chat 등을 호출하면서 404 Not Found 오류가 발생하여 모든 백엔드 API가 동작하지 않았습니다.
🟢 어떻게 해결했는가?
config.js의 Vercel 환경 기본 백엔드 URL을 window.location.origin 대신 실제 배포된 Render 백엔드 주소(https://samsung-stock-ai-assistant.onrender.com)로 기본 지정하여 배포 상태에서도 프론트엔드가 백엔드 API와 올바르게 통신할 수 있도록 해결했습니다.

2. 브라우저에서 백엔드 API URL 동적 설정 및 연결 제어 기능 추가

🔴 무엇이 문제였는가?
Render 무료 티어 특성상 장시간 미사용 시 슬립 모드(Cold Start, 약 30~50초 기동 지연)에 진입하여 초기에 API 요청이 타임아웃되거나 멈춘 것처럼 보였습니다.
또한, 개발/운영 환경에 따라 백엔드 API 서버 URL이 변경되거나 로컬(http://localhost:8000) 테스트가 필요한 경우 소스 코드를 재배포하지 않고는 주소를 변경할 수 없었습니다.
🟢 어떻게 해결했는가?
프론트엔드 UI에 API 서버 연결 설정 모달(serverSettingsModal)을 추가했습니다.
localStorage에 API_BASE_URL을 저장하여 사용자가 Render 서버 주소를 직접 입력하거나 로컬 개발 서버(http://localhost:8000)로 원클릭 초기화/전환할 수 있도록 개선했습니다.

3. Swagger API 문서(/docs) 404 이동 문제 해결

🔴 무엇이 문제였는가?
상단 네비게이션의 "Swagger API Docs" 링크가 단순 상대 경로 href="/docs"로 하드코딩되어 있어, Vercel 배포 환경에서 클릭 시 Vercel 자체의 /docs로 이동하여 404 Not Found가 발생했습니다.
🟢 어떻게 해결했는가?

frontend/app.js
 초기화 시점에 elements.swaggerDocsLink.href = ${CONFIG.API_BASE_URL}/docs``로 동적 바인딩하여, 설정된 백엔드 API 서버의 /docs로 정확하게 이동하도록 수정했습니다.

4. 로컬/백엔드 단독 서빙 시 정적 파일 404 및 스크립트 로드 실패 해결

🔴 무엇이 문제였는가?
FastAPI 백엔드로 웹을 직접 서빙할 때 /static 경로만 마운트되어 있어, HTML에서 상대경로로 참조하던 /styles.css, /app.js, /config.js가 루트 경로에서 404 에러를 반환해 자바스크립트 API 클라이언트 자체가 구동되지 못했습니다.
🟢 어떻게 해결했는가?


backend/main.py에 루트 경로 정적 파일 마운트(app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend_root"))를 추가하여 스크립트와 CSS가 정상 로드되도록 해결했습니다.

5. Gemini AI 모델 호출 실패 시 다중 모델 순차 시도(Fallback) 처리

🔴 무엇이 문제였는가?
특정 단일 Gemini 모델명(gemini-2.5-flash)만 고정 호출하도록 되어 있어, 해당 모델 엔드포인트의 일시 장애 또는 미지원 발생 시 곧바로 예외가 발생하며 모의(Mock) 응답으로 빠지는 문제가 있었습니다.
🟢 어떻게 해결했는가?
models_to_try = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-3.5-flash", "gemini-2.5-flash"] 후보 리스트를 두고 순차적으로 호출을 재시도하는 Fallback 로직을 도입하여 외부 AI API 호출의 가용성을 크게 향상시켰습니다.