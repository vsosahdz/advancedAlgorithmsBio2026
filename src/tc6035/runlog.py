"""Persistence for run evidence.

The autograder re-executes a sample of each submission's runs and compares the
resulting values against what was recorded. That comparison is exact, so the
format must preserve float64 bit-for-bit: trajectories go into a compressed
``.npz`` rather than JSON, where rounding would silently destroy the very thing
being checked.

An environment fingerprint travels with every run set. If a submission was
produced outside the pinned container, the mismatch is then visible as a
mismatch rather than surfacing later as an unexplained "fabricated results"
flag against an honest student.
"""

from __future__ import annotations

import json
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .problem import RunRecord

FORMAT_VERSION = 1

_FINGERPRINTED_PACKAGES = ("numpy", "scipy")

_THREADING_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


def environment_fingerprint() -> dict[str, Any]:
    """Capture everything that could make identical code produce different numbers."""
    import os

    packages: dict[str, str] = {}
    for name in _FINGERPRINTED_PACKAGES:
        try:
            packages[name] = __import__(name).__version__
        except ImportError:
            packages[name] = "absent"

    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": packages,
        "threading": {var: os.environ.get(var) for var in _THREADING_VARS},
        "pythonhashseed": os.environ.get("PYTHONHASHSEED"),
    }


@dataclass
class RunSet:
    """A set of runs of one algorithm on one instance."""

    algorithm: str
    student_id: str
    params: dict[str, Any]
    records: list[RunRecord]
    environment: dict[str, Any] = field(default_factory=environment_fingerprint)

    @property
    def best_values(self) -> np.ndarray:
        return np.array([r.best for r in self.records], dtype=float)

    def summary(self) -> dict[str, Any]:
        best = self.best_values
        return {
            "algorithm": self.algorithm,
            "student_id": self.student_id,
            "n_runs": len(self.records),
            "median": float(np.median(best)) if best.size else None,
            "iqr": [float(np.percentile(best, 25)), float(np.percentile(best, 75))]
            if best.size
            else None,
            "budget": self.records[0].budget if self.records else None,
            "evaluations_used": [r.evaluations_used for r in self.records],
            "seeds": [r.seed for r in self.records],
        }


def save_runset(path: str | Path, runset: RunSet) -> Path:
    """Write a run set to ``path`` as a compressed ``.npz``."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix != ".npz":
        path = path.with_suffix(".npz")

    arrays: dict[str, np.ndarray] = {}
    for i, record in enumerate(runset.records):
        arrays[f"values_{i}"] = np.asarray(record.values, dtype=np.float64)
        arrays[f"best_{i}"] = np.asarray(record.best_so_far, dtype=np.float64)

    meta = {
        "format_version": FORMAT_VERSION,
        "algorithm": runset.algorithm,
        "student_id": runset.student_id,
        "params": runset.params,
        "environment": runset.environment,
        "runs": [
            {
                "seed": record.seed,
                "budget": record.budget,
                "evaluations_used": record.evaluations_used,
                "instance_id": record.instance_id,
            }
            for record in runset.records
        ],
    }

    np.savez_compressed(path, meta=json.dumps(meta), **arrays)
    return path


@dataclass
class LoadedRunSet:
    meta: dict[str, Any]
    values: list[np.ndarray]
    best_so_far: list[np.ndarray]

    @property
    def algorithm(self) -> str:
        return self.meta["algorithm"]

    @property
    def seeds(self) -> list[int]:
        return [run["seed"] for run in self.meta["runs"]]

    @property
    def best_values(self) -> np.ndarray:
        return np.array([b[-1] if b.size else float("-inf") for b in self.best_so_far])


def load_runset(path: str | Path) -> LoadedRunSet:
    """Read a run set written by :func:`save_runset`."""
    with np.load(Path(path), allow_pickle=False) as data:
        meta = json.loads(str(data["meta"]))
        n = len(meta["runs"])
        values = [data[f"values_{i}"] for i in range(n)]
        best = [data[f"best_{i}"] for i in range(n)]
    return LoadedRunSet(meta=meta, values=values, best_so_far=best)


def compare_trajectories(
    recorded: np.ndarray, replayed: np.ndarray, *, exact: bool = True
) -> tuple[bool, str]:
    """Compare a recorded trajectory against a re-execution.

    Exact by default. The pinned container is what makes that sound; falling
    back to a tolerance weakens the check to something a plausible fabricated
    result could pass, so ``exact=False`` should be used only if the container
    requirement is ever relaxed, and the relaxation recorded.
    """
    if recorded.shape != replayed.shape:
        return False, (
            f"length differs: recorded {recorded.shape[0]} evaluations, "
            f"re-execution {replayed.shape[0]}"
        )

    if exact:
        if np.array_equal(recorded, replayed):
            return True, "identical"
        first = int(np.argmax(recorded != replayed))
        return False, (
            f"first divergence at evaluation {first}: "
            f"recorded {recorded[first]!r}, re-executed {replayed[first]!r}"
        )

    if np.allclose(recorded, replayed, rtol=1e-9, atol=1e-12):
        return True, "within tolerance (weakened check)"
    return False, "outside tolerance"


def verify_environment_match(
    recorded: dict[str, Any], current: dict[str, Any] | None = None
) -> list[str]:
    """Report environment differences that could break exact comparison."""
    current = current or environment_fingerprint()
    problems: list[str] = []

    if recorded.get("machine") != current.get("machine"):
        problems.append(
            f"architecture differs: recorded {recorded.get('machine')}, "
            f"current {current.get('machine')} -- exact comparison is unsound across architectures"
        )
    # Sorted so the diagnostic report is byte-identical across runs; dict order
    # would not change any number, but a diffable report is worth having.
    for name, version in sorted((recorded.get("packages") or {}).items()):
        if (current.get("packages") or {}).get(name) != version:
            problems.append(
                f"{name} differs: recorded {version}, "
                f"current {(current.get('packages') or {}).get(name)}"
            )
    for var, value in sorted((recorded.get("threading") or {}).items()):
        if value != "1":
            problems.append(
                f"{var} was {value!r} when the run was recorded, not '1'; "
                "multithreaded BLAS makes the trajectory non-reproducible"
            )
    return problems


def runsets_from_directory(directory: str | Path) -> list[LoadedRunSet]:
    """Load every run set in a directory, sorted by filename for determinism."""
    return [load_runset(p) for p in sorted(Path(directory).glob("*.npz"))]


def as_json_summary(runsets: Sequence[LoadedRunSet]) -> str:
    """Human- and machine-readable summary, for the autograder's evidence report."""
    return json.dumps(
        [
            {
                "algorithm": rs.algorithm,
                "n_runs": len(rs.values),
                "median_best": float(np.median(rs.best_values)),
                "evaluations_used": [run["evaluations_used"] for run in rs.meta["runs"]],
            }
            for rs in runsets
        ],
        indent=2,
    )
