// 텀프로젝트 발표자료 생성 — pptxgenjs
const PptxGenJS = require("pptxgenjs");
const path = require("path");
const fs = require("fs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 inches
pptx.title = "화장품 MES JSSP 최적화 — 텀프로젝트";
pptx.author = "충북대 산업인공지능 대학원";

// === 색상 팔레트 (Midnight Executive) ===
const NAVY = "1E2761";
const ICE  = "CADCFC";
const WHITE = "FFFFFF";
const ACCENT = "F96167"; // 강조
const DARK_TEXT = "212121";
const MUTED = "5A6B8C";

const FONT_H = "Georgia";
const FONT_B = "Calibri";

const RESULTS = path.resolve(__dirname, "results");

// ===== 슬라이드 1: 타이틀 =====
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  // 좌측 색 블록 (모티프)
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: ACCENT },
  });
  s.addText("화장품 제조 MES의\n반제품–완제품 통합 생산 스케줄링", {
    x: 0.9, y: 1.8, w: 11.5, h: 1.8,
    fontFace: FONT_H, fontSize: 36, bold: true, color: WHITE,
    valign: "middle",
  });
  s.addText("Job Shop Scheduling Problem (JSSP) 기반 최적화 모델 개발", {
    x: 0.9, y: 3.7, w: 11.5, h: 0.6,
    fontFace: FONT_B, fontSize: 20, color: ICE, italic: true,
  });
  s.addText("제조데이터 분석과 최적화  |  12주차 텀프로젝트", {
    x: 0.9, y: 5.4, w: 11.5, h: 0.4,
    fontFace: FONT_B, fontSize: 14, color: ICE,
  });
  s.addText("발표자: (학번 / 성명)\n지도교수: 김한진", {
    x: 0.9, y: 5.95, w: 11.5, h: 0.9,
    fontFace: FONT_B, fontSize: 13, color: WHITE,
  });
  s.addText("충북대학교 산업인공지능 대학원", {
    x: 0.9, y: 6.85, w: 11.5, h: 0.35,
    fontFace: FONT_B, fontSize: 11, color: ICE,
  });
}

// === 공통 헬퍼 — 라이트 슬라이드 헤더 ===
function addHeader(s, title, kicker) {
  s.background = { color: WHITE };
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 0.25, h: 7.5, fill: { color: NAVY },
  });
  if (kicker) {
    s.addText(kicker, {
      x: 0.6, y: 0.4, w: 12.5, h: 0.3,
      fontFace: FONT_B, fontSize: 11, color: ACCENT, bold: true,
      charSpacing: 2,
    });
  }
  s.addText(title, {
    x: 0.6, y: 0.7, w: 12.5, h: 0.7,
    fontFace: FONT_H, fontSize: 28, bold: true, color: NAVY,
  });
}

function addFooter(s, n, total) {
  s.addText(`${n} / ${total}`, {
    x: 12.3, y: 7.15, w: 0.8, h: 0.3,
    fontFace: FONT_B, fontSize: 9, color: MUTED, align: "right",
  });
  s.addText("MES JSSP 최적화", {
    x: 0.5, y: 7.15, w: 4, h: 0.3,
    fontFace: FONT_B, fontSize: 9, color: MUTED,
  });
}

const TOTAL_SLIDES = 16;

