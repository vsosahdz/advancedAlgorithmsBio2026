# TC6035 Part 1 — capstone assignment

Advanced Algorithms and Bioinspired Techniques · doctoral programme
Tecnológico de Monterrey · Prof. Víctor Adrián Sosa Hernández

**Read the assignment specification PDF first.** It is on Canvas and it is what
you are graded against. This file only tells you how to get running.

---

## 1. Get set up

You need Python 3.10 or later with `numpy`, `scipy` and `matplotlib`.

### Google Colab — recommended, nothing to install

Upload `tc6035-starter.zip` to your Colab session, then in the first cell:

```python
!unzip -o tc6035-starter.zip
import sys; sys.path.insert(0, "tc6035-starter/src")
```

Colab already has numpy, scipy and matplotlib. Nothing else is needed.

> Colab clears uploaded files when the session ends. Keep your notebook in
> Drive and re-upload the ZIP when you come back, or unzip it into Drive once
> and point `sys.path` there.

### Locally

```bash
python3 -m venv .venv
.venv/bin/pip install numpy scipy matplotlib jupyter
```

Then open the notebooks with `PYTHONPATH=src` set, or add the same
`sys.path.insert` line at the top.

Check it works:

```python
from tc6035 import build_instance, SensorPlacementProblem
instance = build_instance("A01234567")      # your ID
print(instance.n_candidates, "candidate sites")
```

## 2. Set your identity

In the first code cell of each notebook:

```python
STUDENT_ID = "A01234567"   # yours
SALT       = 0             # from the instance manifest on Canvas
```

Your instance is derived from your student ID. It is unique to you, and it is
regenerable — the same ID always produces the same instance, so you can pick the
work up on another machine and get the same problem.

The salt is almost always 0. It is non-zero only when your first instance draw
fell outside the calibrated difficulty band and was regenerated, so that nobody
receives a harder problem than a classmate.

## 3. Work through the milestones

| | released | notebook |
|---|---|---|
| **M0** | Session 1 | `notebooks/m0_foundations.ipynb` |
| M1 | Session 2 | `notebooks/m1_trajectory.ipynb` |
| M2 | Session 3 | `notebooks/m2_swarm.ipynb` |
| M3 | Session 4 | `notebooks/m3_construction.ipynb` |

Each milestone must cite, by name, what it carries forward from the previous
one. A milestone that cites nothing is not scored.

## 4. Submit

One Canvas submission per milestone: **the executed notebook**, named

```
tc6035-m0-A01234567.ipynb
```

Pairs submit once, naming both IDs. Run all cells top to bottom from a restarted
kernel before saving — a notebook whose outputs are missing or stale cannot be
graded on its results.

Full delivery rules are in §11 of the specification PDF.

## 5. Draw your video questions

On the day you record:

```bash
python scripts/draw_video_questions.py --student-id A01234567
```

State the date and the drawn numbers at the start of your recording. The draw is
seeded from your ID and that date, so your instructor reproduces it exactly —
and you cannot know it in advance.

---

## The lecture slides

`slides/` holds the sessions already covered, with their interactive
animations. Open the HTML file in a browser — no server needed.

```
slides/lesson-01.html    landscapes · no free lunch · Monte Carlo · annealing
slides/lesson-02.html    tabu search · particle swarm optimization
slides/anim/             the animations, opened by the decks and on their own
```

The animations are worth driving yourself rather than only watching. Each one
has controls, and the parameters you change there are the same ones you have to
justify in your submission.

## What is in here

```
slides/               lecture decks and their animations
notebooks/            one per milestone
src/tc6035/           the problem library — read it, do not modify it
src/solutions.py      where YOUR algorithms go
VIDEO_QUESTIONS.md    the published question bank
AI_LEDGER_TEMPLATE.md the structure your ledger section must follow
scripts/              the video question draw
```

`src/tc6035/` is provided and fixed. Your own implementations go in
`src/solutions.py`, so each milestone can reuse the last one's code.

## Rules worth repeating

- **5 000 evaluations per run, enforced.** The 5 001st raises. A batch of `n`
  costs `n`.
- **30 seeds, median and IQR, non-parametric tests with Holm correction.**
  Best-of-N without dispersion is a protocol violation, and so is a t-test on
  run outcomes.
- **AI is permitted and graded.** The graded part of the ledger is where the
  model was *wrong*, with the evidence that caught it. Declaring no AI use is a
  complete and unpenalized answer.
- **Everyone records a 5-minute video**, including both members of a pair. It
  multiplies your score and is capped at 1.0.
