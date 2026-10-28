# TC6035 Part 1 — Advanced Algorithms and Bioinspired Techniques

Tecnológico de Monterrey · doctoral programme
Prof. Víctor Adrián Sosa Hernández

Lecture material for the sessions covered so far, and the capstone assignment.

**Start at [`index.html`](index.html)** — open it in a browser and it links
everything below. It is regenerated on every release, so a `git pull` brings
both the new session and the updated page.

| | |
|---|---|
| `slides/lesson-01.html` | landscapes · no free lunch · Monte Carlo · simulated annealing |
| `slides/lesson-02.html` | tabu search · particle swarm optimization |
| `slides/lesson-03.html` | PSO topologies · stability · ant colony optimization |
| `slides/anim/` | the interactive animations, opened by the decks and usable on their own |

## The assignment

| | |
|---|---|
| `assignment-spec.pdf` | what to build, how it is graded, and the deadline |
| `src/tc6035/` | the library that builds your instance |
| `notebooks/00_instance_check.ipynb` | run this first — it builds your instance and proves your setup works |
| `notebooks/m0`…`m3` | one notebook per milestone, to start from |
| `PARAMETERS.md` | every parameter each technique takes, and how to set it |
| `requirements.lock` | the exact versions this was tested against |

In Colab, or anywhere `src` is not already on the path:

```python
import sys; sys.path.insert(0, "src")
from tc6035 import build_instance, SensorPlacementProblem

instance = build_instance("A01234567", salt=0)   # your ID
problem  = SensorPlacementProblem(instance, budget=5000, seed=0)
```

Your video questions are in the Canvas announcement, against your student ID.

## Running the slides

**1. Get the whole folder, not one file.** Each deck loads its animations from
`anim/` next to it, so the two have to stay together.

```bash
git clone https://github.com/vsosahdz/advancedAlgorithmsBio2026.git
```

Or use **Code → Download ZIP** on GitHub and unzip it. Downloading a single
`.html` through *Save page as* gives you a deck whose animation slides are
blank.

**2. Open the file in a browser.** Double-click it, or drag it onto a browser
window. There is nothing to install and no server to start — everything else
the deck needs is already inside the file.

**3. Move around.**

| | |
|---|---|
| `M` | the menu — and **Index**, to come back to this page |
| `→` `←` or `space` | next and previous slide |
| `Esc` or `O` | overview of every slide |
| `F` | full screen |
| `?` | the full list of keys |

## The animations

Eight slides are live animations rather than pictures: the NFL rank inversion,
the five landscape properties, simulated annealing, the tabu list, the PSO
velocity decomposition, the three swarm topologies, the Clerc–Kennedy stability
region, and the ACO pheromone bounds.

**Drive them.** Press Play, move the sliders, change the seed and watch what
happens. The parameters you are changing — tenure, candidate list size,
inertia, the acceleration coefficients — are the ones you will have to choose
and defend in the assignment, and the fastest way to build intuition for them
is to break them on purpose.

Each animation is also a standalone page. Open anything in `slides/anim/`
directly in a browser to use it full size, outside the deck.

## If an animation slide comes up blank

A grey page with a broken-file icon means the browser could not reach
`anim/`. Two causes, in order of likelihood:

1. The deck was moved away from its folder, or saved on its own. Keep
   every `lesson-NN.html` and `anim/` in the same directory.
2. Your browser blocks local pages from loading other local pages. Serve the
   folder instead — from inside `slides/`:

   ```bash
   python3 -m http.server 8000
   ```

   then open <http://localhost:8000/lesson-01.html>.

## Updates

Later sessions appear here as they are given. Run `git pull` in this folder to
pick them up; the landing page updates with them.
