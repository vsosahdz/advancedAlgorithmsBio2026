# TC6035 Part 1 — Capstone Assignment

**Released:** Session 1 · **Due:** one week after Session 4 · **Weight:** the whole of Part 1's 25%

You will design, tune and compare four metaheuristics on a problem instance that
is yours alone, under a fixed evaluation budget, and you will defend a claim
about them with statistics you produced.

The algorithms are not the deliverable. Working code that reproduces a published
method is assumed at this level, and can be obtained in minutes from a language
model. What is assessed is the part that cannot: formulating the problem,
choosing a representation, tuning under a real constraint, and defending a
falsifiable claim with evidence that survives re-execution.

---

## 1. The problem

Wireless sensor network placement. You are given ~80 candidate mounting sites on
a 100×100 field with a non-uniform demand field, and you must decide:

- **which** sites to activate — a discrete subset choice
- **how much** transmit power to give each active sensor — a continuous vector

The layers are coupled and cannot be optimized independently:

```
  power ↑   →   coverage ↑        (radius grows as √p)
            →   energy cost ↑     (superlinear: amplifier efficiency falls)
            →   interference ↑    (overlapping discs waste capacity)
            →   connectivity ↑    (helps satisfy the hard constraint)
```

Every site has its **own maximum power** — mounting sites differ in solar
exposure, battery and thermal headroom. Covering a distant demand hotspot
therefore requires *selecting a site that can actually reach it*. This is why
choosing the subset first and tuning power afterwards is measurably worse than
optimizing jointly, and demonstrating that is part of M0.

**Hard constraint:** the active sensors must form a connected communication
graph. Two active sensors can communicate when their separation is within 2.5×
the smaller of their coverage radii.

Infeasible solutions are handled by penalty. `evaluate()` returns a scalar that
already includes it, so an optimizer needs no feasibility handling of its own;
`evaluate_verbose()` additionally reports `feasible` and the component count, so
a repair-based approach is equally available. **Both cost one evaluation.**
Which you use is a design decision you must justify.

## 2. Your instance

```python
from tc6035 import build_instance, SensorPlacementProblem

instance = build_instance("A01234567", salt=0)   # your ID and salt from the manifest
problem  = SensorPlacementProblem(instance, budget=5000, seed=seed)
```

Your instance is derived deterministically from your student ID. It is
regenerable and unique. Instances are calibrated to comparable difficulty, so
nobody receives a harder problem than a classmate — the acceptance band and the
method are in `CALIBRATION.md`.

**Teams of two carry two instances**, one per member. See §5.

## 3. The evaluation budget

**5 000 objective evaluations per run. This is enforced, not requested.**

The `Problem` object counts every evaluation and raises `BudgetExceeded` on the
5 001st. A batch of `n` candidates costs `n`, not one — submitting a population
at once is a convenience, never a discount.

This is Topic 1.4 made operational. Cost in this field is counted in function
evaluations, not asymptotics, and the budget is what makes tuning a real
decision rather than a matter of running longer. Budget accounting — where your
evaluations went and why — is graded.

## 4. Milestones

Each milestone consumes a named result from the previous one. **A milestone that
cites nothing from its predecessor fails validation.** This is deliberate: the
work is designed so it cannot be assembled the night before.

### M0 — after Session 1 · foundations and baseline

1. Generate your instance and state the optimization problem formally: decision
   variables, objective, constraints, and the feasibility mechanism you chose.
2. **Landscape analysis.** Characterize what makes your instance hard. At
   minimum: what fraction of random deployments is feasible, how the objective
   distributes under random sampling, and how rugged the neighbourhood is.
3. **Demonstrate the coupling on your own instance.** Optimize the discrete
   layer at a fixed nominal power, then optimize power on that fixed subset, and
   compare against joint optimization under the same total budget. Report the
   gap with the protocol of §6.
