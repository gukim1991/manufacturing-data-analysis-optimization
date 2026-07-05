"""엔드투엔드 데모 — 합성 인스턴스 생성 → 4개 솔버 비교 → 간트/KPI 출력.

실행:
    py -3 main.py
"""
from __future__ import annotations
import os
import sys

# src 모듈 import (relative import 용)
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.loader import generate
from src.dispatching_solver import DispatchingSolver, DispatchingRule
from src.milp_solver import MILPSolver
from src.visualizer import plot_gantt, plot_kpi_comparison


RESULTS_DIR = os.path.join(ROOT, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def main():
    print("=" * 60)
    print("화장품 MES JSSP 최적화 — End-to-End Demo")
    print("=" * 60)

    # 1. 합성 인스턴스 생성
    inst = generate(n_bulk=3, n_fg=3, n_scales=2, n_mixers=2,
                    n_fillers=1, n_packaging=1, n_storage=2, seed=42)
    print(f"\n[Instance] {inst.id}")
    print(f"  - Jobs: {len(inst.jobs)} (BULK 3 + FG 3)")
    print(f"  - Machines: {len(inst.machines)}")
    print(f"  - Horizon (Big-M): {inst.horizon}")

    # 2. 솔버 4종 실행
    solvers = [
        DispatchingSolver(DispatchingRule.FIFO),
        DispatchingSolver(DispatchingRule.SPT),
        DispatchingSolver(DispatchingRule.EDD),
        MILPSolver(alpha=1.0, beta=0.3, time_limit=30),
    ]

    schedules = {}
    kpis = {}
    print("\n[Solving]")
    for solver in solvers:
        sched = solver.solve(inst)
        schedules[solver.name] = sched
        util = sched.machine_utilization(inst)
        kpis[solver.name] = {
            "makespan": sched.makespan,
            "mean_tardiness": sched.mean_tardiness(inst),
            "utilization": sum(util.values()) / len(util),
            "time": sched.solve_time_sec,
        }
        print(f"  {solver.name:14s} | "
              f"Makespan={sched.makespan:7.2f}  "
              f"MeanTard={sched.mean_tardiness(inst):6.2f}  "
              f"Util={sum(util.values())/len(util)*100:5.1f}%  "
              f"Time={sched.solve_time_sec:5.2f}s")

    # 3. 간트 차트 저장
    print("\n[Gantt Charts]")
    for name, sched in schedules.items():
        out = os.path.join(RESULTS_DIR, f"gantt_{name}.png")
        plot_gantt(sched, inst, out, title=f"{name} — Makespan={sched.makespan:.1f} min")
        print(f"  saved: {out}")

    # 4. KPI 비교 차트
    out = os.path.join(RESULTS_DIR, "kpi_comparison.png")
    plot_kpi_comparison(kpis, out)
    print(f"  saved: {out}")

    # 5. 텍스트 보고서
    report_path = os.path.join(RESULTS_DIR, "report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("화장품 MES JSSP 최적화 — 실험 결과\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Instance: {inst.id}\n")
        f.write(f"  - BULK Jobs: 3, FG Jobs: 3 (BOM: FG-i → BULK-(i%3))\n")
        f.write(f"  - Machines: {len(inst.machines)} "
                f"(SCALE 2, MIXER 2, QC_BULK 1, STORAGE 2, FILLER 1, QC_FG 1, PACKAGING 1)\n\n")
        f.write("Solver Comparison:\n")
        f.write(f"  {'Solver':<14}  {'Makespan':>9}  {'MeanTard':>9}  {'Util%':>7}  {'Time(s)':>8}\n")
        f.write(f"  {'-'*14}  {'-'*9}  {'-'*9}  {'-'*7}  {'-'*8}\n")
        for name, k in kpis.items():
            f.write(f"  {name:<14}  {k['makespan']:>9.2f}  {k['mean_tardiness']:>9.2f}  "
                    f"{k['utilization']*100:>6.1f}%  {k['time']:>8.3f}\n")

        # MILP 대비 휴리스틱 gap
        if "MILP" in kpis:
            best = kpis["MILP"]["makespan"]
            f.write("\nMakespan Gap vs MILP Optimal:\n")
            for name, k in kpis.items():
                if name == "MILP":
                    continue
                gap = (k['makespan'] - best) / best * 100
                f.write(f"  {name:<14}: +{gap:5.2f}%\n")
    print(f"  saved: {report_path}")
    print("\n[Done] 모든 결과는 results/ 폴더에 저장되었습니다.")


if __name__ == "__main__":
    main()
