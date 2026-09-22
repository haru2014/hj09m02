/**
 * Pet Research Navigator - Frontend Application Controller
 * Pure Vanilla JavaScript (ES6+)
 */

// ========================================================
// 1. Application State & Configuration
// ========================================================
// Production Render backend API URL
const PROD_API_URL = "https://hj09m02-api.onrender.com";

/**
 * Automatically determine the most suitable API Base URL based on the runtime environment:
 * 1. On HTTPS (e.g. Vercel deployment): Use PROD_API_URL (Render HTTPS) or proxy to prevent Mixed Content blocking.
 * 2. In local dev (port 8000): Use relative URL "" (unified backend).
 * 3. In local Live Server (port 5500, 3000, etc.): Use "http://127.0.0.1:8000".
 * 4. Stored setting: Insecure http:// saved on HTTPS pages is automatically purged.
 */
function getDefaultApiBaseUrl() {
  const isHttps = window.location.protocol === "https:";
  const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

  // Check user saved preference in localStorage
  const saved = localStorage.getItem("pet_nav_api_base");
  if (saved !== null && saved !== undefined) {
    const trimmed = saved.trim().replace(/\/+$/, "");
    // Crucial Mixed Content Guard: Insecure http:// on HTTPS pages will be blocked by browsers
    if (isHttps && trimmed.startsWith("http://")) {
      console.warn("Mixed Content 방지: HTTPS 환경에서 비암호화 HTTP 설정(127.0.0.1)이 발견되어 Render 배포 서버 주소로 자동 전환합니다.");
      localStorage.removeItem("pet_nav_api_base");
      return PROD_API_URL;
    }
    // Purge outdated other project URL (samsung-stock) if previously stored
    if (trimmed.includes("samsung-stock")) {
      console.warn("다른 프로젝트 URL(samsung-stock)이 발견되어 현재 프로젝트 Render 정규 주소로 자동 전환합니다.");
      localStorage.removeItem("pet_nav_api_base");
      return PROD_API_URL;
    }
    return trimmed;
  }

  // 1. Direct local FastAPI unified serving
  if (window.location.port === "8000") {
    return "";
  }

  // 2. HTTPS production environment (Vercel / custom domain)
  if (isHttps) {
    return PROD_API_URL;
  }

  // 3. Local standalone frontend runner (e.g., Live Server :5500)
  if (isLocalhost) {
    return "http://127.0.0.1:8000";
  }

  return PROD_API_URL;
}

const state = {
  apiBaseUrl: getDefaultApiBaseUrl(),
  currentTopic: "관절",
  currentConvId: null,
  activeTab: "tab-chat",
  chartInstance: null,
  timeseriesData: [],
  allPapers: [],
  theme: localStorage.getItem("pet_nav_theme") || "dark",
  viewMode: localStorage.getItem("pet_nav_view_mode") || "auto"
};

// Research Methodology Shifts per Category
const TIMELINE_METRICS = {
  "관절": {
    early: "전통적 X-ray 영상진단 및 촉진, 외과적 수술 후 임상 관찰 중심",
    mid: "Force plate 압력판을 통한 정량적 체중부하 및 재활 물리치료 도입",
    recent: "IMU 센서, AI 컴퓨터 비전, 웨어러블 일상생활 비침습 연속 모니터링"
  },
  "행동": {
    early: "설문지 기반 행동평가 및 페로몬 요법 등 임상적 대증 관찰",
    mid: "C-BARQ 표준 행동 평가 도구 도입 및 환경풍부화 실험",
    recent: "AI 음성/영상 기반 이상행동 자동 감지 및 스마트 IoT 원격 홈케어"
  },
  "피부": {
    early: "피부 소파 검사 및 경구 스테로이드 치료 반응 평가 중심",
    mid: "알레르기 항원 특이 면역요법 및 JAK 억제제(아포퀠) 초기 연구",
    recent: "단일클론항체(사이토포인트) 생물학적 제제 및 피부 마이크로바이옴 표적 치료"
  },
  "질병": {
    early: "혈액 생화학 검사 및 기존 인슐린 투약 프로토콜",
    mid: "연속 혈당 측정(CGM) 및 조기 신손상 바이오마커(SDMA) 도입",
    recent: "CGMS 시계열 연속 데이터 AI 분석 및 표적 면역치료 프로토콜"
  },
  "심장": {
    early: "청진 및 흉부 방사선 심비대 지수(VHS) 측정",
    mid: "심장초음파 도플러 검사 및 혈중 NT-proBNP 바이오마커 분석",
    recent: "스마트 청진기·AI 심전도(ECG) 분석 및 조기 심부전 원격 호흡수 예측"
  },
  "영양": {
    early: "단순 칼로리 제한 식이 및 체중 감량률 측정",
    mid: "장내 미생물총(16S rRNA) 변화 분석 및 오메가-3 지방산 연구",
    recent: "맞춤형 정밀 영양학, 대사체학(Metabolomics) 및 스마트 IoT 식판 연동"
  },
  "노령": {
    early: "임상 증상 기반 노화 평가 및 보존적 대증 치료",
    mid: "CDS 전용 인지평가 척도 및 신경보호 영양소 연구",
    recent: "AI 기반 다중질환 모니터링 및 암 조기 혈액 액체생검(ctDNA) 연구"
  }
};