4. **Monte Carlo baseline**, n=30 runs. This is the number every later
   algorithm must beat, and every later milestone must cite it.
5. **Simulated annealing**: implement it, justify your cooling schedule, tune it
   within budget, n=30 runs.

> **Carry forward to M1:** your Monte Carlo baseline median, and the nominal
> power value you justified in step 3.

### M1 — after Session 2 · trajectory methods and first swarm

1. **Tabu search** over the discrete layer. Justify your tabu tenure,
   neighbourhood definition, and aspiration criterion. Explain what your memory
   structure actually stores and why.
2. **Initial PSO** over the continuous layer, on a subset fixed from M1 step 1.
3. Compare tabu against your M0 simulated annealing under §6. Both are
   trajectory methods with different memory; say what the difference bought.

> **Carry forward to M2:** your tuned tabu configuration and your initial PSO
> parameters `(w, c1, c2, swarm size)`.

### M2 — after Session 3 · swarm properly

1. **PSO with topology comparison.** Run global-best against at least one
   local-best topology from the same seeds. Attribute any difference to topology
   rather than to noise.
2. **Stability analysis.** Locate your chosen `(w, c1, c2)` in the
   Clerc–Kennedy stability region. If your parameters are outside it, explain
   what you observe and why.
3. **Stagnation — decide with a measure.** Determine *whether* your swarm
   converged prematurely, supporting the answer with a dispersion measure over
   time rather than by eye. Either answer is correct. If your runs improve until
   the budget runs out, your binding constraint is the budget rather than
   diversity, and saying so is a finding — reporting stagnation you did not
   observe is not.
4. **Initial ACO** as subset construction over the discrete layer.

> **Carry forward to M3:** your best PSO configuration, with the evidence that
> selected it.

### M3 — after Session 4 · construction, comparison, defence

1. **ACO with MMAS-style bounds.** Justify `α`, `β`, evaporation rate and the
   pheromone bounds. Show that your bounds are actually binding.
2. **A hybrid** combining at least two of the four approaches. State the design
   rationale before showing the result.
3. **Comparative study.** All four algorithms plus your hybrid, n=30, under §6.
4. **The no-free-lunch question.** Your comparison is an empirical instance of
   the theorem taught in Session 1. State precisely what your data does and does
   not license you to claim about algorithm superiority.
5. **Teams:** the generalization analysis of §5.
6. AI ledger (§7) and video defence (§8).

## 5. Individual or teams of two

Teams of at most two. **A team is not half the work each — it is a larger
question.**

Each member brings their own instance, so a team holds two. The team must
therefore answer something an individual cannot:

> **Does the algorithm ranking established on one instance hold on the other?**

Report the comparative study on both instances and state whether your
conclusions transfer. If the ranking inverts, you have reproduced no-free-lunch
on data you generated — say so, and say what it implies for anyone selecting an
algorithm for an unseen instance.

Both members are jointly responsible for the whole submission. Individual
differentiation comes from the video defence (§8), which is a multiplier on the
team score.

## 6. Experimental protocol

Every comparison in every milestone must satisfy all of the following.
Violations are detected automatically.

| Requirement | Why |
|---|---|
| **n ≥ 30 independent seeds** per algorithm configuration | Below this the variance of a stochastic search is not estimable |
| **Median and IQR**, never best-of-N alone | Best-of-N reports your luck, not your algorithm |
| **Non-parametric test** — Wilcoxon signed-rank for pairs, Friedman for more | Metaheuristic run outcomes are neither normal nor independent; a t-test's assumptions fail |
| **Holm correction** whenever you make more than one comparison | Uncorrected multiple comparisons manufacture significance |
| **Paired designs where possible** — same seeds across algorithms | Removes instance and seed variance from the comparison |
| **Report effect size**, not only significance | With n=30 a trivial difference can reach significance |

State your seeds. Save your run logs. Both are checked.

