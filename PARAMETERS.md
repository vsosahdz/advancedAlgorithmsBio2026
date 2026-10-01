<!-- Reference for the methods the course develops. Shipped with the starter
     pack rather than printed in the specification, which is meant to be read
     once; this is meant to be looked things up in. -->

# Parameters: what you choose, and what constrains it

Every algorithm below has knobs. The conditions are binding; the starting
points are not. A value copied from this table and never questioned scores in
the lowest band — the rubric marks the justification and the measurement, not
the number. Each milestone asks you to defend at least one of these, and the
video will ask again.

Your functions take `params`, so you may add parameters of your own. These are
the ones this course expects you to have an opinion about.

## Two conditions that apply to everything

Cost per iteration. Several parameters set how many evaluations one
iteration spends. That divides your budget:

| method | evaluations per iteration | iterations from $B = 5\,000$ |
|---|---|---|
| tabu search | $L$ (candidate list) | $L = 12 \to 416$ · $L = 80 \to 62$ |
| PSO | $S$ (swarm size) | $S = 20 \to 250$ · $S = 40 \to 125$ |
| ACO | `n_ants` | $10 \to 500$ · $25 \to 200$ |


A larger swarm or colony is not more search for free. It buys breadth and
pays in iterations.

Direction. Everything here maximizes. See section 2 of the specification.

## Monte Carlo — the baseline

| parameter | controls | condition | start |
|---|---|---|---|
| `active_fraction_range` | how many sites a sampled solution switches on | a sub-interval of $(0,1)$; too narrow and it never samples a workable size | $(0.1,\ 0.5)$ |


## Simulated annealing

| parameter | controls | condition | start |
|---|---|---|---|
| `initial_temperature` | how freely worsening moves are accepted at the start | $> 0$, and high enough that the measured early acceptance rate is substantial. M0 asks you to report it at both ends | $0.15$ |
| `final_temperature` | how frozen the end is | $0 <$ this $<$ `initial_temperature` | $10^{-4}$ |
| `power_step` | move size in the continuous layer | $> 0$; relative to $[p_{\min}, c_i]$ | $3.0$ |
| `flip_probability` | how often a move touches the discrete layer instead | $\in [0,1]$; at $0$ the subset never changes | $0.5$ |
| `active_fraction` | how many sites the initial solution has on | $\in (0,1)$ | $0.3$ |


::: {.callout-warning appearance="minimal"}
The convergence-in-probability guarantee holds only under a logarithmic
schedule, which is useless at any practical budget. A geometric schedule is what
you should use — and you must say what you gave up.
:::

## Tabu search

| parameter | controls | condition | start |
|---|---|---|---|
| `tenure` $T$ | how many iterations a flipped index stays forbidden | $0 \le T < n$. At $T=0$ the search cycles; as $T \to n$ everything is banned at once and it takes what is left rather than what is best | $12$ |
| `sample_size` $L$ | how much of the neighbourhood each iteration evaluates | $1 \le L \le n$. This is a budget decision — see the table above | $12$ |
| `nominal_power` | the frozen power while only the subset is searched | carried forward from your M0 | your M0 value |
| `active_fraction` | initial subset size | $\in (0,1)$ | $0.3$ |


Aspiration is a design choice, not a number: a banned move is admitted when
it beats $z^{*}$. Without it, memory can forbid the very improvement you want.

## Particle swarm optimization

| parameter | controls | condition | start |
|---|---|---|---|
| `swarm_size` $S$ | how many particles | $S \ge 2$. Budget decision — see the table above | $20$ |
| `w` | inertia — how much of the previous velocity survives | $w < 1$ | $0.72984$ |
| `c1` | pull toward the particle's own best | jointly with `c2` and `w`, below | $1.496172$ |
| `c2` | pull toward the swarm's best | $0 < c_1 + c_2 < 2(1+w)$, jointly with `w` (Clerc–Kennedy) | $1.496172$ |
| `topology` | who sees whose best | `gbest`, `ring`, or von Neumann | `gbest` |
| `subset_size` | which sites PSO tunes power on | sets PSO's ceiling — it does not choose the subset, it inherits it | $20$ |


::: {.callout-important appearance="minimal"}
The starting values are the Clerc–Kennedy constriction coefficients, and they
satisfy the condition: $c_1 + c_2 = 2.992 < 2(1+w) = 3.460$. Satisfying it means
the swarm will settle. It says nothing about what it settles on — M2 asks you
to show a configuration that is stable and stuck.
:::

## Ant colony optimization

| parameter | controls | condition | start |
|---|---|---|---|
| `alpha` $\alpha$ | weight of pheromone in the choice | $\ge 0$. At $\alpha = 0$ pheromone is ignored and the colony is random construction | $1.0$ |
| `beta` $\beta$ | weight of the heuristic (marginal coverage) | $\ge 0$. At $\beta = 0$ the heuristic is ignored | $2.0$ |
| `rho` $\rho$ | evaporation rate | $0 < \rho < 1$. Too high forgets everything; too low never forgets | $0.08$ |
| `n_ants` | solutions built per iteration | $\ge 1$. Budget decision | $10$ |
| `subset_size` | how many sites each ant activates | $\ge 1$ | $20$ |
| `nominal_power` | power while the subset is constructed | carried from M0 | your M0 value |
| `use_bounds` | whether MMAS pheromone bounds are enforced | keep them on. M3 asks you to show they are binding; turn them off and the colony collapses to one subset | `True` |


## The hybrid

| parameter | controls | condition | start |
|---|---|---|---|
| `split` | fraction of the budget given to stage one | $0 < \text{split} < 1$, and both stages must come out of one budget — use `problem.limited()`. Building a second `SensorPlacementProblem` silently doubles your budget | $0.6$ |


The split is the design decision of M3: too much in stage one and the power is
left untuned; too little and you tune a bad subset precisely.

{{< pagebreak >}}
