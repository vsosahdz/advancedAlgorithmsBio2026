"""Draw the two video-defence questions for a student.

The draw is seeded from the student ID **and the recording date**, so it cannot
be known before the day, yet the instructor can reproduce it exactly from the ID
and date the student states on camera. That makes the draw both unpredictable
and verifiable, which a purely random draw would not be.

Run:  python scripts/draw_video_questions.py --student-id A01234567
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "assignment" / "VIDEO_QUESTIONS.md"
N_DRAWN = 2

# Section A..F questions are numbered list items at the start of a line.
_ITEM = re.compile(r"^(\d+)\.\s+(.*)$")


def load_questions(path: Path) -> dict[int, str]:
    """Parse the numbered questions out of the published bank."""
    questions: dict[int, str] = {}
    current: int | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _ITEM.match(line)
        if match:
            current = int(match.group(1))
            questions[current] = match.group(2).strip()
        elif current is not None and line.startswith("   ") and line.strip():
            questions[current] += " " + line.strip()
        elif not line.strip():
            current = None
    return questions


def draw(student_id: str, date: dt.date, pool: list[int], n: int = N_DRAWN) -> list[int]:
    """Deterministic draw from (student_id, date). Reproducible by the instructor."""
    key = f"{student_id.strip().upper()}|{date.isoformat()}".encode("utf-8")
    digest = hashlib.blake2b(key, digest_size=16).digest()

    # Fisher-Yates driven by the digest, so the result depends on the whole key
    # rather than on a truncated prefix.
    order = list(pool)
    stream = int.from_bytes(digest, "big")
    for i in range(len(order) - 1, 0, -1):
        stream, j = divmod(stream, i + 1)
        order[i], order[j] = order[j], order[i]
    return sorted(order[:n])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-id", required=True)
    parser.add_argument(
        "--date",
        default=None,
        help="recording date YYYY-MM-DD (default: today, UTC). Instructors pass "
        "the date the student stated on camera to reproduce the draw.",
    )
    args = parser.parse_args()

    date = (
        dt.date.fromisoformat(args.date)
        if args.date
        else dt.datetime.now(dt.timezone.utc).date()
    )

    if not QUESTIONS_FILE.exists():
        print(f"question bank not found at {QUESTIONS_FILE}", file=sys.stderr)
        return 1

    questions = load_questions(QUESTIONS_FILE)
    if len(questions) < N_DRAWN:
        print(f"question bank has only {len(questions)} items", file=sys.stderr)
        return 1

    drawn = draw(args.student_id, date, sorted(questions))

    print()
    print("=" * 68)
    print(f"  VIDEO DEFENCE — {args.student_id.strip().upper()}")
    print(f"  Recording date: {date.isoformat()}")
    print("=" * 68)
    print()
    print("  State the date and these question numbers at the start of your")
    print("  recording. Your instructor reproduces this draw from them.")
    print()
    for number in drawn:
        print(f"  Q{number}. {questions[number]}")
        print()
    print("=" * 68)
    print(f"  {len(questions)} questions in the bank · {N_DRAWN} drawn · 5 minutes total")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