// ===== 슬라이드 2: 목차 =====
{
  const s = pptx.addSlide();
  addHeader(s, "Contents", "AGENDA");
  const items = [
    ["01", "프로젝트 배경 및 필요성"],
    ["02", "프로젝트 목표"],
    ["03", "MES 공정의 JSSP 매핑"],
    ["04", "제약 조건 및 수학적 모델"],
    ["05", "적용 방법론 (3종)"],
    ["06", "시스템 아키텍처"],
    ["07", "실험 결과 — Gantt"],
    ["08", "실험 결과 — KPI 비교"],
    ["09", "분석 및 인사이트"],
    ["10", "기대 효과 및 향후 계획"],
  ];
  items.forEach((it, i) => {
    const col = i < 5 ? 0 : 1;
    const row = i % 5;
    const x = 0.9 + col * 6.0;
    const y = 1.7 + row * 0.95;
    s.addShape(pptx.ShapeType.ellipse, {
      x: x, y: y + 0.05, w: 0.7, h: 0.7,
      fill: { color: NAVY }, line: { color: NAVY },
    });
    s.addText(it[0], {
      x: x, y: y + 0.05, w: 0.7, h: 0.7,
      fontFace: FONT_H, fontSize: 16, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(it[1], {
      x: x + 0.95, y: y + 0.1, w: 4.8, h: 0.6,
      fontFace: FONT_B, fontSize: 16, color: DARK_TEXT, valign: "middle",
    });
  });
  addFooter(s, 2, TOTAL_SLIDES);
}

// ===== 슬라이드 3: 배경 및 필요성 =====
{
  const s = pptx.addSlide();
  addHeader(s, "프로젝트 배경 및 필요성", "01 BACKGROUND");
  // 좌: AS-IS, 우: TO-BE
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.6, y: 1.7, w: 6.0, h: 5.0, fill: { color: "F5F5F5" }, line: { color: "DDDDDD" },
    rectRadius: 0.1,
  });
  s.addText("AS-IS  ·  현황과 문제점", {
    x: 0.8, y: 1.85, w: 5.6, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: ACCENT,
  });
  s.addText([
    { text: "•  현장 반장 경험 + 수기 보드 기반 스케줄링\n", options: { fontSize: 13 } },
    { text: "•  반제품 시험 합격 시점을 사람이 확인 후 완제품 투입\n", options: { fontSize: 13 } },
    { text: "•  시험실(QC) FIFO 운영으로 후공정 병목 발생\n", options: { fontSize: 13 } },
    { text: "•  믹서·충전 PLC 지시 전환 시 idle time 누적\n", options: { fontSize: 13 } },
    { text: "•  저장조/숙성조 충돌을 사후 인지 → 배출 지연\n", options: { fontSize: 13 } },
    { text: "•  What-if 분석 불가 — 신제품/라인 증설 의사결정 어려움", options: { fontSize: 13 } },
  ], {
    x: 0.85, y: 2.4, w: 5.5, h: 4.2,
    fontFace: FONT_B, color: DARK_TEXT,
    paraSpaceAfter: 8,
  });

  s.addShape(pptx.ShapeType.roundRect, {
    x: 6.85, y: 1.7, w: 6.0, h: 5.0, fill: { color: NAVY }, line: { color: NAVY },
    rectRadius: 0.1,
  });
  s.addText("TO-BE  ·  본 프로젝트의 방향", {
    x: 7.05, y: 1.85, w: 5.6, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: ICE,
  });
  s.addText([
    { text: "•  JSSP 기반 자동 스케줄링으로 객관·재현 가능\n", options: { fontSize: 13 } },
    { text: "•  BOM 종속·저장조 용량을 제약식으로 사전 반영\n", options: { fontSize: 13 } },
    { text: "•  시험실 우선순위를 후공정 영향도로 산출\n", options: { fontSize: 13 } },
    { text: "•  SimPy 가상공장으로 What-if 즉시 수행\n", options: { fontSize: 13 } },
    { text: "•  현장 운영팀 의사결정 시간 단축\n", options: { fontSize: 13 } },
    { text: "•  Makespan −15% / 시험실 대기 −50% / 가동률 +10%p (목표)", options: { fontSize: 13, bold: true, color: ACCENT } },
  ], {
    x: 7.1, y: 2.4, w: 5.5, h: 4.2,
    fontFace: FONT_B, color: WHITE,
    paraSpaceAfter: 8,
  });
  addFooter(s, 3, TOTAL_SLIDES);
}

// ===== 슬라이드 4: 프로젝트 목표 =====
{
  const s = pptx.addSlide();
  addHeader(s, "프로젝트 목표", "02 OBJECTIVES");
  const goals = [
    ["1", "모델링", "MES 반제품/완제품 공정을\nJSSP로 정형화", NAVY],
    ["2", "최적화", "Makespan + Tardiness\n가중합 최소화", ACCENT],
    ["3", "비교평가", "MILP / Dispatching / DRL\n세 기법 성능 분석", "55A467"],
    ["4", "현장적용", "Gantt 시각화 →\n수기 대비 정량 개선 평가", "8172B2"],
  ];
  goals.forEach((g, i) => {
    const x = 0.6 + i * 3.1;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 1.9, w: 2.9, h: 4.8,
      fill: { color: "F5F5F5" }, line: { color: g[3], width: 2 },
      rectRadius: 0.1,
    });
    s.addShape(pptx.ShapeType.ellipse, {
      x: x + 1.05, y: 2.15, w: 0.8, h: 0.8,
      fill: { color: g[3] }, line: { color: g[3] },
    });
    s.addText(g[0], {
      x: x + 1.05, y: 2.15, w: 0.8, h: 0.8,
      fontFace: FONT_H, fontSize: 22, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(g[1], {
      x: x, y: 3.15, w: 2.9, h: 0.5,
      fontFace: FONT_H, fontSize: 18, bold: true, color: g[3],
      align: "center",
    });
    s.addText(g[2], {
      x: x + 0.2, y: 3.8, w: 2.5, h: 2.5,
      fontFace: FONT_B, fontSize: 13, color: DARK_TEXT,
      align: "center", valign: "top",
    });
  });
  addFooter(s, 4, TOTAL_SLIDES);
}

