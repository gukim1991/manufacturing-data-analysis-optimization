"""간트 차트 / KPI 비교 시각화."""
from __future__ import annotations
import os
from typing import Dict, List
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .domain import Schedule, Instance, JobType, MachineType


_TYPE_COLOR = {
    MachineType.SCALE:     "#4C72B0",
    MachineType.MIXER:     "#DD8452",
    MachineType.QC_BULK:   "#55A467",
    MachineType.STORAGE:   "#C44E52",
    MachineType.FILLER:    "#8172B2",
    MachineType.QC_FG:     "#937860",
    MachineType.PACKAGING: "#DA8BC3",
}


def plot_gantt(schedule: Schedule, instance: Instance, out_path: str,
               title: str = None) -> None:
    machines = sorted(instance.machines, key=lambda m: (m.type.value, m.id))
    m_index = {m.id: i for i, m in enumerate(machines)}

    fig, ax = plt.subplots(figsize=(12, 0.45 * len(machines) + 2))

    for a in schedule.assignments:
        y = m_index[a.machine.id]
        color = _TYPE_COLOR[a.op.machine_type]
        ax.barh(y, a.end - a.start, left=a.start,
                color=color, edgecolor="black", linewidth=0.4, alpha=0.9)
        ax.text(a.start + (a.end - a.start) / 2, y, a.op.job_id,
                ha="center", va="center", fontsize=7, color="white",
                fontweight="bold")

    ax.set_yticks(range(len(machines)))
    ax.set_yticklabels([m.id for m in machines], fontsize=8)
    ax.set_xlabel("Time (min)")
    ax.set_xlim(0, schedule.makespan * 1.05)
    ax.invert_yaxis()
    ax.set_title(title or f"{schedule.solver_name} | Makespan = {schedule.makespan:.1f}")
    ax.grid(axis="x", alpha=0.3)

    legend_handles = [mpatches.Patch(color=c, label=t.value)
                      for t, c in _TYPE_COLOR.items()]
    ax.legend(handles=legend_handles, loc="lower right",
              ncol=4, fontsize=7, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    plt.close()


def plot_kpi_comparison(kpis: Dict[str, Dict[str, float]], out_path: str) -> None:
    """kpis = {solver_name: {'makespan': .., 'mean_tardiness': .., 'utilization': .., 'time': ..}}"""
    solvers = list(kpis.keys())
    metrics = ["makespan", "mean_tardiness", "utilization", "time"]
    titles = ["Makespan (min, ↓)", "Mean Tardiness (min, ↓)",
              "Avg Machine Util. (%, ↑)", "Solve Time (sec)"]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    colors = ["#4C72B0", "#DD8452", "#55A467", "#C44E52", "#8172B2"]
    for ax, metric, title in zip(axes, metrics, titles):
        vals = [kpis[s][metric] for s in solvers]
        if metric == "utilization":
            vals = [v * 100 for v in vals]
        bars = ax.bar(solvers, vals, color=colors[:len(solvers)],
                      edgecolor="black", linewidth=0.6)
        ax.set_title(title, fontsize=11)
        ax.tick_params(axis="x", rotation=20, labelsize=9)
        ax.grid(axis="y", alpha=0.3)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                    f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    plt.suptitle("Solver Comparison — KPI", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(out_path, dpi=140)
    plt.close()
