"""Verify the execution environment satisfies the reproducibility contract.

Runs automatically when the devcontainer is created, and can be run by hand at
any time. Exits non-zero with an explicit message on any violation, because a
silently wrong environment produces results the autograder will reject as
fabricated.
"""

from __future__ import annotations

import os
import platform
import sys

MIN_PYTHON = (3, 10)

# Multithreaded BLAS reorders floating-point reductions non-deterministically.
# Every backend must be pinned to one thread or seeded runs stop being bitwise
# reproducible, which breaks the autograder's re-execution check.
SINGLE_THREAD_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)

REQUIRED_PACKAGES = {
    "numpy": "2.5.2",
    "scipy": "1.18.1",
    "matplotlib": "3.11.1",
    "yaml": None,  # PyYAML exposes no reliable __version__ across releases
}


def _fail(problems: list[str]) -> None:
    print("\nEnvironment verification FAILED:\n", file=sys.stderr)
    for problem in problems:
        print(f"  - {problem}", file=sys.stderr)
    print(
        "\nWork inside the provided devcontainer. Results produced outside it "
        "may not reproduce, and the autograder compares your reported values "
        "against a re-execution.\n",
        file=sys.stderr,
    )
    sys.exit(1)


def check_python(problems: list[str]) -> None:
    if sys.version_info < MIN_PYTHON:
        problems.append(
            f"Python {'.'.join(map(str, MIN_PYTHON))}+ is required, found "
            f"{platform.python_version()}. otter-grader 7 dropped Python 3.9; "
            "the macOS system interpreter is too old."
        )


def check_threading(problems: list[str]) -> None:
    for var in SINGLE_THREAD_VARS:
        value = os.environ.get(var)
        if value != "1":
            problems.append(
                f"{var} is {value!r}, expected '1'. Multithreaded BLAS breaks "
                "bitwise reproducibility of seeded runs."
            )

    if os.environ.get("PYTHONHASHSEED") != "0":
        problems.append(
            f"PYTHONHASHSEED is {os.environ.get('PYTHONHASHSEED')!r}, expected "
            "'0', so that any hash-ordered iteration is at least stable."
        )


def check_packages(problems: list[str]) -> None:
    for module_name, expected in REQUIRED_PACKAGES.items():
        try:
            module = __import__(module_name)
        except ImportError:
            problems.append(f"required package {module_name!r} is not installed")
            continue

        if expected is None:
            continue

        found = getattr(module, "__version__", None)
        if found != expected:
            problems.append(
                f"{module_name} is {found}, expected {expected} "
                "(the lock file pins it; an unpinned version can change results)"
            )


def check_determinism(problems: list[str]) -> None:
    """Confirm a seeded draw reproduces, catching a broken RNG outright."""
    try:
        import numpy as np
    except ImportError:
        return  # already reported by check_packages

    first = np.random.default_rng(20260906).standard_normal(1000).sum()
    second = np.random.default_rng(20260906).standard_normal(1000).sum()
    if first != second:
        problems.append(
            "a seeded numpy draw did not reproduce within this process; "
            "the environment cannot support reproducible experiments"
        )


def main() -> None:
    problems: list[str] = []
    check_python(problems)
    check_threading(problems)
    check_packages(problems)
    check_determinism(problems)

    if problems:
        _fail(problems)

    print("Environment OK")
    print(f"  python   {platform.python_version()}")
    print(f"  platform {platform.system()} {platform.machine()}")
    print(f"  threads  pinned to 1 across {len(SINGLE_THREAD_VARS)} backends")


if __name__ == "__main__":
    main()
