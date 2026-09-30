"""Diagnostic measures. Shipped to students.

These are *measurements*, not solutions. A diversity or entropy measure tells
you whether a search is still searching; it does not tell you how to search.
Handing them over costs nothing and removes an excuse for the answer "the curve
went flat", which is not a diagnosis.
"""

from __future__ import annotations

import numpy as np


def selection_entropy(weights: np.ndarray, alpha: float = 1.0) -> float:
    """Shannon entropy of a selection distribution.

    For ant colony optimization, pass the pheromone vector. Entropy falling
    toward zero means every ant now builds the same solution -- the colony has
    stopped searching.

    Comparing final objective values cannot show this: a collapsed colony still
    reports a number, and often a respectable one. That is why the measure
    exists.
    """
    w = np.asarray(weights, dtype=float) ** alpha
    total = w.sum()
    if total <= 0:
        return 0.0
    p = w / total
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def swarm_diversity(positions: np.ndarray) -> float:
    """Mean distance from each particle to the swarm centroid.

    Falling to zero while the best objective stops improving is premature
    convergence. Falling to zero while the best is still improving is just
    convergence -- the two look identical on a convergence curve and different
    here, which is the whole point.
    """
    pos = np.atleast_2d(np.asarray(positions, dtype=float))
    centroid = pos.mean(axis=0)
    return float(np.mean(np.linalg.norm(pos - centroid, axis=1)))


def last_improvement_fraction(best_so_far: np.ndarray) -> float:
    """Fraction of the budget at which the best-so-far last improved.

    Near 1.0 means the search was still finding improvements when the budget ran
    out -- your binding constraint is the budget, not diversity. Well below 1.0
    means evaluations were spent after progress stopped.
    """
    trace = np.asarray(best_so_far, dtype=float)
    if trace.size < 2:
        return 0.0
    gains = np.flatnonzero(np.diff(trace) > 0)
    return float(gains[-1] / trace.size) if gains.size else 0.0