// ===== 슬라이드 5: JSSP 매핑 =====
{
  const s = pptx.addSlide();
  addHeader(s, "MES 공정의 JSSP 매핑", "03 PROBLEM DEFINITION");
  // 매핑 표
  s.addTable([
    [
      { text: "JSSP", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "MES 매핑", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    ],
    [
      { text: "Job", options: { bold: true } },
      "반제품 지시 (BULK) / 완제품 지시 (FG)",
    ],
    [
      { text: "Machine", options: { bold: true } },
      "저울, 믹서(PLC), 시험실, 저장조/숙성조, 충전(PLC), 포장 라인",
    ],
    [
      { text: "Operation", options: { bold: true } },
      "각 지시를 구성하는 단위 작업",
    ],
  ], {
    x: 0.6, y: 1.7, w: 12.2, colW: [2.0, 10.2],
    fontFace: FONT_B, fontSize: 13, color: DARK_TEXT,
    border: { type: "solid", color: "DDDDDD", pt: 0.5 },
    rowH: 0.55,
  });

  // 라우팅 다이어그램
  s.addText("Routing", {
    x: 0.6, y: 3.9, w: 4, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY,
  });

  // BULK 라우팅
  const bulkSteps = ["SCALE\n(저울)", "MIXER\n(믹서 PLC)", "QC_BULK\n(시험)", "STORAGE\n(저장조)"];
  s.addText("BULK", {
    x: 0.6, y: 4.5, w: 1.0, h: 0.6, fontFace: FONT_B, fontSize: 14, bold: true,
    color: ACCENT, valign: "middle",
  });
  bulkSteps.forEach((step, i) => {
    const x = 1.7 + i * 2.6;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 4.4, w: 2.2, h: 0.85,
      fill: { color: NAVY }, line: { color: NAVY },
      rectRadius: 0.05,
    });
    s.addText(step, {
      x: x, y: 4.4, w: 2.2, h: 0.85,
      fontFace: FONT_B, fontSize: 11, color: WHITE, bold: true,
      align: "center", valign: "middle",
    });
    if (i < bulkSteps.length - 1) {
      s.addText("▶", {
        x: x + 2.2, y: 4.4, w: 0.4, h: 0.85,
        fontFace: FONT_B, fontSize: 16, color: NAVY,
        align: "center", valign: "middle",
      });
    }
  });

  // FG 라우팅
  const fgSteps = ["FILLER\n(충전 PLC)", "QC_FG\n(시험)", "PACKAGING\n(포장)"];
  s.addText("FG", {
    x: 0.6, y: 5.6, w: 1.0, h: 0.6, fontFace: FONT_B, fontSize: 14, bold: true,
    color: ACCENT, valign: "middle",
  });
  fgSteps.forEach((step, i) => {
    const x = 1.7 + i * 2.6;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 5.5, w: 2.2, h: 0.85,
      fill: { color: "8172B2" }, line: { color: "8172B2" },
      rectRadius: 0.05,
    });
    s.addText(step, {
      x: x, y: 5.5, w: 2.2, h: 0.85,
      fontFace: FONT_B, fontSize: 11, color: WHITE, bold: true,
      align: "center", valign: "middle",
    });
    if (i < fgSteps.length - 1) {
      s.addText("▶", {
        x: x + 2.2, y: 5.5, w: 0.4, h: 0.85,
        fontFace: FONT_B, fontSize: 16, color: "8172B2",
        align: "center", valign: "middle",
      });
    }
  });

  // BOM 화살표
  s.addText("BOM 종속:  FG 의 FILLER 시작 ≥ 해당 BULK 의 QC_BULK 종료", {
    x: 0.6, y: 6.55, w: 12.2, h: 0.4,
    fontFace: FONT_B, fontSize: 12, italic: true, color: ACCENT, bold: true,
  });

  addFooter(s, 5, TOTAL_SLIDES);
}

// ===== 슬라이드 6: 제약 조건 =====
{
  const s = pptx.addSlide();
  addHeader(s, "제약 조건 (6 종)", "04 CONSTRAINTS");
  const constraints = [
    ["①", "선후행", "Job 내 Operation 은 정의된 순서대로만 진행"],
    ["②", "비선점", "믹서/충전 PLC 가동 시작 후 중단 불가"],
    ["③", "기계 용량", "저울·믹서·시험실·충전은 동시 1 Job 만 처리"],
    ["④", "BOM 종속", "FG 충전 시작 ≥ 해당 BULK 의 시험 합격"],
    ["⑤", "저장조 용량", "동시 점유 반제품 ≤ 저장조 수, 숙성시간 부여"],
    ["⑥", "라벨 동기", "원료/계량/반제품 라벨 스캔으로 batch 추적"],
  ];
  constraints.forEach((c, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.6 + col * 6.2;
    const y = 1.8 + row * 1.5;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: y, w: 6.0, h: 1.3, fill: { color: "F5F5F5" }, line: { color: "DDDDDD" },
      rectRadius: 0.08,
    });
    s.addShape(pptx.ShapeType.ellipse, {
      x: x + 0.2, y: y + 0.3, w: 0.7, h: 0.7,
      fill: { color: NAVY }, line: { color: NAVY },
    });
    s.addText(c[0], {
      x: x + 0.2, y: y + 0.3, w: 0.7, h: 0.7,
      fontFace: FONT_H, fontSize: 18, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(c[1], {
      x: x + 1.05, y: y + 0.2, w: 4.8, h: 0.45,
      fontFace: FONT_H, fontSize: 15, bold: true, color: NAVY,
    });
    s.addText(c[2], {
      x: x + 1.05, y: y + 0.65, w: 4.8, h: 0.6,
      fontFace: FONT_B, fontSize: 11, color: DARK_TEXT,
    });
  });
  s.addText("※ 강의의 JSSP 3대 제약(①②③) + 본 공정 고유 확장(④⑤⑥)", {
    x: 0.6, y: 6.8, w: 12.5, h: 0.3,
    fontFace: FONT_B, fontSize: 11, italic: true, color: MUTED,
  });
  addFooter(s, 6, TOTAL_SLIDES);
}