// ========================================================
// 2. DOM Elements Cache
// ========================================================
const el = {
  themeToggleBtn: document.getElementById("themeToggleBtn"),
  themeIcon: document.getElementById("themeIcon"),
  btnToggleViewMode: document.getElementById("btnToggleViewMode"),
  viewModeIcon: document.getElementById("viewModeIcon"),
  viewModeLabel: document.getElementById("viewModeLabel"),
  mobileBottomNav: document.getElementById("mobileBottomNav"),
  apiStatusBadge: document.getElementById("apiStatusBadge"),
  apiStatusLabel: document.getElementById("apiStatusLabel"),
  navTabs: document.getElementById("mainNavTabs"),
  tabPanes: document.querySelectorAll(".tab-pane"),
  
  // Tab 1 (Chat & Trends)
  topicChipsContainer: document.getElementById("topicChipsContainer"),
  summaryPeriod: document.getElementById("summaryPeriod"),
  summaryCount: document.getElementById("summaryCount"),
  summaryTotalValue: document.getElementById("summaryTotalValue"),
  summaryAverage: document.getElementById("summaryAverage"),
  summaryRange: document.getElementById("summaryRange"),
  summaryTrend: document.getElementById("summaryTrend"),
  summaryTrendMethod: document.getElementById("summaryTrendMethod"),
  chartTopicBadge: document.getElementById("chartTopicBadge"),
  btnRefreshSummary: document.getElementById("btnRefreshSummary"),
  timeSeriesCanvas: document.getElementById("timeSeriesChart"),
  descEarly: document.getElementById("descEarly"),
  descMid: document.getElementById("descMid"),
  descRecent: document.getElementById("descRecent"),
  
  // Chat
  chatMessagesStream: document.getElementById("chatMessagesStream"),
  chatInputForm: document.getElementById("chatInputForm"),
  chatInputText: document.getElementById("chatInputText"),
  btnClearChat: document.getElementById("btnClearChat"),
  chatContextSubtitle: document.getElementById("chatContextSubtitle"),
  chatOfflineBanner: document.getElementById("chatOfflineBanner"),
  offlineBannerIcon: document.getElementById("offlineBannerIcon"),
  offlineBannerText: document.getElementById("offlineBannerText"),
  btnBannerRetry: document.getElementById("btnBannerRetry"),
  btnBannerCheckServer: document.getElementById("btnBannerCheckServer"),
  welcomeTopic: document.getElementById("welcomeTopic"),
  promptRecentTrend: document.getElementById("promptRecentTrend"),
  promptMethodShift: document.getElementById("promptMethodShift"),
  promptKeyPapers: document.getElementById("promptKeyPapers"),

  // Tab 2 (Data CRUD)
  filterTopicSelect: document.getElementById("filterTopicSelect"),
  dataSearchInput: document.getElementById("dataSearchInput"),
  btnExportCsv: document.getElementById("btnExportCsv"),
  btnExportJson: document.getElementById("btnExportJson"),
  btnOpenAddModal: document.getElementById("btnOpenAddModal"),
  statFilteredCount: document.getElementById("statFilteredCount"),
  statAverageValue: document.getElementById("statAverageValue"),
  statTotalValue: document.getElementById("statTotalValue"),
  timeseriesTableBody: document.getElementById("timeseriesTableBody"),
  tableEmptyState: document.getElementById("tableEmptyState"),

  // Modals
  dataModalBackdrop: document.getElementById("dataModalBackdrop"),
  btnCloseDataModal: document.getElementById("btnCloseDataModal"),
  btnCancelDataModal: document.getElementById("btnCancelDataModal"),
  dataForm: document.getElementById("dataForm"),
  modalTitle: document.getElementById("modalTitle"),
  editItemId: document.getElementById("editItemId"),
  formDataDate: document.getElementById("formDataDate"),
  formDataTopic: document.getElementById("formDataTopic"),
  formDataValue: document.getElementById("formDataValue"),
  formDataMemo: document.getElementById("formDataMemo"),

  // Tab 3 (Conversations)
  conversationsGrid: document.getElementById("conversationsGrid"),
  historyEmptyState: document.getElementById("historyEmptyState"),
  btnRefreshHistory: document.getElementById("btnRefreshHistory"),
  btnGoToChat: document.getElementById("btnGoToChat"),

  // Tab 4 (Papers)
  papersGrid: document.getElementById("papersGrid"),
  paperTopicFilter: document.getElementById("paperTopicFilter"),
  paperYearFilter: document.getElementById("paperYearFilter"),
  paperSearchInput: document.getElementById("paperSearchInput"),
  papersTotalCount: document.getElementById("papersTotalCount"),
  paperModalBackdrop: document.getElementById("paperModalBackdrop"),
  btnClosePaperModal: document.getElementById("btnClosePaperModal"),
  modalPaperSpecies: document.getElementById("modalPaperSpecies"),
  modalPaperTitle: document.getElementById("modalPaperTitle"),
  modalPaperBody: document.getElementById("modalPaperBody"),

  // Swagger & Server Modal
  swaggerDocsLink: document.getElementById("swaggerDocsLink"),
  btnServerConfig: document.getElementById("btnServerConfig"),
  serverModalBackdrop: document.getElementById("serverModalBackdrop"),
  btnCloseServerModal: document.getElementById("btnCloseServerModal"),
  serverBaseUrlInput: document.getElementById("serverBaseUrlInput"),
  btnSaveServerUrl: document.getElementById("btnSaveServerUrl"),
  btnResetServerUrl: document.getElementById("btnResetServerUrl"),
  btnPresetRender: document.getElementById("btnPresetRender"),
  btnPresetLocal: document.getElementById("btnPresetLocal"),
  btnPresetProxy: document.getElementById("btnPresetProxy"),

  // Toast
  toastContainer: document.getElementById("toastContainer")
};

// ========================================================
// 3. UI Helpers & Toast Notification
// ========================================================
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  const icon = type === "success" ? "✅" : type === "error" ? "❌" : "ℹ️";
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  el.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  state.theme = theme;
  localStorage.setItem("pet_nav_theme", theme);
  el.themeIcon.textContent = theme === "dark" ? "🌙" : "☀️";
  if (state.chartInstance) {
    updateChartTheme();
  }
}

function applyViewMode(mode) {
  state.viewMode = mode;
  localStorage.setItem("pet_nav_view_mode", mode);
  document.documentElement.setAttribute("data-view-mode", mode);
  updateViewModeUI();
}

function updateViewModeUI() {
  const isMobileScreen = window.innerWidth <= 768;
  const currentMode = state.viewMode;
  const isEffectiveMobile = currentMode === "mobile" || (currentMode === "auto" && isMobileScreen);

  if (isEffectiveMobile) {
    if (el.viewModeIcon) el.viewModeIcon.textContent = "🖥️";
    if (el.viewModeLabel) el.viewModeLabel.textContent = "PC 뷰";
    if (el.btnToggleViewMode) el.btnToggleViewMode.title = "PC 화면 모드로 전환";
  } else {
    if (el.viewModeIcon) el.viewModeIcon.textContent = "📱";
    if (el.viewModeLabel) el.viewModeLabel.textContent = "모바일 뷰";
    if (el.btnToggleViewMode) el.btnToggleViewMode.title = "모바일 화면 모드로 전환";
  }
}

function updateSwaggerDocsUrl() {
  if (el.swaggerDocsLink) {
    const base = state.apiBaseUrl ? state.apiBaseUrl.replace(/\/+$/, "") : "";
    if (base) {
      el.swaggerDocsLink.href = `${base}/docs`;
    } else if (window.location.protocol === "https:" && !state.apiBaseUrl) {
      el.swaggerDocsLink.href = `${PROD_API_URL}/docs`;
    } else {
      el.swaggerDocsLink.href = "/docs";
    }
  }
}

