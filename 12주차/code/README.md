# 화장품 MES JSSP 최적화 — 텀프로젝트 코드

## 구조
```
code/
├── main.py                   # End-to-end demo entry point
├── README.md
├── requirements.txt
├── src/
│   ├── domain.py             # Operation/Job/Machine/Schedule
│   ├── loader.py             # 합성 인스턴스 생성기
│   ├── dispatching_solver.py # SPT/EDD/FIFO/LPT/CR
│   ├── milp_solver.py        # PuLP + CBC 기반 MILP
│   └── visualizer.py         # 간트 / KPI 비교 차트
└── results/                  # 출력 PNG 및 텍스트 보고서
```

## 실행
```powershell
py -3 -m pip install -r requirements.txt
py -3 main.py
```

## 모델링 요약
- **Job**: 반제품(BULK) + 완제품(FG) 지시
- **Routing**:
  - BULK: SCALE → MIXER → QC_BULK → STORAGE
  - FG:   FILLER → QC_FG → PACKAGING
- **제약**: 선후행 / 비선점 / 기계용량 / **BOM 종속**(FG 첫 op ≥ BULK 마지막 op end)
- **목적**: `min α·Cmax + β·Σ Tardiness`

## 풀이 기법 (4종 비교)
1. **FIFO** — release 순서대로
2. **SPT** — 처리시간 짧은 순
3. **EDD** — 납기 빠른 순
4. **MILP** — PuLP + CBC, Big-M disjunctive 모델 (전역 최적)
