"""TC6035 Part 1 — wireless sensor network placement.

Public surface used by student notebooks:

    from tc6035 import build_instance, SensorPlacementProblem

Everything else is either instructor-side or internal.
"""

from .instance import Instance, InstanceSpec, build_instance, coverage_radius, seed_from_student_id
from .problem import (
    DEFAULT_BUDGET,
    BudgetExceeded,
    Evaluation,
    RunRecord,
    SensorPlacementProblem,
)

__all__ = [
    "Instance",
    "InstanceSpec",
    "build_instance",
    "coverage_radius",
    "seed_from_student_id",
    "SensorPlacementProblem",
    "Evaluation",
    "RunRecord",
    "BudgetExceeded",
    "DEFAULT_BUDGET",
]
