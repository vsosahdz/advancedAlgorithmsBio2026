# Rubric — TC6035 Part 1 Capstone

```
final_grade_i = ( autograder[60] + rubric[40] ) × video_factor_i
```

The team earns the 100 points. `video_factor` is **individual**, so two members
of the same team can receive different final grades.

---

## Autograder — 60 points

Machine-decidable only. It never scores argument quality; that is §Rubric below.
It runs on every submission and produces an evidence report (convergence curves,
test outputs, budget usage, invariant results, commit distribution) which the
human marker reads alongside the notebooks.

| | Points | Checked |
|---|---:|---|
| **API conformance** | 10 | Required functions exist with the specified signatures; run logs are present, well-formed, and one per declared configuration |
| **Budget compliance** | 5 | No run exceeds 5 000 evaluations. Batch calls charged per candidate. Declared and recorded counts agree |
| **Reproducibility** | 15 | A randomly sampled subset of your runs is re-executed in the pinned container and compared **exactly** against your recorded trajectories |
| **Solution quality** | 10 | Median best objective across your 30 seeds, per algorithm, against the calibrated baseline thresholds |
| **Algorithm invariants** | 10 | Pheromone within declared bounds and evaporated each iteration; velocity bounded; tabu tenure respected; SA acceptance follows the stated schedule |
| **Statistical protocol** | 10 | n ≥ 30 seeds; dispersion reported; non-parametric test used; multiple-comparison correction applied |

### Reproducibility is pass-or-fail per sampled run

A sampled run whose re-execution diverges from your recorded trajectory scores
zero for that run and is flagged for review. The comparison is exact — the
pinned container is what makes that sound. Work outside the container and honest
results will not match.

### Milestone chaining

Each milestone must cite, by name, the result it carries forward from its
predecessor (§4 of the assignment). A milestone citing nothing fails validation
and the affected work is not scored.

---

## Rubric — 40 points

Marked by the instructor, using the autograder's evidence report.

### Analysis and interpretation — 25 points

| Band | Points | Descriptor |
|---|---:|---|
| **Exemplary** | 22–25 | States falsifiable claims and tests them. Explains *mechanistically* why one algorithm beat another on this instance — referring to the landscape, the memory structure, the budget — not merely that it did. Correctly bounds what the data licenses. The no-free-lunch discussion distinguishes what was observed from what can be generalized. Negative or surprising results are reported and analysed rather than hidden. |
| **Proficient** | 17–21 | Comparisons are correct and correctly interpreted. Convergence behaviour is read accurately. Some mechanistic explanation, but partly descriptive. Conclusions are appropriately hedged. |
| **Developing** | 11–16 | Reports what happened without explaining why. Convergence curves are shown but not interpreted. Claims slightly outrun the evidence. Design choices asserted rather than justified. |
| **Inadequate** | 0–10 | Describes outputs with no analysis, or draws conclusions the data does not support. Parameter choices unexplained. No engagement with the coupling, the budget or the landscape. |

Specific things that earn credit here: a stagnation diagnosis supported by a
diversity measure rather than by eye; locating your parameters in the stability
region and reasoning from that; showing your MMAS bounds are actually binding;
an honest account of where your budget went.

### AI ledger — 15 points

| Band | Points | Descriptor |
|---|---:|---|
| **Exemplary** | 13–15 | Documents at least one substantive error by the model — a wrong claim, an inappropriate method, a subtly incorrect implementation — with the specific evidence that revealed it and what was done instead. Shows a working process of verification, not post-hoc justification. A signed no-AI declaration accompanied by evidence of independent verification earns this band equally. |
| **Proficient** | 9–12 | Complete and honest ledger. An error is identified but the detection is described loosely, or the error is minor. |
| **Developing** | 5–8 | Ledger present but records only successful interactions. No critical engagement. Reads as compliance. |
| **Inadequate** | 0–4 | Absent, or plainly incomplete given the evident use of assistance. |

Volume is not credit. A ledger of fifty accepted prompts and no critique scores
in the Developing band. One well-documented catch scores at the top.

---

## Video factor — individual multiplier

Applied to the team's 100 points. **Capped at 1.0**: the video can confirm or
reduce a grade, never inflate one.

| Factor | Descriptor |
|---:|---|
| **1.00** | Explains their own contribution *and* can answer about the partner's. Handles the drawn questions from their own data without hesitation. Distinguishes what they found from what they inferred. |
| **0.85** | Explains their own work confidently and correctly. Vague on the parts they did not do. |
| **0.60** | Hesitates on their *own* results. Can describe what was done but not why. Answers the drawn questions only partly. |
| **0.30** | Cannot account for results attributed to them. Describes the submission as an observer rather than an author. |
| **0.00** | No video submitted, or unable to defend any part of the work. |

For an individual submission the factor is applied identically; there is simply
no partner component.

---

## Automatic penalties

| | |
|---|---|
| Work produced outside the pinned container | Reproducibility points cannot be earned; results are unverifiable |
| Milestone with no citation of its predecessor | That milestone is not scored |
| More than two members on a submission | Submission rejected |
| Fabricated results (re-execution diverges with no environment explanation) | Referred under academic integrity |

## What is *not* penalized

- A negative result, honestly analysed. An algorithm performing badly on your
  instance is a finding, and no-free-lunch predicts you should see some.
- A hybrid that fails to beat its components, if the design rationale was stated
  in advance and the failure is analysed.
- Declaring no AI use.
- Disagreeing with the course material, if the argument is supported.

