"""Your algorithm implementations.

The autograder re-executes a sample of your runs and compares the numbers
against what you reported, so your algorithms have to be reachable from outside
your notebooks. That is the only thing this file constrains.

Three requirements:

  1. callable as  fn(problem, seed, **params) -> float
  2. DETERMINISTIC in (problem, seed, params) — same inputs, same trajectory.
     Seed every generator explicitly; never use the unseeded `random` module.
  3. your notebooks import from here, so the logs describe the code that will
     actually be re-executed

Everything else — representation, neighbourhood, tuning, hybridisation — is
yours. Register each algorithm in ALGORITHMS under the name the milestone asks
for; a run logged under a name that is not here cannot be re-executed and earns
nothing for reproducibility.
"""

import numpy as np


def monte_carlo(problem, seed, **params) -> float:
    """Uniform sampling until the budget is exhausted. Return the best objective."""
    raise NotImplementedError("M0 Question 6")


def simulated_annealing(problem, seed, **params) -> float:
    """Metropolis acceptance. Justify your schedule; report acceptance rates."""
    raise NotImplementedError("M0 Question 7")


# def tabu_search(problem, seed, **params) -> float:   # M1
# def pso(problem, seed, **params) -> float:           # M1 / M2
# def aco(problem, seed, **params) -> float:           # M2 / M3
# def hybrid(problem, seed, **params) -> float:        # M3


ALGORITHMS = {
    "monte_carlo": monte_carlo,
    "simulated_annealing": simulated_annealing,
}
