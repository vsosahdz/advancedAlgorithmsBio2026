"""TC6035 Part 1 — wireless sensor network placement.

Public surface used by student notebooks:

    from tc6035 import build_instance, SensorPlacementProblem

Everything else is either instructor-side or internal.
"""

from .diagnostics import (
    last_improvement_fraction,
    selection_entropy,
    swarm_diversity,
)
from .instance import Instance, InstanceSpec, build_instance, coverage_radius, seed_from_student_id
from .problem import (
    DEFAULT_BUDGET,
    BudgetExceeded,
    Evaluation,
    RunRecord,
    SensorPlacementProblem,
)

__all__ = [
    "selection_entropy",
    "swarm_diversity",
    "last_improvement_fraction",
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
