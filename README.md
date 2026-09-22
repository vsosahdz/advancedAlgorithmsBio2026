# TC6035 Part 1 — capstone assignment

Advanced Algorithms and Bioinspired Techniques · doctoral programme
Tecnológico de Monterrey · Prof. Víctor Adrián Sosa Hernández

Everything you need is here. Read [`assignment/README.md`](assignment/README.md)
first — it is the specification you are graded against.

---

## 1. Get your own copy

**Use the green "Use this template" button. Do not fork.**

A fork of a public repository **cannot be made private** — GitHub does not allow
it. Forking would publish your work to the whole cohort from your first commit,
and list your submission on the template's fork graph. Since your problem
instance is personal, copying code would gain someone little, but your written
analysis is fully copyable and it is the part being graded.

```
Use this template  →  Create a new repository
  Repository name : tc6035-<your student id>        e.g. tc6035-A01234567
  Visibility      : PRIVATE                          ← not optional
```

Then add your instructor as a collaborator:

```
Settings → Collaborators → Add people → <instructor GitHub username>
```

You will be asked to confirm this before the M0 deadline. A repository your
instructor cannot read cannot be graded.

**Working in a pair?** One of you creates the repository and adds both the other
student and the instructor as collaborators. Declare both student IDs in
`TEAM.md`. You will each carry your own problem instance — see §5 of the
assignment specification.

## 2. Open it in the container

**This is not a suggestion.** Your results are re-executed and compared against
what you reported, exactly. Work outside the container and your honest results
will not match: on a different architecture a last-bit floating-point difference
redirects a stochastic search entirely.

You need [Docker](https://docs.docker.com/get-docker/) and VS Code with the
**Dev Containers** extension.

```
VS Code → Open Folder → your repository
        → "Reopen in Container" when prompted
```

The container builds once, then starts in seconds. It verifies itself on
creation; you can re-run that check any time:

```bash
python scripts/verify_environment.py
```

It fails loudly rather than warning, because a silently wrong environment
produces results the autograder will reject.

## 3. Set your identity

Open [`notebooks/m0_foundations.ipynb`](notebooks/m0_foundations.ipynb) and set,
in the first code cell:

```python
STUDENT_ID = "A01234567"   # yours
SALT       = 0             # from the instance manifest your instructor published
```

The salt is almost always 0. It is non-zero only when your first instance draw
fell outside the calibrated difficulty band and was regenerated, so that nobody
receives a harder problem than a classmate.

## 4. Work through the milestones

| | released | notebook |
|---|---|---|
| **M0** | Session 1 | `notebooks/m0_foundations.ipynb` |
| M1 | Session 2 | `notebooks/m1_trajectory.ipynb` |
| M2 | Session 3 | `notebooks/m2_swarm.ipynb` |
| M3 | Session 4 | `notebooks/m3_construction.ipynb` |

Each milestone must cite by name what it carries forward from the previous one.
One that cites nothing fails validation and is not scored.

## 5. Check before you submit

```bash
python scripts/self_check.py
```

This runs every structural check the autograder runs. Nothing should fail for a
reason you could not have detected yourself — if `self_check` passes and the
autograder still fails you on structure, tell your instructor, because that is a
bug in the assignment and not in your work.

Inside a notebook you can also run the public tests for one question:

```python
grader.check("q3_feasibility")
grader.check_all()
```

Public tests are a floor, not the grade. Hidden tests check more.

## 6. Draw your video questions

On the day you record:

```bash
python scripts/draw_video_questions.py --student-id A01234567
```

State the date and the drawn question numbers at the start of your recording.
The draw is seeded from your ID and that date, so your instructor reproduces it
exactly — and you cannot know it in advance.

---

## What is in here

```
assignment/     the specification, rubric, AI ledger template, video bank
notebooks/      one per milestone
src/tc6035/     the problem library — read it, do not modify it
scripts/        environment check, self-check, video draw
results/        your run logs land here (.npz)
.devcontainer/  the pinned environment
```

`src/tc6035/` is provided and fixed. Your own algorithm implementations go in a
`src/` module of your own, or in the notebooks — your choice, but be consistent
and say which you chose.

## Rules worth repeating

- **5 000 evaluations per run, enforced.** The 5 001st raises. A batch of `n`
  costs `n`.
- **n = 30 seeds, median and IQR, non-parametric tests with Holm correction.**
  Best-of-N without dispersion is a protocol violation, and so is a t-test on
  run outcomes.
- **AI is permitted and graded.** The graded part of the ledger is where the
  model was *wrong*, with the evidence that caught it. A ledger of fifty
  accepted prompts and no critique scores poorly. Declaring no AI use is a
  complete and unpenalized answer.
- **Everyone records a 5-minute video**, including both members of a pair. It
  multiplies your team score and is capped at 1.0.