// ===== 슬라이드 7: 수학적 모델 (MILP) =====
{
  const s = pptx.addSlide();
  addHeader(s, "수학적 모델 — MILP 정식화", "04 MATHEMATICAL MODEL");
  // 좌: 변수
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.6, y: 1.7, w: 4.0, h: 5.0, fill: { color: "F5F5F5" }, line: { color: "DDDDDD" },
    rectRadius: 0.08,
  });
  s.addText("Decision Variables", {
    x: 0.8, y: 1.85, w: 3.6, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: NAVY,
  });
  s.addText([
    { text: "s_o", options: { bold: true, fontFace: "Consolas" } },
    { text: "    Operation o 의 시작시점\n\n", options: {} },
    { text: "x_{o,m}", options: { bold: true, fontFace: "Consolas" } },
    { text: " 1 if o → m (assign)\n\n", options: {} },
    { text: "y_{o,o',m}", options: { bold: true, fontFace: "Consolas" } },
    { text: " 1 if o ≺ o' on m\n\n", options: {} },
    { text: "C_max", options: { bold: true, fontFace: "Consolas" } },
    { text: "  Makespan\n\n", options: {} },
    { text: "T_j", options: { bold: true, fontFace: "Consolas" } },
    { text: "    Tardiness of Job j", options: {} },
  ], {
    x: 0.8, y: 2.3, w: 3.6, h: 4.2, fontSize: 12, color: DARK_TEXT,
  });

  // 우: 제약 & 목적함수
  s.addShape(pptx.ShapeType.roundRect, {
    x: 4.85, y: 1.7, w: 8.0, h: 5.0, fill: { color: NAVY }, line: { color: NAVY },
    rectRadius: 0.08,
  });
  s.addText("Objective & Constraints", {
    x: 5.05, y: 1.85, w: 7.6, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: ICE,
  });
  s.addText("min   α·C_max  +  β·Σⱼ T_j", {
    x: 5.05, y: 2.35, w: 7.6, h: 0.5,
    fontFace: "Consolas", fontSize: 18, bold: true, color: ACCENT,
  });
  s.addText([
    { text: "C1. ", options: { bold: true, color: ICE } },
    { text: "Σ_m x_{o,m} = 1                       ∀o\n", options: {} },
    { text: "C3. ", options: { bold: true, color: ICE } },
    { text: "s_{o_{i+1}} ≥ s_{o_i} + p_{o_i}        (선후행)\n", options: {} },
    { text: "C4. ", options: { bold: true, color: ICE } },
    { text: "s_{o'} ≥ s_o + p_o − H(1−y) − H(2−xᵢ−xⱼ)   (Big-M)\n", options: {} },
    { text: "C5. ", options: { bold: true, color: ICE } },
    { text: "s_{o_{FG,0}} ≥ s_{o_{BULK,last}} + p     (BOM)\n", options: {} },
    { text: "C7. ", options: { bold: true, color: ICE } },
    { text: "C_max ≥ s_{j,last} + p_{j,last}        ∀j\n", options: {} },
    { text: "C7. ", options: { bold: true, color: ICE } },
    { text: "T_j ≥ s_{j,last} + p_{j,last} − d_j    ∀j", options: {} },
  ], {
    x: 5.05, y: 3.0, w: 7.7, h: 3.6,
    fontFace: "Consolas", fontSize: 12, color: WHITE,
    paraSpaceAfter: 6,
  });
  addFooter(s, 7, TOTAL_SLIDES);
}

