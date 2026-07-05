"""도메인 모델 — Job / Operation / Machine / Schedule / Instance."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class MachineType(str, Enum):
    SCALE     = "SCALE"      # 저울
    MIXER     = "MIXER"      # 믹서(PLC)
    QC_BULK   = "QC_BULK"    # 반제품 시험실
    STORAGE   = "STORAGE"    # 저장조/숙성조
    FILLER    = "FILLER"     # 충전(PLC)
    QC_FG     = "QC_FG"      # 완제품 시험실
    PACKAGING = "PACKAGING"  # 포장


class JobType(str, Enum):
    BULK = "BULK"   # 반제품
    FG   = "FG"     # 완제품


@dataclass(frozen=True)
class Operation:
    id: str
    job_id: str
    seq: int
    machine_type: MachineType
    proc_time: float


@dataclass
class Job:
    id: str
    type: JobType
    operations: List[Operation]
    due_date: float
    release: float = 0.0
    bom_parent_id: Optional[str] = None

    @property
    def total_proc_time(self) -> float:
        return sum(o.proc_time for o in self.operations)


@dataclass(frozen=True)
class Machine:
    id: str
    type: MachineType


@dataclass
class Instance:
    id: str
    jobs: List[Job]
    machines: List[Machine]
    horizon: int = 0

    def __post_init__(self):
        if self.horizon == 0:
            self.horizon = int(sum(j.total_proc_time for j in self.jobs) * 2)

    def machines_of(self, mtype: MachineType) -> List[Machine]:
        return [m for m in self.machines if m.type == mtype]

    def job(self, job_id: str) -> Job:
        return next(j for j in self.jobs if j.id == job_id)


@dataclass
class Assignment:
    op: Operation
    machine: Machine
    start: float
    end: float


@dataclass
class Schedule:
    instance_id: str
    solver_name: str
    assignments: List[Assignment] = field(default_factory=list)
    solve_time_sec: float = 0.0

    @property
    def makespan(self) -> float:
        return max((a.end for a in self.assignments), default=0.0)

    def tardiness(self, instance: Instance) -> Dict[str, float]:
        last_end: Dict[str, float] = {}
        for a in self.assignments:
            last_end[a.op.job_id] = max(last_end.get(a.op.job_id, 0.0), a.end)
        return {jid: max(0.0, last_end.get(jid, 0.0) - instance.job(jid).due_date)
                for jid in [j.id for j in instance.jobs]}

    def mean_tardiness(self, instance: Instance) -> float:
        tards = self.tardiness(instance)
        return sum(tards.values()) / max(len(tards), 1)

    def machine_utilization(self, instance: Instance) -> Dict[str, float]:
        busy: Dict[str, float] = {m.id: 0.0 for m in instance.machines}
        for a in self.assignments:
            busy[a.machine.id] += a.end - a.start
        mks = self.makespan or 1.0
        return {mid: busy[mid] / mks for mid in busy}
