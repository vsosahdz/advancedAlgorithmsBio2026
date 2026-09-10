"""The instrumented sensor placement objective.

Two things make this object different from a plain fitness function.

First, it **counts and caps** objective evaluations. Cost in this field is
measured in function evaluations, not asymptotics, so the budget is the binding
constraint of the assignment rather than a suggestion. Exceeding it raises
rather than returning a value: a run cannot quietly consume more budget than it
declares.

Second, it **records** every evaluation. The autograder re-executes a sample of
each submission's runs and compares against the recorded trace, so the trace is
evidence, not a convenience.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

from .instance import Instance, coverage_radius

DEFAULT_BUDGET = 5_000


@dataclass(frozen=True)
class ObjectiveConfig:
    """Weights and exponents of the scalarized objective.

    Exposed as configuration rather than hard-coded constants because these
    values are *calibrated*, not chosen: they are what make the problem have the
    structure the assignment depends on. See ``scripts/calibrate_objective.py``.

    Two of them carry the design load:

    ``energy_exponent``
        Coverage area grows as r^2, and r grows as sqrt(p), so coverage grows
        *linearly* in power. If energy also grew linearly the two would cancel
        and maximum power would always win, leaving the continuous layer
        trivial. Real RF amplifiers lose efficiency at high output, so consumed
        energy grows faster than radiated power. A superlinear exponent is both
        physically honest and what produces the rise-then-fall the assignment
        needs.

    ``activation_cost``
        A fixed cost per activated sensor, independent of its power. Without it,
        activating an extra sensor at minimum power is nearly free and the
        discrete layer degenerates. With it, the discrete layer becomes a
        set-cover-like problem where finding a *small* covering set is the hard
        part -- which is what random sampling is bad at and directed search is
        good at.
    """

    w_coverage: float = 1.0
    w_energy: float = 0.6
    w_interference: float = 0.25

    energy_exponent: float = 2.0
    activation_cost: float = 25.0

    # Energy is normalized against a reference deployment rather than against
    # the absurd upper bound of every candidate at full power, which would make
    # the energy term numerically negligible.
    reference_active_fraction: float = 0.3

    # An infeasible solution must score below every feasible one, or search will
    # happily live in the infeasible region. The per-component term keeps a
    # gradient pointing back toward feasibility.
    penalty_base: float = 2.0
    penalty_per_extra_component: float = 0.1


DEFAULT_OBJECTIVE = ObjectiveConfig()


class BudgetExceeded(RuntimeError):
    """Raised when a run asks for more evaluations than its budget allows."""


@dataclass
class Evaluation:
    """The full breakdown of one objective evaluation."""

    objective: float
    feasible: bool
    coverage: float
    energy: float
    interference: float
    n_active: int
    n_components: int


@dataclass
class RunRecord:
    """The evidence trail for a single run."""

    instance_id: str
    seed: int
    budget: int
    values: list[float] = field(default_factory=list)
    best_so_far: list[float] = field(default_factory=list)

    @property
    def evaluations_used(self) -> int:
        return len(self.values)

    @property
    def best(self) -> float:
        return self.best_so_far[-1] if self.best_so_far else float("-inf")


class SensorPlacementProblem:
    """Mixed discrete/continuous sensor placement.

    A solution is a pair ``(active, power)``:

    - ``active``: boolean array of length N, which candidate positions are on
    - ``power``:  float array of length N, transmit power per position, clipped
      into ``[power_min, power_max]``; entries for inactive positions are ignored

    The two layers are genuinely coupled. Raising a sensor's power widens its
    coverage, but also raises energy cost, raises interference where its disc
    overlaps a neighbour's, and *helps* satisfy the connectivity constraint.
    Optimizing either layer with the other frozen is therefore suboptimal, which
    is the whole point of the problem.

    **Infeasibility is handled by penalty, and reported explicitly.** The scalar
    returned by :meth:`evaluate` already includes the penalty, so an optimizer
    can be run without any feasibility handling of its own; :meth:`evaluate_verbose`
    additionally reports ``feasible`` and the component count, so a repair-based
    approach is equally available. Both cost one evaluation.
    """

    def __init__(
        self,
        instance: Instance,
        budget: int = DEFAULT_BUDGET,
        *,
        seed: int | None = None,
        objective: ObjectiveConfig = DEFAULT_OBJECTIVE,
    ) -> None:
        self.instance = instance
        self.objective_config = objective
        self.budget = int(budget)
        self._used = 0
        self._record = RunRecord(
            instance_id=instance.student_id, seed=seed if seed is not None else -1, budget=self.budget
        )
        self._best = float("-inf")

    # -- budget ------------------------------------------------------------

    @property
    def evaluations_used(self) -> int:
        return self._used

    @property
    def evaluations_remaining(self) -> int:
        return self.budget - self._used

    @property
    def record(self) -> RunRecord:
        return self._record

    def reset(self, *, seed: int | None = None) -> None:
        """Begin a new run, clearing the counter and the evidence trail."""
        self._used = 0
        self._best = float("-inf")
        self._record = RunRecord(
            instance_id=self.instance.student_id,
            seed=seed if seed is not None else -1,
            budget=self.budget,
        )

    def _charge(self, n: int) -> None:
        if self._used + n > self.budget:
            raise BudgetExceeded(
                f"run would use {self._used + n} evaluations but the budget is "
                f"{self.budget}. Requesting a batch of {n} with only "
                f"{self.evaluations_remaining} remaining is still overspending: "
                "a batch costs one evaluation per candidate."
            )
        self._used += n

    # -- evaluation --------------------------------------------------------

    def evaluate(self, active: np.ndarray, power: np.ndarray) -> float:
        """Evaluate one solution. Costs one evaluation."""
        self._charge(1)
        result = self._objective(active, power)
        self._log(result.objective)
        return result.objective

    def evaluate_verbose(self, active: np.ndarray, power: np.ndarray) -> Evaluation:
        """Evaluate one solution and return the full breakdown. Costs one evaluation."""
        self._charge(1)
        result = self._objective(active, power)
        self._log(result.objective)
        return result

    def evaluate_batch(self, actives: np.ndarray, powers: np.ndarray) -> np.ndarray:
        """Evaluate ``n`` solutions. Costs ``n`` evaluations, not one.

        Submitting a population as a batch is a convenience, never a discount.
        """
        actives = np.atleast_2d(actives)
        powers = np.atleast_2d(powers)
        if actives.shape[0] != powers.shape[0]:
            raise ValueError("actives and powers must describe the same number of solutions")

        n = actives.shape[0]
        self._charge(n)

        values = np.empty(n, dtype=float)
        for i in range(n):
            result = self._objective(actives[i], powers[i])
            values[i] = result.objective
            self._log(result.objective)
        return values

    def _log(self, value: float) -> None:
        self._record.values.append(float(value))
        if value > self._best:
            self._best = float(value)
        self._record.best_so_far.append(self._best)

    # -- objective ---------------------------------------------------------

    def _objective(self, active: np.ndarray, power: np.ndarray) -> Evaluation:
        spec = self.instance.spec
        cfg = self.objective_config
        active = np.asarray(active, dtype=bool)
        # Each site has its own cap, so a request above what the site can
        # sustain is silently limited rather than rewarded.
        power = np.clip(np.asarray(power, dtype=float), spec.power_min, self.instance.power_cap)

        idx = np.flatnonzero(active)
        n_active = int(idx.size)

        if n_active == 0:
            return Evaluation(
                objective=-cfg.penalty_base,
                feasible=False,
                coverage=0.0,
                energy=0.0,
                interference=0.0,
                n_active=0,
                n_components=0,
            )

        radii = coverage_radius(power[idx], spec.radius_coeff)

        # covered_count[g] = how many active sensors reach grid point g
        within = self.instance.dist_to_grid[idx] <= radii[:, None]
        covered_count = within.sum(axis=0)

        demand = self.instance.demand
        coverage = float(demand[covered_count > 0].sum())

        # Interference rises with redundant coverage but saturates: one extra
        # overlapping sensor hurts much more than the tenth.
        with np.errstate(divide="ignore", invalid="ignore"):
            redundancy = np.where(covered_count > 0, 1.0 - 1.0 / np.maximum(covered_count, 1), 0.0)
        interference = float((demand * redundancy).sum())

        # Superlinear in power, plus a fixed cost per activated sensor. Both
        # terms are load-bearing; see ObjectiveConfig for why.
        raw_energy = float(
            n_active * cfg.activation_cost + np.power(power[idx], cfg.energy_exponent).sum()
        )
        reference_energy = (
            cfg.reference_active_fraction
            * spec.n_candidates
            * (cfg.activation_cost + spec.power_max**cfg.energy_exponent)
        )
        energy = raw_energy / reference_energy

        n_components = self._count_components(idx, radii)
        feasible = n_components == 1

        objective = (
            cfg.w_coverage * coverage
            - cfg.w_energy * energy
            - cfg.w_interference * interference
        )
        if not feasible:
            objective -= cfg.penalty_base + cfg.penalty_per_extra_component * (n_components - 1)

        return Evaluation(
            objective=float(objective),
            feasible=feasible,
            coverage=coverage,
            energy=energy,
            interference=interference,
            n_active=n_active,
            n_components=n_components,
        )

    def _count_components(self, idx: np.ndarray, radii: np.ndarray) -> int:
        """Connected components of the communication graph over active sensors.

        Two active sensors can communicate when their separation is within
        ``comm_factor`` times the smaller of their coverage radii -- so the
        continuous layer determines whether the discrete layer is even feasible.
        """
        comm_factor = self.instance.spec.comm_factor
        sub = self.instance.dist_between[np.ix_(idx, idx)]
        threshold = comm_factor * np.minimum(radii[:, None], radii[None, :])
        adjacency = sub <= threshold
        np.fill_diagonal(adjacency, False)

        n = idx.size
        seen = np.zeros(n, dtype=bool)
        components = 0
        for start in range(n):
            if seen[start]:
                continue
            components += 1
            queue = deque([start])
            seen[start] = True
            while queue:
                node = queue.popleft()
                for neighbour in np.flatnonzero(adjacency[node] & ~seen):
                    seen[neighbour] = True
                    queue.append(neighbour)
        return components