// ===== 슬라이드 8: 3가지 적용 방법론 =====
{
  const s = pptx.addSlide();
  addHeader(s, "적용 방법론 (3 종 비교)", "05 METHODOLOGY");
  const methods = [
    {
      tag: "MILP",
      title: "혼합정수계획법",
      lib: "PuLP + CBC",
      pros: "전역 최적해\n벤치마크 기준",
      cons: "대규모 인스턴스\n연산시간 폭증",
      color: NAVY,
    },
    {
      tag: "DISPATCH",
      title: "Dispatching Rules",
      lib: "SimPy + 5종 규칙",
      pros: "실시간 (ms 단위)\n구현·해석 용이",
      cons: "최적성 보장 X\n규칙 의존적",
      color: ACCENT,
    },
    {
      tag: "DRL",
      title: "강화학습",
      lib: "PPO + Action Masking",
      pros: "대규모 확장\n학습 후 빠른 추론",
      cons: "학습 비용 高\n수렴 불안정",
      color: "55A467",
    },
  ];
  methods.forEach((m, i) => {
    const x = 0.6 + i * 4.2;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 1.7, w: 4.0, h: 5.2, fill: { color: WHITE }, line: { color: m.color, width: 2 },
      rectRadius: 0.08,
    });
    s.addShape(pptx.ShapeType.rect, {
      x: x, y: 1.7, w: 4.0, h: 0.7, fill: { color: m.color }, line: { color: m.color },
    });
    s.addText(m.tag, {
      x: x, y: 1.7, w: 4.0, h: 0.7,
      fontFace: FONT_H, fontSize: 16, bold: true, color: WHITE,
      align: "center", valign: "middle", charSpacing: 2,
    });
    s.addText(m.title, {
      x: x + 0.2, y: 2.55, w: 3.6, h: 0.45,
      fontFace: FONT_H, fontSize: 18, bold: true, color: m.color,
    });
    s.addText(m.lib, {
      x: x + 0.2, y: 3.0, w: 3.6, h: 0.4,
      fontFace: "Consolas", fontSize: 12, color: DARK_TEXT, italic: true,
    });
    s.addText("Pros", {
      x: x + 0.2, y: 3.6, w: 3.6, h: 0.3,
      fontFace: FONT_B, fontSize: 11, bold: true, color: "55A467",
    });
    s.addText(m.pros, {
      x: x + 0.2, y: 3.9, w: 3.6, h: 1.0,
      fontFace: FONT_B, fontSize: 12, color: DARK_TEXT,
    });
    s.addText("Cons", {
      x: x + 0.2, y: 5.0, w: 3.6, h: 0.3,
      fontFace: FONT_B, fontSize: 11, bold: true, color: ACCENT,
    });
    s.addText(m.cons, {
      x: x + 0.2, y: 5.3, w: 3.6, h: 1.0,
      fontFace: FONT_B, fontSize: 12, color: DARK_TEXT,
    });
  });
  addFooter(s, 8, TOTAL_SLIDES);
}

// ===== 슬라이드 9: 시스템 아키텍처 =====
{
  const s = pptx.addSlide();
  addHeader(s, "시스템 아키텍처", "06 ARCHITECTURE");
  // 7개 모듈 박스
  const modules = [
    ["Loader", "MES CSV / 합성 / 벤치마크\n→ Instance"],
    ["Domain", "Job / Operation\nMachine / Schedule"],
    ["Solver", "MILP / Dispatching\nDRL (PPO)"],
    ["Simulator", "SimPy DES\n(가상 공장)"],
    ["Evaluator", "Makespan / Tardiness\nUtilization / Time"],
    ["Visualizer", "Gantt 차트\nKPI 비교 그래프"],
  ];
  modules.forEach((m, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.7 + col * 4.2;
    const y = 1.9 + row * 1.7;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: y, w: 3.9, h: 1.45, fill: { color: NAVY }, line: { color: NAVY },
      rectRadius: 0.08,
    });
    s.addText(m[0], {
      x: x + 0.15, y: y + 0.1, w: 3.6, h: 0.45,
      fontFace: FONT_H, fontSize: 16, bold: true, color: WHITE,
    });
    s.addText(m[1], {
      x: x + 0.15, y: y + 0.6, w: 3.6, h: 0.8,
      fontFace: FONT_B, fontSize: 11, color: ICE,
    });
  });
  // 데이터 플로우 화살표
  s.addText("Data Flow:   Raw  →  Instance  →  Schedule  →  ExecutionLog  →  KPI  →  Gantt", {
    x: 0.7, y: 5.4, w: 12.2, h: 0.5,
    fontFace: FONT_B, fontSize: 14, bold: true, color: NAVY,
    align: "center",
  });
  s.addText("Tech Stack:   Python 3.14  ·  SimPy 4  ·  PuLP+CBC  ·  matplotlib  ·  Gymnasium+sb3-contrib (DRL)", {
    x: 0.7, y: 6.0, w: 12.2, h: 0.5,
    fontFace: "Consolas", fontSize: 12, color: MUTED,
    align: "center",
  });
  addFooter(s, 9, TOTAL_SLIDES);
}

