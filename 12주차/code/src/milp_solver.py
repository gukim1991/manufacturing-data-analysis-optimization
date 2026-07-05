"""MILP 기반 JSSP 솔버 (PuLP + CBC) — 소규모 인스턴스 전역 최적해."""
from __future__ import annotations
import time
from typing import Dict, List, Tuple
import pulp

from .domain import (
    Instance, Schedule, Assignment, Operation, Machine,
    MachineType, JobType,
)


class MILPSolver:
    def __init__(self, alpha: float = 1.0, beta: float = 0.5,
                 time_limit: int = 60):
        self.alpha = alpha
        self.beta = beta
        self.time_limit = time_limit

    @property
    def name(self) -> str:
        return "MILP"

    def solve(self, instance: Instance) -> Schedule:
        t0 = time.perf_counter()

        ops: List[Operation] = [o for j in instance.jobs for o in j.operations]
        H = instance.horizon

        # 기계 타입별 사용 가능 기계
        by_type: Dict[MachineType, List[Machine]] = {}
        for m in instance.machines:
            by_type.setdefault(m.type, []).append(m)

        prob = pulp.LpProblem("JSSP_MES", pulp.LpMinimize)

        # 결정 변수
        s = {o.id: pulp.LpVariable(f"s_{o.id}", lowBound=0, upBound=H)
             for o in ops}
        x = {(o.id, m.id): pulp.LpVariable(f"x_{o.id}_{m.id}", cat="Binary")
             for o in ops for m in by_type[o.machine_type]}
        # disjunctive y
        y = {}
        for m in instance.machines:
            ops_on_m = [o for o in ops if o.machine_type == m.type]
            for i, oi in enumerate(ops_on_m):
                for oj in ops_on_m[i+1:]:
                    y[(oi.id, oj.id, m.id)] = pulp.LpVariable(
                        f"y_{oi.id}_{oj.id}_{m.id}", cat="Binary")

        C_max = pulp.LpVariable("C_max", lowBound=0, upBound=H)
        T = {j.id: pulp.LpVariable(f"T_{j.id}", lowBound=0, upBound=H)
             for j in instance.jobs}

        # 목적함수
        prob += self.alpha * C_max + self.beta * pulp.lpSum(T.values())

        # C1. 각 op 정확히 1대에 배정
        for o in ops:
            prob += pulp.lpSum(x[(o.id, m.id)]
                               for m in by_type[o.machine_type]) == 1

        # C2. Release
        for j in instance.jobs:
            prob += s[j.operations[0].id] >= j.release

        # C3. Job 내 선후행
        for j in instance.jobs:
            for i in range(len(j.operations) - 1):
                a = j.operations[i]
                b = j.operations[i + 1]
                prob += s[b.id] >= s[a.id] + a.proc_time

        # C4. 기계 disjunctive (Big-M)
        for (oi_id, oj_id, m_id), y_var in y.items():
            oi = next(o for o in ops if o.id == oi_id)
            oj = next(o for o in ops if o.id == oj_id)
            xi = x[(oi.id, m_id)]
            xj = x[(oj.id, m_id)]
            prob += (s[oj.id] >= s[oi.id] + oi.proc_time
                     - H * (1 - y_var) - H * (2 - xi - xj))
            prob += (s[oi.id] >= s[oj.id] + oj.proc_time
                     - H * y_var - H * (2 - xi - xj))

        # C5. BOM 종속 (FG 첫 op ≥ BULK 마지막 op end)
        for j in instance.jobs:
            if j.type == JobType.FG and j.bom_parent_id:
                parent = instance.job(j.bom_parent_id)
                last = parent.operations[-1]
                prob += s[j.operations[0].id] >= s[last.id] + last.proc_time

        # C7. Makespan / Tardiness
        for j in instance.jobs:
            last = j.operations[-1]
            prob += C_max >= s[last.id] + last.proc_time
            prob += T[j.id] >= s[last.id] + last.proc_time - j.due_date

        # 풀이
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=self.time_limit)
        prob.solve(solver)

        # 결과 → Schedule
        assignments: List[Assignment] = []
        for o in ops:
            for m in by_type[o.machine_type]:
                if pulp.value(x[(o.id, m.id)]) > 0.5:
                    start = pulp.value(s[o.id])
                    assignments.append(
                        Assignment(o, m, start, start + o.proc_time))
                    break
        assignments.sort(key=lambda a: a.start)

        return Schedule(
            instance_id=instance.id,
            solver_name=self.name,
            assignments=assignments,
            solve_time_sec=time.perf_counter() - t0,
        )