// ========================================================
// 4. API Communication Layer
// ========================================================
async function apiRequest(endpoint, options = {}) {
  const url = `${state.apiBaseUrl}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers
      },
      ...options
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errData.detail || `HTTP Error ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

async function checkApiHealth(retryCount = 0) {
  try {
    if (retryCount > 0) {
      el.apiStatusBadge.className = "status-indicator offline";
      el.apiStatusLabel.textContent = `서버 기상 중 (Cold Start... ${retryCount}/5)`;
      if (el.offlineBannerIcon) el.offlineBannerIcon.textContent = "⏳";
      if (el.offlineBannerText) {
        el.offlineBannerText.innerHTML = `Render 클라우드 서버 기상 중입니다... <strong>(무료 플랜 슬립 해제 ${retryCount}/5, 약 30초 소요)</strong>`;
      }
      if (el.chatOfflineBanner) el.chatOfflineBanner.style.display = "flex";
    }
    const health = await apiRequest("/api/health");
    el.apiStatusBadge.className = "status-indicator online";
    
    // Friendly status label: Clear differentiation between Cloud (Render/Firestore) and Local Dev
    let targetDbLabel = health.database_label;
    if (!targetDbLabel) {
      if (health.database === "firestore") {
        targetDbLabel = "Firestore";
      } else if (state.apiBaseUrl.includes("onrender.com") || window.location.hostname.includes("vercel.app")) {
        targetDbLabel = "Render Cloud";
      } else {
        targetDbLabel = "로컬 개발";
      }
    }
    el.apiStatusLabel.textContent = `Online (${targetDbLabel})`;
    const aiNote = health.has_ai_key 
      ? `실시간 AI: ${health.ai_engine} (${health.model})`
      : `AI 엔진: ${health.ai_engine} (Render에 GEMINI_API_KEY 설정 시 실시간 활성화)`;
    el.apiStatusBadge.title = `백엔드 서버: 온라인 정상 연동 중 (${targetDbLabel}) | ${aiNote}`;
    
    if (el.chatOfflineBanner) el.chatOfflineBanner.style.display = "none";
    if (el.chatContextSubtitle) {
      el.chatContextSubtitle.innerHTML = '<span class="context-pulse"></span> 데이터 요약(Context) 자동 주입 중';
    }

    // Clear background recovery interval on success
    if (window._healthPollingTimer) {
      clearInterval(window._healthPollingTimer);
      window._healthPollingTimer = null;
    }
    return true;
  } catch (err) {
    // Free tier Render backend may take 30~50s to wake from sleep
    if (retryCount < 5 && (state.apiBaseUrl.includes("onrender.com") || state.apiBaseUrl === "")) {
      el.apiStatusBadge.className = "status-indicator offline";
      el.apiStatusLabel.textContent = `서버 기상 중 (Cold Start... ${retryCount + 1}/5)`;
      if (el.offlineBannerIcon) el.offlineBannerIcon.textContent = "⏳";
      if (el.offlineBannerText) {
        el.offlineBannerText.innerHTML = `Render 클라우드 서버 기상 중입니다... <strong>(무료 플랜 슬립 해제 ${retryCount + 1}/5, 약 30초 소요)</strong>`;
      }
      if (el.chatOfflineBanner) el.chatOfflineBanner.style.display = "flex";
      await new Promise(resolve => setTimeout(resolve, 5000));
      return await checkApiHealth(retryCount + 1);
    }

    el.apiStatusBadge.className = "status-indicator offline";
    el.apiStatusLabel.textContent = "Offline (연결 대기)";
    if (el.offlineBannerIcon) el.offlineBannerIcon.textContent = "⚠️";
    if (el.offlineBannerText) {
      el.offlineBannerText.innerHTML = "백엔드 서버 연결 대기 중입니다. Render 서버가 깨어나는 중이거나 주소 설정이 필요할 수 있습니다.";
    }
    if (el.chatOfflineBanner) el.chatOfflineBanner.style.display = "flex";
    if (el.chatContextSubtitle) {
      el.chatContextSubtitle.innerHTML = '<span style="color:var(--accent-rose,#ef4444); font-weight:600;">● 오프라인 (온라인 AI 분석 불가)</span>';
    }

    // Auto-poll in background every 8 seconds until live
    startBackgroundHealthPolling();
    return false;
  }
}

function startBackgroundHealthPolling() {
  if (window._healthPollingTimer) return;
  window._healthPollingTimer = setInterval(async () => {
    try {
      const res = await apiRequest("/api/health");
      if (res && res.status === "online") {
        clearInterval(window._healthPollingTimer);
        window._healthPollingTimer = null;
        await checkApiHealth(0);
        if (state.timeseriesData.length === 0) {
          await loadTopicTrends(state.currentTopic);
        }
        showToast("Render 클라우드 서버가 성공적으로 연결되었습니다!", "success");
      }
    } catch (_) {
      // Continue polling silently
    }
  }, 8000);
}

// ========================================================
// 5. Tab 1: AI Chat & Time-Series Trend Charts
// ========================================================
async function loadTopicTrends(topic) {
  state.currentTopic = topic;
  if (el.chartTopicBadge) el.chartTopicBadge.textContent = topic;
  if (el.welcomeTopic) el.welcomeTopic.textContent = topic;

  // Update Timeline text
  const shifts = TIMELINE_METRICS[topic] || TIMELINE_METRICS["관절"];
  el.descEarly.textContent = shifts.early;
  el.descMid.textContent = shifts.mid;
  el.descRecent.textContent = shifts.recent;

  try {
    // 1. Fetch Summary
    const summary = await apiRequest(`/api/data/summary?topic=${encodeURIComponent(topic)}`);
    renderSummaryCards(summary);

    // 2. Fetch Topic Timeseries for Chart
    const dataList = await apiRequest(`/api/data?topic=${encodeURIComponent(topic)}`);
    renderTimeSeriesChart(topic, dataList);
  } catch (err) {
    showToast(`요약 데이터 로딩 실패: ${err.message}`, "error");
  }
}

function renderSummaryCards(summary) {
  el.summaryPeriod.textContent = summary.period || "2010 ~ 2025";
  el.summaryCount.textContent = `${summary.count}개 레코드`;
  el.summaryTotalValue.textContent = `연구 활동 누적치: ${summary.metrics.total}`;
  el.summaryAverage.textContent = `${summary.metrics.average}`;
  el.summaryRange.textContent = `최대: ${summary.metrics.max} | 최소: ${summary.metrics.min}`;
  el.summaryTrend.textContent = summary.trend || "지속 상승";
  el.summaryTrendMethod.textContent = `주요 기법: ${summary.key_methods.slice(0, 3).join(", ") || "정밀 측정"}`;
}

function renderTimeSeriesChart(topic, items) {
  const sorted = [...items].sort((a, b) => a.date.localeCompare(b.date));
  const labels = sorted.map(d => d.date.slice(0, 4));
  const values = sorted.map(d => d.value);

  const isDark = state.theme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#9ca3af" : "#475569";

  const ctx = el.timeSeriesCanvas.getContext("2d");
  
  // Gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, "rgba(99, 102, 241, 0.45)");
  gradient.addColorStop(1, "rgba(99, 102, 241, 0.0)");

  if (state.chartInstance) {
    state.chartInstance.destroy();
  }

  state.chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: `${topic} 분야 연구 지수 (논문수)`,
        data: values,
        borderColor: "#6366f1",
        borderWidth: 3,
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "#818cf8",
        pointBorderColor: "#fff",
        pointHoverRadius: 7,
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: textColor, font: { family: "Pretendard, Inter", size: 12 } }
        },
        tooltip: {
          backgroundColor: isDark ? "rgba(17, 24, 39, 0.9)" : "rgba(255, 255, 255, 0.95)",
          titleColor: isDark ? "#fff" : "#111",
          bodyColor: isDark ? "#c7d2fe" : "#4338ca",
          borderColor: "rgba(99, 102, 241, 0.3)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            afterBody: (context) => {
              const idx = context[0].dataIndex;
              const memo = sorted[idx]?.memo || "";
              return memo ? `\n💡 ${memo}` : "";
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: "Pretendard" } }
        },
        y: {
          grid: { color: gridColor },
          ticks: { color: textColor, font: { family: "Pretendard" } },
          title: { display: true, text: "연구 발표량 (지수)", color: textColor }
        }
      }
    }
  });
}