// ===== 슬라이드 10: 실험 환경 =====
{
  const s = pptx.addSlide();
  addHeader(s, "실험 환경 — 합성 인스턴스", "07 EXPERIMENT SETUP");
  // 좌: 인스턴스 명세
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.6, y: 1.7, w: 6.0, h: 5.0, fill: { color: "F5F5F5" }, line: { color: "DDDDDD" },
    rectRadius: 0.08,
  });
  s.addText("Instance: inst_b3_f3_s42", {
    x: 0.8, y: 1.85, w: 5.6, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY,
  });
  s.addText([
    { text: "Jobs:    ", options: { bold: true, fontFace: "Consolas" } },
    { text: "6 (BULK 3 + FG 3)\n", options: {} },
    { text: "BOM:     ", options: { bold: true, fontFace: "Consolas" } },
    { text: "FG-i ⟵ BULK-(i mod 3)\n\n", options: {} },
    { text: "Machines: 10\n", options: { bold: true } },
    { text: "  · SCALE   × 2\n", options: {} },
    { text: "  · MIXER   × 2\n", options: {} },
    { text: "  · QC_BULK × 1\n", options: {} },
    { text: "  · STORAGE × 2\n", options: {} },
    { text: "  · FILLER  × 1\n", options: {} },
    { text: "  · QC_FG   × 1\n", options: {} },
    { text: "  · PACKAGING × 1\n\n", options: {} },
    { text: "Horizon (Big-M): 1804 min", options: { fontFace: "Consolas", color: ACCENT, bold: true } },
  ], {
    x: 0.85, y: 2.35, w: 5.5, h: 4.3,
    fontFace: FONT_B, fontSize: 13, color: DARK_TEXT,
  });

  // 우: 비교 솔버
  s.addShape(pptx.ShapeType.roundRect, {
    x: 6.85, y: 1.7, w: 6.0, h: 5.0, fill: { color: NAVY }, line: { color: NAVY },
    rectRadius: 0.08,
  });
  s.addText("비교 대상 솔버 (4종)", {
    x: 7.05, y: 1.85, w: 5.6, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: ICE,
  });
  const solvers = [
    ["1.", "DISP-FIFO", "도착 순서대로 처리 (기준선)"],
    ["2.", "DISP-SPT",  "처리시간 짧은 Op 우선"],
    ["3.", "DISP-EDD",  "납기 빠른 Job 우선"],
    ["4.", "MILP",      "PuLP + CBC, time_limit=30s"],
  ];
  solvers.forEach((sv, i) => {
    const y = 2.45 + i * 0.95;
    s.addText(sv[0], {
      x: 7.1, y: y, w: 0.4, h: 0.5,
      fontFace: FONT_H, fontSize: 16, bold: true, color: ACCENT,
    });
    s.addText(sv[1], {
      x: 7.55, y: y, w: 2.5, h: 0.4,
      fontFace: "Consolas", fontSize: 14, bold: true, color: WHITE,
    });
    s.addText(sv[2], {
      x: 7.55, y: y + 0.42, w: 5.2, h: 0.4,
      fontFace: FONT_B, fontSize: 11, color: ICE, italic: true,
    });
  });
  addFooter(s, 10, TOTAL_SLIDES);
}

// ===== 슬라이드 11: 실험 결과 1 — MILP Gantt =====
{
  const s = pptx.addSlide();
  addHeader(s, "실험 결과 ① — MILP 스케줄 (Gantt)", "07 RESULTS");
  s.addImage({
    path: path.join(RESULTS, "gantt_MILP.png"),
    x: 0.55, y: 1.6, w: 12.2, h: 5.0,
  });
  s.addText("Makespan = 380.1 min  ·  Mean Tardiness = 0.0  ·  Solve = 0.20 s", {
    x: 0.55, y: 6.7, w: 12.2, h: 0.4,
    fontFace: FONT_B, fontSize: 13, bold: true, color: NAVY, align: "center",
  });
  addFooter(s, 11, TOTAL_SLIDES);
}

// ===== 슬라이드 12: 실험 결과 2 — Dispatching 비교 =====
{
  const s = pptx.addSlide();
  addHeader(s, "실험 결과 ② — Dispatching Rules 비교", "07 RESULTS");
  s.addImage({
    path: path.join(RESULTS, "gantt_DISP-FIFO.png"),
    x: 0.4, y: 1.5, w: 6.4, h: 2.6,
  });
  s.addText("FIFO  ·  Makespan 361.8", {
    x: 0.4, y: 4.1, w: 6.4, h: 0.3,
    fontFace: FONT_B, fontSize: 11, bold: true, color: NAVY, align: "center",
  });
  s.addImage({
    path: path.join(RESULTS, "gantt_DISP-SPT.png"),
    x: 6.85, y: 1.5, w: 6.4, h: 2.6,
  });
  s.addText("SPT  ·  Makespan 388.2", {
    x: 6.85, y: 4.1, w: 6.4, h: 0.3,
    fontFace: FONT_B, fontSize: 11, bold: true, color: NAVY, align: "center",
  });
  s.addImage({
    path: path.join(RESULTS, "gantt_DISP-EDD.png"),
    x: 0.4, y: 4.5, w: 6.4, h: 2.6,
  });
  s.addText("EDD  ·  Makespan 361.8", {
    x: 0.4, y: 7.1, w: 6.4, h: 0.3,
    fontFace: FONT_B, fontSize: 11, bold: true, color: NAVY, align: "center",
  });
  // 우측 하단: 관찰
  s.addShape(pptx.ShapeType.roundRect, {
    x: 6.85, y: 4.5, w: 6.4, h: 2.6, fill: { color: "F5F5F5" }, line: { color: NAVY },
    rectRadius: 0.08,
  });
  s.addText("Observation", {
    x: 7.0, y: 4.6, w: 6.0, h: 0.4,
    fontFace: FONT_H, fontSize: 14, bold: true, color: NAVY,
  });
  s.addText([
    { text: "• ", options: { bold: true } },
    { text: "FIFO ≈ EDD: release 동일 시 두 규칙이 동일 순서 산출\n", options: {} },
    { text: "• ", options: { bold: true } },
    { text: "SPT 가 짧은 Op 우선 → 긴 MIXER 가 후순위로 밀려 손해\n", options: {} },
    { text: "• ", options: { bold: true } },
    { text: "본 소규모 instance 에서는 단순 FIFO 가 우수\n", options: {} },
    { text: "• ", options: { bold: true } },
    { text: "instance 규모↑ 시 MILP / DRL 의 우위 기대", options: {} },
  ], {
    x: 7.0, y: 5.0, w: 6.2, h: 2.0,
    fontFace: FONT_B, fontSize: 11, color: DARK_TEXT,
  });
  addFooter(s, 12, TOTAL_SLIDES);
}