> A note you should take seriously: this is the single most common place where
> confidently-written but wrong analysis appears, including from language
> models. A t-test on raw run outcomes is a rejection-worthy error in this
> field, and it is exactly what an unprompted "compare these algorithms
> statistically" tends to produce.

## 7. Use of AI is permitted, documented and graded

You may use language models. At doctoral level the relevant skill is not
abstinence; it is **critical use**. What is assessed is your judgment about the
output, not the volume of it.

Maintain `AI_LEDGER.md` — the format and requirements are in
[`AI_LEDGER.md`](AI_LEDGER.md) in this directory. It must record, per entry: the
tool and version, the prompt, what came back, your verdict
(accepted/modified/rejected), your justification, and the verification you
performed.

**The graded part is §3 of the ledger:** at least one concrete instance where the
model was wrong, with the evidence that revealed it. A ledger that records only
successful interactions scores poorly regardless of length.

If you used no AI, say so in a signed declaration. That is a complete and
unpenalized ledger.

## 8. Video defence

Each student individually records **at most 5 minutes**, showing their own
instance and their own convergence results, and answering two questions drawn at
recording time from [`VIDEO_QUESTIONS.md`](VIDEO_QUESTIONS.md).

The bank is published deliberately. Every question in it is answerable only by
reference to *your* data, so knowing them in advance does not let you prepare a
generic answer.

In a team, **both members record separately.** The video yields an individual
multiplier on the team score — see the rubric. No video means a zero multiplier
regardless of the artifact's quality.

## 9. What you submit

```
your-repo/
├── notebooks/
│   ├── m0_foundations.ipynb
│   ├── m1_trajectory.ipynb
│   ├── m2_swarm.ipynb
│   └── m3_construction_and_comparison.ipynb
├── src/                 your algorithm implementations
├── results/             run logs (.npz), one per algorithm configuration
├── figures/             including your own animation (§10)
├── AI_LEDGER.md
└── VIDEO.md             links to each member's recording
```

### The one interface you must conform to

Your algorithms must be **reachable from outside your notebook**, because the
autograder re-executes a sample of your runs and compares the numbers. Put them
in `src/solutions.py` and expose them in an `ALGORITHMS` table:

```python
# src/solutions.py
ALGORITHMS = {
    "monte_carlo": monte_carlo,
    "simulated_annealing": simulated_annealing,
    # ... tabu_search, pso, aco, hybrid as your milestones reach them
}

def monte_carlo(problem, seed, **params) -> float:
    """Search until the budget is exhausted; return the best objective found."""
```

Three requirements, and nothing else is constrained:

1. callable as `fn(problem, seed, **params)`
2. **deterministic** in `(problem, seed, params)` — same inputs, same trajectory
3. your notebooks call *these* functions, so the logs describe the code that
   will actually be re-executed

Representation, neighbourhood, tuning, hybridisation and internal structure are
entirely yours. The names above are fixed only so the autograder knows what to
look for; if you log a run under a name that is not in `ALGORITHMS`, that run
cannot be re-executed and earns nothing for reproducibility.

Work **inside the provided devcontainer**. Results produced elsewhere may not
reproduce, and the autograder compares your reported values against a
re-execution of a sample of your runs. This is not a formality: on a different
architecture a last-bit floating-point difference redirects a stochastic search
entirely, and your honest results would not match.

Run the public checks before submitting. Nothing should fail for a reason you
could not have detected yourself.

## 10. Your own visualization

Produce at least one animation or visualization of your algorithm's internal
state — swarm trajectory, or pheromone matrix evolution — **generated from your
own logged run data**.

This is checked against your run logs, so it cannot be produced from borrowed or
invented numbers. It is graded on whether it correctly exposes the mechanism,
not on presentation polish.

## 11. Grading

```
final = ( 60 autograder + 40 rubric ) × individual_video_factor
```

Full breakdown and anchored descriptors: [`RUBRIC.md`](RUBRIC.md).
