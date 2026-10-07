"""Problem instances for the wireless sensor network placement task.

Each student receives a distinct instance derived deterministically from their
student ID. Instances are regenerable from the ID alone and are calibrated to be
comparable in difficulty, so no student is handed a materially easier or harder
problem than anyone else.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import numpy as np

"""Coverage radius grows as the square root of transmit power.

That is the free-space path-loss relationship: received power falls as 1/d^2, so
the distance at which a fixed sensitivity threshold is met scales as sqrt(p).
The proportionality constant lives in :class:`InstanceSpec` because it is
calibrated -- it sets how many sensors are needed to cover the field, and
therefore whether the discrete layer is a real combinatorial problem or a
formality.
"""


@dataclass(frozen=True)
class InstanceSpec:
    """Structural constants shared by every instance.

    These are fixed across the cohort. What varies per student is the geometry
    and the demand field, not the size or the physics.
    """

    n_candidates: int = 80
    grid_size: int = 50
    field_size: float = 100.0
    power_min: float = 1.0
    power_max: float = 25.0

    # radius = radius_coeff * sqrt(power). Calibrated: too large and a handful
    # of sensors blanket the field, collapsing the discrete layer into a
    # formality that random sampling solves as well as directed search.
    # At 4.0 the sensing radius spans 4-20 on a 100x100 field, so covering the
    # demand takes roughly 20 well-placed sensors out of 80 candidates.
    radius_coeff: float = 4.0

    # Communication link exists between two active sensors when their distance
    # is within comm_factor times the smaller of their coverage radii. Raising
    # power therefore helps connectivity as well as coverage -- a third channel
    # through which the continuous layer couples to the discrete one.
    #
    # A radio reaches considerably farther than the sensing footprint it
    # supports, which is why this is well above 1. Calibrated at 1.0 the
    # connectivity constraint dominated everything: fewer than 1% of random
    # deployments were feasible and search spent its whole budget escaping the
    # infeasible region rather than optimizing.
    comm_factor: float = 2.5

    n_hotspots: int = 4
    n_clusters: int = 5

    # Not every mounting site can sustain the same transmit power: solar
    # exposure, battery size and thermal headroom differ. Each candidate gets
    # its own cap, drawn between these fractions of ``power_max``.
    #
    # This is what makes the two decision layers genuinely COMPLEMENTARY rather
    # than substitutes. Without it, excess overlap can be fixed either by
    # switching a sensor off or by turning its power down -- the layers become
    # interchangeable and choosing the subset barely depends on the power
    # assignment. With heterogeneous caps, covering a distant hotspot *requires*
    # selecting a site that can actually reach it, so the optimal subset depends
    # on the power profile the deployment needs.
    power_cap_min_fraction: float = 0.35
    power_cap_max_fraction: float = 1.0


@dataclass(frozen=True)
class Instance:
    """A concrete problem instance.

    The distance matrices are precomputed once because every objective
    evaluation needs them; recomputing per evaluation would make the evaluation
    budget measure numpy throughput rather than search quality.
    """

    student_id: str
    seed: int
    spec: InstanceSpec

    candidates: np.ndarray  # (N, 2) candidate sensor positions
    power_cap: np.ndarray  # (N,) per-site maximum transmit power
    grid_points: np.ndarray  # (G, 2) demand sample points
    demand: np.ndarray  # (G,) demand weights, summing to 1

    dist_to_grid: np.ndarray = field(repr=False)  # (N, G)
    dist_between: np.ndarray = field(repr=False)  # (N, N)

    @property
    def n_candidates(self) -> int:
        return int(self.candidates.shape[0])

    @property
    def n_grid(self) -> int:
        return int(self.grid_points.shape[0])


def seed_from_student_id(student_id: str) -> int:
    """Derive a stable 63-bit seed from a student ID.

    Uses blake2b rather than the built-in ``hash``: the latter is randomized per
    process by PYTHONHASHSEED and is not stable across Python versions, so an
    instance generated today would not be regenerable tomorrow.
    """
    normalized = student_id.strip().upper().encode("utf-8")
    digest = hashlib.blake2b(normalized, digest_size=8).digest()
    return int.from_bytes(digest, "big") & ((1 << 63) - 1)


def _sample_candidates(rng: np.random.Generator, spec: InstanceSpec) -> np.ndarray:
    """Place candidate positions with cluster structure.

    Uniformly scattered candidates make the discrete layer nearly separable and
    uninteresting. Clustering creates neighbourhoods where activating one sensor
    genuinely changes the value of activating another.
    """
    n_clustered = int(spec.n_candidates * 0.7)
    n_uniform = spec.n_candidates - n_clustered

    centers = rng.uniform(
        0.15 * spec.field_size, 0.85 * spec.field_size, size=(spec.n_clusters, 2)
    )
    assignment = rng.integers(0, spec.n_clusters, size=n_clustered)
    spread = 0.09 * spec.field_size
    clustered = centers[assignment] + rng.normal(0.0, spread, size=(n_clustered, 2))

    uniform = rng.uniform(0.0, spec.field_size, size=(n_uniform, 2))

    positions = np.vstack([clustered, uniform])
    np.clip(positions, 0.0, spec.field_size, out=positions)
    rng.shuffle(positions)
    return positions


def _build_demand(rng: np.random.Generator, spec: InstanceSpec) -> tuple[np.ndarray, np.ndarray]:
    """Build the demand field: a uniform floor plus Gaussian hotspots.

    The hotspots are what make the landscape multimodal. A uniform demand field
    would reward little more than spreading sensors evenly.
    """
    axis = np.linspace(0.0, spec.field_size, spec.grid_size)
    xx, yy = np.meshgrid(axis, axis, indexing="ij")
    grid_points = np.column_stack([xx.ravel(), yy.ravel()])

    demand = np.full(grid_points.shape[0], 0.25)
    hotspot_centers = rng.uniform(
        0.1 * spec.field_size, 0.9 * spec.field_size, size=(spec.n_hotspots, 2)
    )
    hotspot_scale = rng.uniform(
        0.08 * spec.field_size, 0.18 * spec.field_size, size=spec.n_hotspots
    )
    hotspot_weight = rng.uniform(0.6, 1.6, size=spec.n_hotspots)

    for center, scale, weight in zip(hotspot_centers, hotspot_scale, hotspot_weight):
        sq = np.sum((grid_points - center) ** 2, axis=1)
        demand += weight * np.exp(-sq / (2.0 * scale**2))

    demand /= demand.sum()
    return grid_points, demand


def build_instance(student_id: str, spec: InstanceSpec | None = None, *, salt: int = 0) -> Instance:
    """Generate the instance belonging to ``student_id``.

    ``salt`` exists only for difficulty calibration: if a generated instance
    falls outside the acceptance band it is regenerated with the next salt, so
    the mapping from ID to instance stays deterministic while still allowing
    unusable draws to be rejected.
    """
    spec = spec or InstanceSpec()
    base_seed = seed_from_student_id(student_id)
    seed = (base_seed + salt) & ((1 << 63) - 1)
    rng = np.random.default_rng(seed)

    candidates = _sample_candidates(rng, spec)
    power_cap = spec.power_max * rng.uniform(
        spec.power_cap_min_fraction, spec.power_cap_max_fraction, size=spec.n_candidates
    )
    grid_points, demand = _build_demand(rng, spec)

    diff_grid = candidates[:, None, :] - grid_points[None, :, :]
    dist_to_grid = np.sqrt(np.einsum("ijk,ijk->ij", diff_grid, diff_grid))

    diff_cand = candidates[:, None, :] - candidates[None, :, :]
    dist_between = np.sqrt(np.einsum("ijk,ijk->ij", diff_cand, diff_cand))

    return Instance(
        student_id=student_id,
        seed=seed,
        spec=spec,
        candidates=candidates,
        power_cap=power_cap,
        grid_points=grid_points,
        demand=demand,
        dist_to_grid=dist_to_grid,
        dist_between=dist_between,
    )


def coverage_radius(power: np.ndarray | float, radius_coeff: float) -> np.ndarray | float:
    """Coverage radius for a given transmit power."""
    return radius_coeff * np.sqrt(power)