function updateChartTheme() {
  if (!state.chartInstance) return;
  const isDark = state.theme === "dark";
  const gridColor = isDark ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.06)";
  const textColor = isDark ? "#9ca3af" : "#475569";

  state.chartInstance.options.scales.x.grid.color = gridColor;
  state.chartInstance.options.scales.x.ticks.color = textColor;
  state.chartInstance.options.scales.y.grid.color = gridColor;
  state.chartInstance.options.scales.y.ticks.color = textColor;
  state.chartInstance.options.plugins.legend.labels.color = textColor;
  state.chartInstance.update();
}

// Chat UI Handlers
function appendMessage(role, text, metaTag = null) {
  const bubble = document.createElement("div");
  bubble.className = `message-bubble ${role === "user" ? "user-message" : "bot-message"}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.textContent = role === "user" ? "👤" : "🤖";

  const content = document.createElement("div");
  content.className = "message-content";

  const textDiv = document.createElement("div");
  textDiv.className = "message-text";

  if (role === "assistant" || role === "bot") {
    // Markdown parse
    textDiv.innerHTML = marked.parse(text);
  } else {
    textDiv.textContent = text;
  }

  const meta = document.createElement("div");
  meta.className = "message-meta";
  const timeSpan = document.createElement("span");
  timeSpan.className = "message-time";
  timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  meta.appendChild(timeSpan);

  if (metaTag) {
    const tagSpan = document.createElement("span");
    tagSpan.className = "message-tag";
    tagSpan.textContent = metaTag;
    meta.appendChild(tagSpan);
  }

  content.appendChild(textDiv);
  content.appendChild(meta);
  bubble.appendChild(avatar);
  bubble.appendChild(content);

  el.chatMessagesStream.appendChild(bubble);
  el.chatMessagesStream.scrollTop = el.chatMessagesStream.scrollHeight;
  return bubble;
}

function showLoadingIndicator() {
  const loading = document.createElement("div");
  loading.className = "message-bubble bot-message loading-bubble";
  loading.id = "chatLoadingBubble";
  loading.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text">
        <div class="loading-indicator">
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
          <span class="loading-dot"></span>
          <span style="font-size:0.75rem; color:var(--text-muted); margin-left:0.5rem;">데이터 요약 주입 및 Gemini 분석 중...</span>
        </div>
      </div>
    </div>
  `;
  el.chatMessagesStream.appendChild(loading);
  el.chatMessagesStream.scrollTop = el.chatMessagesStream.scrollHeight;
}

function hideLoadingIndicator() {
  const loading = document.getElementById("chatLoadingBubble");
  if (loading) loading.remove();
}