// ===== 슬라이드 13: KPI 비교 =====
{
  const s = pptx.addSlide();
  addHeader(s, "실험 결과 ③ — KPI 종합 비교", "08 KPI COMPARISON");
  s.addImage({
    path: path.join(RESULTS, "kpi_comparison.png"),
    x: 0.4, y: 1.55, w: 12.5, h: 3.2,
  });

  // 결과 표
  s.addTable([
    [
      { text: "Solver", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Makespan", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Mean Tard.", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Util %", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Time(s)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
      { text: "Gap vs MILP", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
    ],
    ["DISP-FIFO", "361.8", "0.0", "24.9%", "<0.01", { text: "−4.83%", options: { color: "55A467", bold: true } }],
    ["DISP-SPT",  "388.2", "0.0", "23.2%", "<0.01", { text: "+2.12%", options: { color: ACCENT, bold: true } }],
    ["DISP-EDD",  "361.8", "0.0", "24.9%", "<0.01", { text: "−4.83%", options: { color: "55A467", bold: true } }],
    [
      { text: "MILP", options: { bold: true } },
      { text: "380.1", options: { bold: true } },
      "0.0", "23.7%", "0.20",
      { text: "—", options: { color: MUTED } },
    ],
  ], {
    x: 0.6, y: 5.0, w: 12.2, colW: [2.4, 1.8, 2.0, 1.6, 1.8, 2.6],
    fontFace: FONT_B, fontSize: 12, color: DARK_TEXT,
    border: { type: "solid", color: "DDDDDD", pt: 0.5 },
    rowH: 0.4, align: "center",
  });
  addFooter(s, 13, TOTAL_SLIDES);
}

// ===== 슬라이드 14: 분석 & 인사이트 =====
{
  const s = pptx.addSlide();
  addHeader(s, "결과 분석 및 인사이트", "09 DISCUSSION");
  const insights = [
    ["기계 병렬도가 높을수록", "휴리스틱과 MILP 격차 축소 — 본 instance (10 기계 / 6 job) 는 capacity 여유가 커서 FIFO 도 충분히 강함"],
    ["SPT 의 함정", "긴 MIXER op 을 미루다 critical path 가 늘어남 — 순수 SPT 는 다단계 공정에서 위험"],
    ["MILP 의 진가는 규모에서", "Job 수가 30↑ 으로 늘면 휴리스틱은 sub-optimal, MILP 는 전역 최적 (단, 연산시간 trade-off)"],
    ["BOM 종속의 영향", "모든 솔버에서 FG 시작이 BULK QC 완료 이후로 정렬됨 — 제약식 정상 작동 확인"],
    ["다음 단계 (DRL)", "MaskablePPO 학습으로 대규모 + 동적 환경에서 휴리스틱 / MILP 한계 보완"],
  ];
  insights.forEach((it, i) => {
    const y = 1.8 + i * 1.05;
    s.addShape(pptx.ShapeType.ellipse, {
      x: 0.6, y: y + 0.1, w: 0.55, h: 0.55, fill: { color: NAVY }, line: { color: NAVY },
    });
    s.addText(`${i+1}`, {
      x: 0.6, y: y + 0.1, w: 0.55, h: 0.55,
      fontFace: FONT_H, fontSize: 14, bold: true, color: WHITE,
      align: "center", valign: "middle",
    });
    s.addText(it[0], {
      x: 1.3, y: y, w: 4.3, h: 0.85,
      fontFace: FONT_H, fontSize: 14, bold: true, color: NAVY,
      valign: "middle",
    });
    s.addText(it[1], {
      x: 5.7, y: y, w: 7.3, h: 0.85,
      fontFace: FONT_B, fontSize: 12, color: DARK_TEXT,
      valign: "middle",
    });
  });
  addFooter(s, 14, TOTAL_SLIDES);
}

// ===== 슬라이드 15: 기대효과 =====
{
  const s = pptx.addSlide();
  addHeader(s, "기대 효과", "10 EXPECTED BENEFITS");
  // 좌: 정량
  s.addShape(pptx.ShapeType.roundRect, {
    x: 0.6, y: 1.7, w: 6.0, h: 5.0, fill: { color: NAVY }, line: { color: NAVY },
    rectRadius: 0.08,
  });
  s.addText("정량적 효과 (Target)", {
    x: 0.8, y: 1.85, w: 5.6, h: 0.45,
    fontFace: FONT_H, fontSize: 16, bold: true, color: ICE,
  });
  const quant = [
    ["−15%", "Makespan 단축"],
    ["−50%", "시험실 평균 대기"],
    ["+10%p", "설비 가동률"],
    ["−30%", "납기 지각 (Tardiness)"],
  ];
  quant.forEach((q, i) => {
    const y = 2.45 + i * 1.0;
    s.addText(q[0], {
      x: 0.8, y: y, w: 2.5, h: 0.8,
      fontFace: FONT_H, fontSize: 32, bold: true, color: ACCENT,
      valign: "middle",
    });
    s.addText(q[1], {
      x: 3.3, y: y, w: 3.1, h: 0.8,
      fontFace: FONT_B, fontSize: 13, color: WHITE,
      valign: "middle",
    });
  });

  // 우: 정성
  s.addShape(pptx.ShapeType.roundRect, {
    x: 6.85, y: 1.7, w: 6.0, h: 5.0, fill: { color: "F5F5F5" }, line: { color: "DDDDDD" },
    rectRadius: 0.08,
  });
  s.addText("정성적 효과", {
    x: 7.05, y: 1.85, w: 5.6, h: 0.45,
    fontFace: FONT_H, fontSize: 16, bold: true, color: NAVY,
  });
  s.addText([
    { text: "• ", options: { bold: true, color: NAVY } },
    { text: "경험 → 데이터·모델 기반 의사결정 전환\n\n", options: {} },
    { text: "• ", options: { bold: true, color: NAVY } },
    { text: "반장 교체·신규 인력에도 동일 품질 스케줄 산출\n\n", options: {} },
    { text: "• ", options: { bold: true, color: NAVY } },
    { text: "SimPy 가상공장 → 신제품·라인 증설 What-if 분석\n\n", options: {} },
    { text: "• ", options: { bold: true, color: NAVY } },
    { text: "공정 간 충돌·대기 사전 차단 → 운영 스트레스 ↓\n\n", options: {} },
    { text: "• ", options: { bold: true, color: NAVY } },
    { text: "JSSP 사례 자산화 → 타 사업장·공정 확장 기반", options: {} },
  ], {
    x: 7.05, y: 2.35, w: 5.7, h: 4.2,
    fontFace: FONT_B, fontSize: 13, color: DARK_TEXT,
  });
  addFooter(s, 15, TOTAL_SLIDES);
}

// ===== 슬라이드 16: 향후 계획 & Q&A =====
{
  const s = pptx.addSlide();
  s.background = { color: NAVY };
  s.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: ACCENT },
  });
  s.addText("Next Steps & Q&A", {
    x: 0.9, y: 0.7, w: 11.5, h: 0.8,
    fontFace: FONT_H, fontSize: 32, bold: true, color: WHITE,
  });
  // 일정 라인
  const phases = [
    ["13주차", "MES 데이터 매핑\n+ 인스턴스 확장 (J=30/50)"],
    ["14주차", "MILP 대규모 실험\n+ Dispatching 5종 풀비교"],
    ["15주차", "DRL (MaskablePPO)\n학습 및 튜닝"],
    ["16주차", "통합 비교 + 최종\n보고서 및 발표"],
  ];
  phases.forEach((p, i) => {
    const x = 0.9 + i * 3.0;
    s.addShape(pptx.ShapeType.roundRect, {
      x: x, y: 2.0, w: 2.8, h: 2.5,
      fill: { color: "2D3A7A" }, line: { color: ICE, width: 1 },
      rectRadius: 0.08,
    });
    s.addText(p[0], {
      x: x, y: 2.15, w: 2.8, h: 0.5,
      fontFace: FONT_H, fontSize: 18, bold: true, color: ACCENT,
      align: "center",
    });
    s.addText(p[1], {
      x: x + 0.15, y: 2.8, w: 2.5, h: 1.6,
      fontFace: FONT_B, fontSize: 12, color: WHITE,
      align: "center",
    });
    if (i < phases.length - 1) {
      s.addText("→", {
        x: x + 2.8, y: 2.0, w: 0.2, h: 2.5,
        fontFace: FONT_B, fontSize: 22, color: ICE,
        align: "center", valign: "middle",
      });
    }
  });
  s.addText("Thank You", {
    x: 0.9, y: 5.0, w: 11.5, h: 1.0,
    fontFace: FONT_H, fontSize: 54, bold: true, color: WHITE,
    align: "center",
  });
  s.addText("질문과 피드백을 환영합니다.", {
    x: 0.9, y: 6.0, w: 11.5, h: 0.5,
    fontFace: FONT_B, fontSize: 16, color: ICE, italic: true,
    align: "center",
  });
  s.addText("코드 저장소:  code/  (Python 3.14, SimPy, PuLP, matplotlib)", {
    x: 0.9, y: 6.8, w: 11.5, h: 0.3,
    fontFace: "Consolas", fontSize: 11, color: ICE, align: "center",
  });
}

// === Save ===
const out = path.resolve(__dirname, "텀프로젝트_발표자료.pptx");
pptx.writeFile({ fileName: out }).then(f => console.log("Saved:", f));
