"""Run every structural check the autograder runs, before you submit.

The contract this file exists to enforce: **nothing should fail for a reason you
could not have detected yourself.** If this passes and the autograder still
fails you on structure, that is a bug in the assignment, not in your work — tell
your instructor.

It does not grade you. It checks that your submission is well-formed enough to
*be* graded: the environment is right, your logs exist and respect the budget,
you ran enough seeds, your milestones cite their predecessors, and your ledger
is not still the template.

Run:  python scripts/self_check.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
NOTEBOOKS = ROOT / "notebooks"

BUDGET = 5_000
MIN_SEEDS = 30
PLACEHOLDER_ID = "A01234567"

# Milestones and the notebook that must exist once that milestone is due.
MILESTONES = [
    ("M0", "m0_foundations.ipynb", None),
    ("M1", "m1_trajectory.ipynb", "M0"),
    ("M2", "m2_swarm.ipynb", "M1"),
    ("M3", "m3_construction.ipynb", "M2"),
]

# Statistical procedures that are protocol violations in this field.
FORBIDDEN_STATS = [
    (re.compile(r"\bttest_(ind|rel|1samp)\b"), "a t-test on run outcomes: metaheuristic "
     "results are neither normal nor independent. Use wilcoxon or friedmanchisquare."),
    (re.compile(r"\bf_oneway\b"), "ANOVA on run outcomes: same assumption failure as the t-test."),
]
REQUIRED_STATS = re.compile(r"\b(wilcoxon|friedmanchisquare|mannwhitneyu)\b")
CORRECTION = re.compile(r"\b(holm|multipletests|bonferroni)\b", re.IGNORECASE)


class Check:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passed: list[str] = []

    def ok(self, message: str) -> None:
        self.passed.append(message)

    def fail(self, message: str) -> None:
        self.failures.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def check_environment(c: Check) -> None:
    import os
    import platform

    if sys.version_info < (3, 10):
        c.fail(f"Python {platform.python_version()} is too old; the container provides 3.12")
        return
    unpinned = [v for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
                if os.environ.get(v) != "1"]
    if unpinned:
        c.fail(
            f"threading not pinned ({', '.join(unpinned)}). You are probably running "
            "outside the devcontainer; your results will not reproduce under re-execution"
        )
    else:
        c.ok("environment: python and threading pinned")


def check_identity(c: Check) -> str | None:
    """Find the declared student ID, and refuse the placeholder."""
    team = ROOT / "TEAM.md"
    ids: list[str] = []
    if team.exists():
        ids = re.findall(r"\b([A-Z]\d{8})\b", team.read_text(encoding="utf-8"))

    nb = NOTEBOOKS / "m0_foundations.ipynb"
    if nb.exists():
        found = re.findall(r'STUDENT_ID\s*=\s*"([^"]+)"', nb.read_text(encoding="utf-8"))
        ids.extend(found)

    real = [i for i in ids if i != PLACEHOLDER_ID]
    if not ids:
        c.fail("no student ID found in TEAM.md or the M0 notebook")
        return None
    if not real:
        c.fail(f"student ID is still the placeholder {PLACEHOLDER_ID}; set your own")
        return None
    if len(set(real)) > 2:
        c.fail(f"{len(set(real))} distinct student IDs declared; a team is at most two")
        return None

    c.ok(f"identity: {', '.join(sorted(set(real)))}")
    return sorted(set(real))[0]


def check_runlogs(c: Check) -> None:
    if not RESULTS.exists() or not any(RESULTS.glob("*.npz")):
        c.fail("no run logs in results/ — save them with save_runset(...)")
        return

    try:
        sys.path.insert(0, str(ROOT / "src"))
        from tc6035.runlog import load_runset, verify_environment_match
    except ImportError as error:
        c.fail(f"cannot import the course library: {error}")
        return

    for path in sorted(RESULTS.glob("*.npz")):
        name = path.name
        try:
            rs = load_runset(path)
        except Exception as error:  # noqa: BLE001 - report, do not crash the check
            c.fail(f"{name}: unreadable ({error})")
            continue

        used = [run["evaluations_used"] for run in rs.meta["runs"]]
        over = [u for u in used if u > BUDGET]
        if over:
            c.fail(f"{name}: {len(over)} run(s) exceeded the {BUDGET} evaluation budget")
        elif any(u < BUDGET * 0.5 for u in used):
            c.warn(f"{name}: some runs used under half the budget — deliberate?")

        if len(rs.meta["runs"]) < MIN_SEEDS:
            c.fail(f"{name}: {len(rs.meta['runs'])} seeds, the protocol requires {MIN_SEEDS}")

        if len(set(rs.seeds)) != len(rs.seeds):
            c.fail(f"{name}: seeds are not distinct — the runs are not independent")

        problems = verify_environment_match(rs.meta["environment"])
        for problem in problems:
            c.fail(f"{name}: {problem}")

        if not problems and len(rs.meta["runs"]) >= MIN_SEEDS and not over:
            c.ok(f"{name}: {len(rs.meta['runs'])} seeds, budget respected, environment consistent")


def _notebook_text(path: Path) -> str:
    try:
        nb = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return ""
    return "\n".join("".join(cell.get("source", [])) for cell in nb.get("cells", []))


def check_statistics(c: Check) -> None:
    seen_required = False
    for path in sorted(NOTEBOOKS.glob("*.ipynb")):
        text = _notebook_text(path)
        for pattern, why in FORBIDDEN_STATS:
            if pattern.search(text):
                c.fail(f"{path.name}: {why}")
        if REQUIRED_STATS.search(text):
            seen_required = True

    if not seen_required and any(NOTEBOOKS.glob("*.ipynb")):
        c.warn("no non-parametric test found in any notebook yet")
    elif seen_required:
        c.ok("statistics: a non-parametric test is used")


def check_chaining(c: Check) -> None:
    for label, filename, predecessor in MILESTONES:
        path = NOTEBOOKS / filename
        if not path.exists():
            continue
        if predecessor is None:
            continue
        text = _notebook_text(path)
        if predecessor not in text:
            c.fail(
                f"{filename}: does not cite {predecessor} by name. Each milestone must "
                f"carry forward a named result from its predecessor or it is not scored"
            )
        else:
            c.ok(f"chaining: {label} cites {predecessor}")


def check_ledger(c: Check) -> None:
    ledger = ROOT / "AI_LEDGER.md"
    if not ledger.exists():
        c.fail("AI_LEDGER.md is missing. Declaring no AI use is fine, but it must be declared")
        return
    text = ledger.read_text(encoding="utf-8")

    if "<!-- add entries below -->" in text and "no AI assistant" not in text:
        c.fail("AI_LEDGER.md is still the unedited template")
        return
    if "Choose one and delete the other" in text:
        c.fail("AI_LEDGER.md: delete the declaration you are not making")
        return
    if "no AI assistant" in text:
        c.ok("AI ledger: no-AI declaration present")
        return
    if "### Case 1" in text and len(text.split("### Case 1")[1].strip()) < 120:
        c.fail(
            "AI_LEDGER.md section 3 is empty. That section is the graded one: "
            "document a case where the model was wrong and how you caught it"
        )
        return
    c.ok("AI ledger: present and edited")


def check_visualization(c: Check) -> None:
    figures = ROOT / "figures"
    produced = list(figures.glob("*")) if figures.exists() else []
    if not produced:
        c.warn("no files in figures/ — the visualization deliverable is required by M2")
    else:
        c.ok(f"visualization: {len(produced)} file(s) in figures/")


def main() -> int:
    c = Check()
    check_environment(c)
    check_identity(c)
    check_runlogs(c)
    check_statistics(c)
    check_chaining(c)
    check_ledger(c)
    check_visualization(c)

    width = 68
    print("=" * width)
    print("  SELF-CHECK — the structural checks the autograder runs")
    print("=" * width)

    for message in c.passed:
        print(f"  [ok]   {message}")
    for message in c.warnings:
        print(f"  [warn] {message}")
    for message in c.failures:
        print(f"  [FAIL] {message}")

    print("=" * width)
    if c.failures:
        print(f"  {len(c.failures)} blocking problem(s). Fix these before submitting.")
        return 1
    if c.warnings:
        print(f"  No blocking problems. {len(c.warnings)} warning(s) — check they are deliberate.")
        return 0
    print("  All structural checks pass.")
    print("  This does not mean your analysis is good; it means it can be graded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