async function handleSendMessage(text) {
  const cleanText = text.trim();
  if (!cleanText) return;

  // Append user message
  appendMessage("user", cleanText);
  el.chatInputText.value = "";

  // 1. Check if the server is currently Offline
  const isCurrentlyOffline = el.apiStatusBadge.classList.contains("offline") || !navigator.onLine;
  if (isCurrentlyOffline) {
    const offlineNotice = `### ⚠️ 현재 분석을 진행하지 못하는 상태입니다.

**[분석 불가 사유]**
* **오프라인 상태**: 현재 백엔드 API 서버와의 온라인 연결이 끊어져 있는 **오프라인(Offline)** 상태입니다.
* **실시간 AI 분석 불가**: 온라인 서버 및 AI 분석 엔진(Gemini)과 연결되어 있지 않아 실시간 연구동향 분석이 불가능합니다.

**[원인 및 조치 안내]**
1. **서버 주소 설정 확인**: 우측 상단의 **⚙️ API 서버 주소 설정**을 열어 올바른 주소(Render 배포 서버: \`https://hj09m02-api.onrender.com\`)가 지정되어 있는지 확인해 주세요.
2. **콜드 스타트(Cold Start)**: Render 무료 인스턴스가 슬립 모드일 수 있습니다. 약 30~50초 후 자동으로 기상하니 잠시 후 다시 시도해 주세요.
3. **네트워크 확인**: 인터넷 연결 상태를 확인해 주세요.`;

    appendMessage("assistant", offlineNotice, "오프라인 · AI 분석 불가");
    showToast("현재 오프라인 상태이므로 온라인 AI 분석이 불가능합니다.", "error");
    return;
  }

  showLoadingIndicator();

  try {
    const payload = {
      message: cleanText,
      topic: state.currentTopic,
      conversation_id: state.currentConvId
    };

    const res = await apiRequest("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    hideLoadingIndicator();
    state.currentConvId = res.conversation_id;

    // Append AI response
    let engineLabel = "Gemini AI";
    if (res.engine_used === "smart_fallback_engine") {
      engineLabel = "오프라인 대체 · 구조화 리포트";
      showToast("온라인 AI 미연결: 시계열 데이터 기반 대체 리포트가 생성되었습니다.", "warning");
    } else if (res.engine_used) {
      engineLabel = `Gemini (${res.engine_used})`;
    }

    appendMessage("assistant", res.reply, `${state.currentTopic} 분석 · ${engineLabel}`);

    // Update suggestions if available
    if (res.suggested_topics && res.suggested_topics.length > 0) {
      updatePromptChips(res.suggested_topics);
    }
  } catch (err) {
    hideLoadingIndicator();

    // Mark status badge as offline
    el.apiStatusBadge.className = "status-indicator offline";
    el.apiStatusLabel.textContent = "Offline (연결 실패)";
    if (el.chatOfflineBanner) el.chatOfflineBanner.style.display = "flex";
    if (el.chatContextSubtitle) {
      el.chatContextSubtitle.innerHTML = '<span style="color:var(--accent-rose,#ef4444); font-weight:600;">● 오프라인 (온라인 AI 분석 불가)</span>';
    }

    const errorNotice = `### ⚠️ 현재 분석을 진행하지 못하는 상태입니다.

**[분석 불가 사유]**
* **서버 연결 실패 (오프라인)**: API 서버로부터 정상 응답을 수신하지 못했습니다. (\`${err.message}\`)
* **온라인 AI 분석 불가**: 백엔드 서버가 오프라인 상태이거나 네트워크 연결이 끊어져 실시간 AI 연구동향 분석이 불가능합니다.

**[조치 안내]**
1. 우측 상단의 **⚙️ API 서버 주소 설정**에서 배포 서버 주소(\`https://hj09m02-api.onrender.com\`)가 올바른지 확인해 주세요.
2. Render 무료 서버 슬립 모드일 수 있으니 약 30초 후 다시 시도해 주세요.
3. 인터넷 네트워크 연결 상태를 확인해 주세요.`;

    appendMessage("assistant", errorNotice, "오프라인 · AI 분석 불가");
    showToast("현재 오프라인 상태이므로 온라인 AI 분석이 불가능합니다.", "error");
  }
}

function updatePromptChips(suggestions) {
  const chips = [el.promptRecentTrend, el.promptMethodShift, el.promptKeyPapers];
  suggestions.slice(0, 3).forEach((s, idx) => {
    if (chips[idx]) {
      chips[idx].textContent = s.length > 22 ? s.slice(0, 20) + "..." : s;
      chips[idx].title = s;
      chips[idx].dataset.prompt = s;
    }
  });
}

// ========================================================
// 6. Tab 2: Time-Series Data Management (CRUD)
// ========================================================
async function loadTimeseriesTable() {
  const topicFilter = el.filterTopicSelect.value;
  const searchFilter = el.dataSearchInput.value.toLowerCase().trim();

  try {
    const endpoint = topicFilter && topicFilter !== "전체" 
      ? `/api/data?topic=${encodeURIComponent(topicFilter)}` 
      : "/api/data";
    const dataList = await apiRequest(endpoint);
    state.timeseriesData = dataList;

    let filtered = dataList;
    if (searchFilter) {
      filtered = filtered.filter(item => 
        (item.memo && item.memo.toLowerCase().includes(searchFilter)) ||
        (item.topic && item.topic.toLowerCase().includes(searchFilter)) ||
        (item.date && item.date.includes(searchFilter))
      );
    }

    renderTimeseriesRows(filtered);
    updateDataStats(filtered);
  } catch (err) {
    showToast(`시계열 데이터 조회 실패: ${err.message}`, "error");
  }
}

function updateDataStats(items) {
  const count = items.length;
  const total = items.reduce((acc, cur) => acc + Number(cur.value || 0), 0);
  const avg = count > 0 ? (total / count).toFixed(1) : 0;

  el.statFilteredCount.textContent = `${count}개`;
  el.statAverageValue.textContent = avg;
  el.statTotalValue.textContent = total.toFixed(1);
}

function renderTimeseriesRows(items) {
  el.timeseriesTableBody.innerHTML = "";

  if (!items || items.length === 0) {
    el.tableEmptyState.style.display = "block";
    return;
  }
  el.tableEmptyState.style.display = "none";

  // Sort by date desc
  const sorted = [...items].sort((a, b) => b.date.localeCompare(a.date));

  sorted.forEach(item => {
    const tr = document.createElement("tr");
    tr.dataset.id = item.id;
    tr.innerHTML = `
      <td><strong>${item.date}</strong></td>
      <td><span class="badge-topic">${item.topic || "일반"}</span></td>
      <td><span class="value-highlight">${item.value}</span></td>
      <td>${escapeHtml(item.memo || "-")}</td>
      <td style="font-size:0.78rem; color:var(--text-muted);">${(item.created_at || "").slice(0, 16).replace("T", " ")}</td>
      <td style="text-align: center;">
        <div class="table-actions">
          <button class="btn-action edit" data-id="${item.id}" title="수정">✏️ 수정</button>
          <button class="btn-action delete" data-id="${item.id}" title="삭제">🗑️ 삭제</button>
        </div>
      </td>
    `;
    el.timeseriesTableBody.appendChild(tr);
  });
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Modal Handlers
function openAddDataModal() {
  el.modalTitle.textContent = "➕ 새 시계열 데이터 추가";
  el.editItemId.value = "";
  el.formDataDate.value = new Date().toISOString().slice(0, 10);
  el.formDataTopic.value = state.currentTopic || "관절";
  el.formDataValue.value = "";
  el.formDataMemo.value = "";
  el.dataModalBackdrop.classList.add("show");
}

function openEditDataModal(id) {
  const item = state.timeseriesData.find(d => d.id === id);
  if (!item) return;

  el.modalTitle.textContent = "✏️ 시계열 데이터 수정";
  el.editItemId.value = item.id;
  el.formDataDate.value = item.date;
  el.formDataTopic.value = item.topic;
  el.formDataValue.value = item.value;
  el.formDataMemo.value = item.memo;
  el.dataModalBackdrop.classList.add("show");
}

function closeDataModal() {
  el.dataModalBackdrop.classList.remove("show");
}

async function handleSaveData(e) {
  e.preventDefault();
  const id = el.editItemId.value;
  const payload = {
    date: el.formDataDate.value,
    topic: el.formDataTopic.value,
    value: parseFloat(el.formDataValue.value),
    memo: el.formDataMemo.value.trim()
  };

  try {
    if (id) {
      // Update
      await apiRequest(`/api/data/${id}`, {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      showToast("데이터가 성공적으로 수정되었습니다.", "success");
    } else {
      // Create
      await apiRequest("/api/data", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      showToast("새 시계열 데이터가 등록되었습니다.", "success");
    }
    closeDataModal();
    loadTimeseriesTable();
    loadTopicTrends(state.currentTopic);
  } catch (err) {
    showToast(`저장 실패: ${err.message}`, "error");
  }
}

async function handleDeleteData(id) {
  if (!confirm("정말 이 데이터를 삭제하시겠습니까?")) return;

  try {
    await apiRequest(`/api/data/${id}`, { method: "DELETE" });
    showToast("데이터가 삭제되었습니다.", "success");
    loadTimeseriesTable();
    loadTopicTrends(state.currentTopic);
  } catch (err) {
    showToast(`삭제 실패: ${err.message}`, "error");
  }
}

// Export CSV / JSON
function triggerExport(format) {
  const topic = el.filterTopicSelect.value !== "전체" ? el.filterTopicSelect.value : "";
  const query = topic ? `?format=${format}&topic=${encodeURIComponent(topic)}` : `?format=${format}`;
  const url = `${state.apiBaseUrl}/api/data/export${query}`;
  window.open(url, "_blank");
  showToast(`${format.toUpperCase()} 파일 다운로드를 시작합니다.`, "info");
}

// ========================================================
// 7. Tab 3: Conversation History Management
// ========================================================
async function loadConversations() {
  try {
    const convs = await apiRequest("/api/conversations");
    renderConversationsList(convs);
  } catch (err) {
    showToast(`대화 기록 로딩 실패: ${err.message}`, "error");
  }
}

function renderConversationsList(convs) {
  el.conversationsGrid.innerHTML = "";

  if (!convs || convs.length === 0) {
    el.historyEmptyState.style.display = "block";
    return;
  }
  el.historyEmptyState.style.display = "none";

  convs.forEach(c => {
    const card = document.createElement("div");
    card.className = "conv-card glass-card";
    
    const firstUserMsg = c.messages?.find(m => m.role === "user")?.content || "대화 내용 없음";
    const lastBotMsg = c.messages?.filter(m => m.role === "assistant").pop()?.content || "";
    const previewText = lastBotMsg.replace(/[#*`]/g, "").slice(0, 110) + "...";

    card.innerHTML = `
      <div>
        <div class="conv-header">
          <h3 class="conv-title">${escapeHtml(c.title || firstUserMsg.slice(0, 25))}</h3>
          <span class="conv-topic-badge">${c.topic || "일반"}</span>
        </div>
        <p class="conv-preview">${escapeHtml(previewText)}</p>
      </div>
      <div class="conv-footer">
        <span class="conv-time">🕒 ${(c.updated_at || "").slice(0, 16).replace("T", " ")} · ${c.messages?.length || 0}개 메시지</span>
        <div class="conv-actions">
          <button class="btn btn-outline btn-load-conv" data-id="${c.id}">💬 불러오기</button>
          <button class="btn-action delete btn-del-conv" data-id="${c.id}">🗑️</button>
        </div>
      </div>
    `;
    el.conversationsGrid.appendChild(card);
  });
}

async function loadSingleConversationToChat(convId) {
  try {
    const conv = await apiRequest(`/api/conversations/${convId}`);
    state.currentConvId = conv.id;
    if (conv.topic) {
      setActiveTopic(conv.topic);
    }

    // Clear and restore messages in stream
    el.chatMessagesStream.innerHTML = "";
    conv.messages.forEach(m => {
      appendMessage(m.role, m.content);
    });

    // Switch to chat tab
    switchTab("tab-chat");
    showToast(`'${conv.title}' 대화 세션을 불러왔습니다.`, "success");
  } catch (err) {
    showToast(`대화 불러오기 실패: ${err.message}`, "error");
  }
}

async function handleDeleteConversation(convId) {
  if (!confirm("이 대화 기록을 삭제하시겠습니까?")) return;
  try {
    await apiRequest(`/api/conversations/${convId}`, { method: "DELETE" });
    showToast("대화가 삭제되었습니다.", "success");
    if (state.currentConvId === convId) {
      state.currentConvId = null;
    }
    loadConversations();
  } catch (err) {
    showToast(`대화 삭제 실패: ${err.message}`, "error");
  }
}

// ========================================================
// 8. Tab 4: Research Papers Archive
// ========================================================
async function loadPapers() {
  const topic = el.paperTopicFilter.value !== "전체" ? el.paperTopicFilter.value : "";
  const year = el.paperYearFilter.value;
  const search = el.paperSearchInput.value.trim();

  let queryParams = [];
  if (topic) queryParams.push(`topic=${encodeURIComponent(topic)}`);
  if (year) queryParams.push(`year=${year}`);
  if (search) queryParams.push(`search=${encodeURIComponent(search)}`);

  const qs = queryParams.length > 0 ? `?${queryParams.join("&")}` : "";

  try {
    const papers = await apiRequest(`/api/papers${qs}`);
    state.allPapers = papers;
    el.papersTotalCount.textContent = papers.length;
    renderPaperCards(papers);
  } catch (err) {
    showToast(`논문 목록 조회 실패: ${err.message}`, "error");
  }
}

function renderPaperCards(papers) {
  el.papersGrid.innerHTML = "";
  if (!papers || papers.length === 0) {
    el.papersGrid.innerHTML = `<div style="grid-column: 1/-1; text-align:center; padding:3rem; color:var(--text-muted);">조건에 일치하는 논문이 없습니다.</div>`;
    return;
  }

  papers.forEach(p => {
    const card = document.createElement("div");
    card.className = "paper-card glass-card";
    const speciesKor = p.species === "dog" ? "🐶 반려견" : p.species === "cat" ? "🐱 반려묘" : "🐾 공통";

    card.innerHTML = `
      <div>
        <div class="paper-card-header">
          <h3 class="paper-title">${escapeHtml(p.title)}</h3>
        </div>
        <div class="paper-badges">
          <span class="badge-year">${p.year}년</span>
          <span class="badge-species">${speciesKor}</span>
          <span class="badge-topic">${p.topic}</span>
        </div>
        <div class="paper-meta-row">
          <strong>기법:</strong> ${escapeHtml(p.method)} | <strong>표본:</strong> ${escapeHtml(p.sample_size)}
        </div>
        <p class="paper-abstract-snippet">${escapeHtml(p.summary)}</p>
      </div>
      <div class="paper-footer">
        <span class="paper-journal">${escapeHtml(p.journal || "")}</span>
        <button class="btn btn-outline btn-view-paper" data-id="${p.id}">🔍 초록 상세</button>
      </div>
    `;
    el.papersGrid.appendChild(card);
  });
}

function openPaperDetailModal(paperId) {
  const paper = state.allPapers.find(p => p.id === paperId);
  if (!paper) return;

  el.modalPaperTitle.textContent = paper.title;
  el.modalPaperSpecies.textContent = paper.species.toUpperCase();

  el.modalPaperBody.innerHTML = `
    <div style="margin-bottom: 1rem; display:flex; gap:0.5rem; flex-wrap:wrap;">
      <span class="badge-topic">${paper.topic} &gt; ${paper.subtopic}</span>
      <span class="badge-year">${paper.year}년 발행</span>
      <span class="badge-species">${paper.species === 'dog' ? '반려견' : '반려묘'} 연구</span>
    </div>
    
    <div style="background:var(--bg-card); padding:1rem; border-radius:var(--radius-md); margin-bottom:1rem; font-size:0.85rem; border:1px solid var(--border-subtle);">
      <p><strong>저널명:</strong> ${paper.journal}</p>
      <p><strong>DOI:</strong> <a href="https://doi.org/${paper.doi}" target="_blank" style="color:var(--primary-light); text-decoration:none;">${paper.doi}</a></p>
      <p><strong>표본 규모:</strong> ${paper.sample_size}</p>
      <p><strong>연구 방법:</strong> ${paper.method}</p>
    </div>

    <h4 style="font-size:0.95rem; margin-bottom:0.5rem; color:var(--primary-light);">📄 초록 및 주요 결과 요약</h4>
    <p style="font-size:0.88rem; line-height:1.6; color:var(--text-primary); margin-bottom:1rem; background:rgba(0,0,0,0.15); padding:1rem; border-radius:var(--radius-md);">
      ${escapeHtml(paper.summary)}
    </p>

    <div style="display:flex; gap:0.35rem; flex-wrap:wrap;">
      ${(paper.keywords || []).map(kw => `<span class="prompt-chip" style="font-size:0.7rem;">#${escapeHtml(kw)}</span>`).join("")}
    </div>
  `;

  el.paperModalBackdrop.classList.add("show");
}

// ========================================================
// 9. Tab Switching & Topic Handlers
// ========================================================
function switchTab(tabId) {
  state.activeTab = tabId;
  el.tabPanes.forEach(pane => {
    pane.classList.toggle("active", pane.id === tabId);
  });
  document.querySelectorAll(".tab-btn, .mobile-nav-item").forEach(btn => {
    const isActive = btn.dataset.tab === tabId;
    btn.classList.toggle("active", isActive);
    btn.setAttribute("aria-selected", isActive);
  });

  if (tabId === "tab-data") {
    loadTimeseriesTable();
  } else if (tabId === "tab-history") {
    loadConversations();
  } else if (tabId === "tab-papers") {
    loadPapers();
  }
}

function setActiveTopic(topic) {
  state.currentTopic = topic;
  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.topic === topic);
  });
  loadTopicTrends(topic);
}

// ========================================================
// 10. Event Listeners Initialization
// ========================================================
function setupEventListeners() {
  // Theme Toggle
  el.themeToggleBtn.addEventListener("click", () => {
    const nextTheme = state.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
  });

  // View Mode Toggle (PC <-> Mobile)
  if (el.btnToggleViewMode) {
    el.btnToggleViewMode.addEventListener("click", () => {
      const isMobileScreen = window.innerWidth <= 768;
      const isCurrentlyMobile = state.viewMode === "mobile" || (state.viewMode === "auto" && isMobileScreen);
      const nextMode = isCurrentlyMobile ? "pc" : "mobile";
      applyViewMode(nextMode);
      showToast(nextMode === "mobile" ? "📱 모바일 화면 모드로 전환되었습니다." : "🖥️ PC 화면 모드로 전환되었습니다.", "info");
    });
  }

  // Mobile Bottom Navigation Tabs
  if (el.mobileBottomNav) {
    el.mobileBottomNav.addEventListener("click", e => {
      const item = e.target.closest(".mobile-nav-item");
      if (item && item.dataset.tab) {
        switchTab(item.dataset.tab);
      }
    });
  }

  // Window resize to update view mode UI
  window.addEventListener("resize", debounce(() => {
    updateViewModeUI();
  }, 150));

  // Navigation Tabs
  el.navTabs.addEventListener("click", e => {
    const btn = e.target.closest(".tab-btn");
    if (btn) switchTab(btn.dataset.tab);
  });

  // Topic Chips
  el.topicChipsContainer.addEventListener("click", e => {
    const chip = e.target.closest(".chip-btn");
    if (chip) setActiveTopic(chip.dataset.topic);
  });

  // Chat Form Submit
  el.chatInputForm.addEventListener("submit", e => {
    e.preventDefault();
    handleSendMessage(el.chatInputText.value);
  });

  // Prompt Chips
  document.querySelectorAll(".prompt-chip").forEach(btn => {
    btn.addEventListener("click", () => {
      const promptText = btn.dataset.prompt || btn.textContent.replace(/^[🔥💡📖]\s*/, "");
      handleSendMessage(promptText);
    });
  });

  // Clear Chat Button
  el.btnClearChat.addEventListener("click", () => {
    state.currentConvId = null;
    el.chatMessagesStream.innerHTML = `
      <div class="message-bubble bot-message">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="message-text">
            <p>새로운 대화 세션이 시작되었습니다. 🐾</p>
            <p>현재 <strong>[${state.currentTopic}]</strong> 분야의 시계열 연구동향 요약이 주입되어 있습니다. 질문해 주세요!</p>
          </div>
          <div class="message-meta">
            <span class="message-time">방금 전</span>
            <span class="message-tag">신규 세션</span>
          </div>
        </div>
      </div>
    `;
    showToast("새 대화 세션이 시작되었습니다.", "info");
  });

  // Refresh Summary Button
  el.btnRefreshSummary.addEventListener("click", () => {
    loadTopicTrends(state.currentTopic);
    showToast(`${state.currentTopic} 요약 및 차트 갱신 완료`, "success");
  });

  // Tab 2 (Data CRUD)
  el.filterTopicSelect.addEventListener("change", loadTimeseriesTable);
  el.dataSearchInput.addEventListener("input", debounce(loadTimeseriesTable, 300));
  el.btnOpenAddModal.addEventListener("click", openAddDataModal);
  el.btnCloseDataModal.addEventListener("click", closeDataModal);
  el.btnCancelDataModal.addEventListener("click", closeDataModal);
  el.dataForm.addEventListener("submit", handleSaveData);

  el.timeseriesTableBody.addEventListener("click", e => {
    const editBtn = e.target.closest(".btn-action.edit");
    const delBtn = e.target.closest(".btn-action.delete");
    if (editBtn) openEditDataModal(editBtn.dataset.id);
    if (delBtn) handleDeleteData(delBtn.dataset.id);
  });

  // Export Buttons
  el.btnExportCsv.addEventListener("click", () => triggerExport("csv"));
  el.btnExportJson.addEventListener("click", () => triggerExport("json"));

  // Tab 3 (Conversations)
  el.btnRefreshHistory.addEventListener("click", loadConversations);
  el.btnGoToChat.addEventListener("click", () => switchTab("tab-chat"));
  el.conversationsGrid.addEventListener("click", e => {
    const loadBtn = e.target.closest(".btn-load-conv");
    const delBtn = e.target.closest(".btn-del-conv");
    if (loadBtn) loadSingleConversationToChat(loadBtn.dataset.id);
    if (delBtn) handleDeleteConversation(delBtn.dataset.id);
  });

  // Tab 4 (Papers)
  el.paperTopicFilter.addEventListener("change", loadPapers);
  el.paperYearFilter.addEventListener("change", loadPapers);
  el.paperSearchInput.addEventListener("input", debounce(loadPapers, 300));
  el.papersGrid.addEventListener("click", e => {
    const btn = e.target.closest(".btn-view-paper");
    if (btn) openPaperDetailModal(btn.dataset.id);
  });
  el.btnClosePaperModal.addEventListener("click", () => el.paperModalBackdrop.classList.remove("show"));

  // Server Config Modal
  el.btnServerConfig.addEventListener("click", () => {
    el.serverBaseUrlInput.value = state.apiBaseUrl;
    el.serverModalBackdrop.classList.add("show");
  });
  el.btnCloseServerModal.addEventListener("click", () => el.serverModalBackdrop.classList.remove("show"));
  el.btnSaveServerUrl.addEventListener("click", () => {
    let newUrl = el.serverBaseUrlInput.value.trim().replace(/\/+$/, "");
    if (window.location.protocol === "https:" && newUrl.startsWith("http://")) {
      showToast("⚠️ HTTPS 환경에서는 http:// 주소가 보안상 차단됩니다. https:// 주소를 사용해주세요.", "error");
      return;
    }
    if (newUrl.includes("samsung-stock")) {
      showToast("⚠️ 다른 프로젝트(삼성 주식)의 주소입니다. 현재 프로젝트 주소(hj09m02-api)로 자동 복원합니다.", "warning");
      newUrl = PROD_API_URL;
      el.serverBaseUrlInput.value = PROD_API_URL;
    }
    state.apiBaseUrl = newUrl;
    if (newUrl) {
      localStorage.setItem("pet_nav_api_base", newUrl);
    } else {
      localStorage.removeItem("pet_nav_api_base");
    }
    el.serverModalBackdrop.classList.remove("show");
    updateSwaggerDocsUrl();
    checkApiHealth();
    loadTopicTrends(state.currentTopic);
    showToast("API 서버 주소가 업데이트되었습니다.", "success");
  });
  el.btnResetServerUrl.addEventListener("click", () => {
    localStorage.removeItem("pet_nav_api_base");
    state.apiBaseUrl = getDefaultApiBaseUrl();
    el.serverBaseUrlInput.value = state.apiBaseUrl;
    el.serverModalBackdrop.classList.remove("show");
    updateSwaggerDocsUrl();
    checkApiHealth();
    loadTopicTrends(state.currentTopic);
    showToast("기본 추천 주소로 복원되었습니다.", "info");
  });

  // Preset quick buttons
  if (el.btnPresetRender) {
    el.btnPresetRender.addEventListener("click", () => {
      el.serverBaseUrlInput.value = PROD_API_URL;
    });
  }
  if (el.btnPresetProxy) {
    el.btnPresetProxy.addEventListener("click", () => {
      el.serverBaseUrlInput.value = "";
    });
  }
  if (el.btnPresetLocal) {
    el.btnPresetLocal.addEventListener("click", () => {
      if (window.location.protocol === "https:") {
        showToast("⚠️ HTTPS 페이지에서는 로컬 http:// 주소가 브라우저 보안에 의해 차단될 수 있습니다.", "warning");
      }
      el.serverBaseUrlInput.value = "http://127.0.0.1:8000";
    });
  }

  // Banner Check Server Button
  if (el.btnBannerCheckServer) {
    el.btnBannerCheckServer.addEventListener("click", () => {
      el.serverBaseUrlInput.value = state.apiBaseUrl;
      el.serverModalBackdrop.classList.add("show");
    });
  }

  // Banner Retry Connection Button
  if (el.btnBannerRetry) {
    el.btnBannerRetry.addEventListener("click", async () => {
      showToast("서버 연결을 다시 확인 중입니다...", "info");
      const ok = await checkApiHealth(0);
      if (ok) {
        showToast("클라우드 서버 연결 성공!", "success");
        await loadTopicTrends(state.currentTopic);
      } else {
        showToast("서버가 아직 준비 중입니다. 잠시 후 다시 시도해주세요.", "warning");
      }
    });
  }

  // Close modals on outside click
  window.addEventListener("click", e => {
    if (e.target.classList.contains("modal-backdrop")) {
      e.target.classList.remove("show");
    }
  });
}

function debounce(func, wait) {
  let timeout;
  return function(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// ========================================================
// 11. Application Bootstrap
// ========================================================
document.addEventListener("DOMContentLoaded", async () => {
  applyTheme(state.theme);
  applyViewMode(state.viewMode);
  setupEventListeners();
  updateSwaggerDocsUrl();

  // Initial connection check
  await checkApiHealth();

  // Load initial topic data (관절)
  await loadTopicTrends(state.currentTopic);
});
