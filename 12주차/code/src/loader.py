"""합성 인스턴스 생성기 — 코스맥스 MES 공정을 모사."""
from __future__ import annotations
import random
from .domain import (
    Operation, Job, Machine, Instance, MachineType, JobType,
)


def generate(n_bulk: int = 3, n_fg: int = 3,
             n_scales: int = 2, n_mixers: int = 2,
             n_fillers: int = 1, n_packaging: int = 1,
             n_storage: int = 2,
             seed: int = 42) -> Instance:
    """반제품 n_bulk건, 완제품 n_fg건을 가진 인스턴스 생성.

    반제품 라우팅: SCALE → MIXER → QC_BULK → STORAGE
    완제품 라우팅: FILLER → QC_FG → PACKAGING
    BOM: FG-i 는 BULK-(i % n_bulk) 에 의존.
    """
    rng = random.Random(seed)

    machines: list[Machine] = []
    for i in range(n_scales):
        machines.append(Machine(id=f"SCALE-{i+1:02d}", type=MachineType.SCALE))
    for i in range(n_mixers):
        machines.append(Machine(id=f"MIXER-{i+1:02d}", type=MachineType.MIXER))
    machines.append(Machine(id="QC-BULK-01", type=MachineType.QC_BULK))
    for i in range(n_storage):
        machines.append(Machine(id=f"STORAGE-{i+1:02d}", type=MachineType.STORAGE))
    for i in range(n_fillers):
        machines.append(Machine(id=f"FILLER-{i+1:02d}", type=MachineType.FILLER))
    machines.append(Machine(id="QC-FG-01", type=MachineType.QC_FG))
    for i in range(n_packaging):
        machines.append(Machine(id=f"PACK-{i+1:02d}", type=MachineType.PACKAGING))

    jobs: list[Job] = []

    # 반제품 Job 생성
    for i in range(n_bulk):
        jid = f"BULK-{i+1:02d}"
        ops = [
            Operation(f"{jid}-OP1", jid, 0, MachineType.SCALE,   rng.uniform(20, 40)),
            Operation(f"{jid}-OP2", jid, 1, MachineType.MIXER,   rng.uniform(60, 120)),
            Operation(f"{jid}-OP3", jid, 2, MachineType.QC_BULK, rng.uniform(30, 60)),
            Operation(f"{jid}-OP4", jid, 3, MachineType.STORAGE, rng.uniform(15, 30)),
        ]
        due = sum(o.proc_time for o in ops) * rng.uniform(1.5, 2.5)
        jobs.append(Job(jid, JobType.BULK, ops, due_date=due, release=0.0))

    # 완제품 Job 생성 (BOM = BULK-(i % n_bulk))
    for i in range(n_fg):
        jid = f"FG-{i+1:02d}"
        bom_parent = f"BULK-{(i % n_bulk) + 1:02d}"
        ops = [
            Operation(f"{jid}-OP1", jid, 0, MachineType.FILLER,    rng.uniform(40, 80)),
            Operation(f"{jid}-OP2", jid, 1, MachineType.QC_FG,     rng.uniform(20, 40)),
            Operation(f"{jid}-OP3", jid, 2, MachineType.PACKAGING, rng.uniform(30, 60)),
        ]
        parent_total = next(j.total_proc_time for j in jobs if j.id == bom_parent)
        due = (parent_total + sum(o.proc_time for o in ops)) * rng.uniform(1.5, 2.5)
        jobs.append(Job(jid, JobType.FG, ops,
                        due_date=due, release=0.0,
                        bom_parent_id=bom_parent))

    return Instance(id=f"inst_b{n_bulk}_f{n_fg}_s{seed}",
                    jobs=jobs, machines=machines)
