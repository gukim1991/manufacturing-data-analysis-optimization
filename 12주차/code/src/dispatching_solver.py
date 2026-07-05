"""Dispatching Rules 기반 스케줄러 (SimPy 환경에서 실시간 dispatch)."""
from __future__ import annotations
import time
from enum import Enum
from typing import List, Dict, Optional
import simpy

from .domain import (
    Instance, Schedule, Assignment, Job, Operation, Machine,
    MachineType, JobType,
)


class DispatchingRule(str, Enum):
    SPT  = "SPT"   # Shortest Processing Time
    LPT  = "LPT"   # Longest Processing Time
    EDD  = "EDD"   # Earliest Due Date
    FIFO = "FIFO"
    CR   = "CR"    # Critical Ratio


def _priority(rule: DispatchingRule, op: Operation, job: Job, now: float,
              remaining_after_op: float) -> float:
    """우선순위 score — 작을수록 우선."""
    if rule == DispatchingRule.SPT:
        return op.proc_time
    if rule == DispatchingRule.LPT:
        return -op.proc_time
    if rule == DispatchingRule.EDD:
        return job.due_date
    if rule == DispatchingRule.FIFO:
        return job.release
    if rule == DispatchingRule.CR:
        slack = job.due_date - now
        work  = max(op.proc_time + remaining_after_op, 1e-6)
        return slack / work
    raise ValueError(rule)


class DispatchingSolver:
    def __init__(self, rule: DispatchingRule):
        self.rule = rule

    @property
    def name(self) -> str:
        return f"DISP-{self.rule.value}"

    def solve(self, instance: Instance) -> Schedule:
        t0 = time.perf_counter()

        env = simpy.Environment()
        # 각 기계 = capacity 1 Resource
        machine_res: Dict[str, simpy.Resource] = {
            m.id: simpy.Resource(env, capacity=1) for m in instance.machines
        }
        # 기계 타입별 사용 가능 기계
        by_type: Dict[MachineType, List[Machine]] = {}
        for m in instance.machines:
            by_type.setdefault(m.type, []).append(m)

        assignments: List[Assignment] = []
        # BOM 종속 이벤트 (BULK 의 QC_BULK 완료 시점)
        bom_event: Dict[str, simpy.Event] = {
            j.id: env.event() for j in instance.jobs if j.type == JobType.BULK
        }

        def remaining_after(job: Job, op_idx: int) -> float:
            return sum(o.proc_time for o in job.operations[op_idx + 1:])

        def acquire_machine(op: Operation, job: Job, op_idx: int):
            """가용 기계 중 즉시 점유 가능한 가장 빠른 기계를 선택.
            없으면 첫 번째 기계 큐에서 대기."""
            candidates = by_type[op.machine_type]
            # 즉시 점유 가능한 기계 우선
            free = [m for m in candidates if machine_res[m.id].count == 0]
            chosen = free[0] if free else candidates[0]
            return chosen

        def job_process(job: Job):
            # release 대기
            if job.release > env.now:
                yield env.timeout(job.release - env.now)
            # FG는 BOM 부모의 QC 완료를 기다림
            if job.type == JobType.FG and job.bom_parent_id:
                yield bom_event[job.bom_parent_id]

            for idx, op in enumerate(job.operations):
                # dispatching 의사결정은 자원 점유 직전에 — 같은 기계 타입에 대해
                # 현재 대기 중인 op들의 우선순위를 정해 우선 순서대로 진입.
                # 단순화를 위해 본 구현은 자원 request 시점에 자연스럽게
                # 순서가 결정되도록 하고, 우선순위 룰은 release/도착 순서로
                # 작업 시작을 staggering 함으로써 반영.
                chosen = acquire_machine(op, job, idx)
                with machine_res[chosen.id].request() as req:
                    yield req
                    start = env.now
                    yield env.timeout(op.proc_time)
                    end = env.now
                    assignments.append(Assignment(op, chosen, start, end))
                    # BULK 의 QC_BULK 완료 시 이벤트 발화
                    if (job.type == JobType.BULK
                        and op.machine_type == MachineType.QC_BULK
                        and not bom_event[job.id].triggered):
                        bom_event[job.id].succeed()

        # 우선순위 룰에 따라 Job 시작 순서를 정렬 (간이 dispatching)
        def job_sort_key(j: Job) -> float:
            first_op = j.operations[0]
            rem = sum(o.proc_time for o in j.operations[1:])
            return _priority(self.rule, first_op, j, 0.0, rem)

        # BULK 먼저 (BOM 종속) 그 다음 FG, 각 그룹 내 우선순위 정렬
        bulks = sorted([j for j in instance.jobs if j.type == JobType.BULK],
                       key=job_sort_key)
        fgs   = sorted([j for j in instance.jobs if j.type == JobType.FG],
                       key=job_sort_key)

        for j in bulks + fgs:
            env.process(job_process(j))

        env.run()

        sched = Schedule(
            instance_id=instance.id,
            solver_name=self.name,
            assignments=assignments,
            solve_time_sec=time.perf_counter() - t0,
        )
        return sched
