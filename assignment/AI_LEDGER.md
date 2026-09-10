# AI Ledger — required deliverable

Copy this file to the root of your repository as `AI_LEDGER.md` and fill it in
**as you work**, not afterwards. A ledger reconstructed at the end is usually
visible as one, and it defeats the purpose.

## Why this exists

Language models are part of the research toolkit now, and pretending otherwise
would make this course less useful, not more honest. What distinguishes a
doctoral practitioner is not avoiding them but **knowing when the output is
wrong**. That judgment is what this deliverable assesses, and it is worth 15 of
the 40 rubric points.

You are not penalized for using AI. You are not penalized for declaring you did
not. You are penalized for using it uncritically.

---

## Section 1 — Declaration

Choose one and delete the other.

> **I used one or more AI assistants on this assignment.** The interactions
> material to the submitted work are recorded in Section 2, and Section 3
> documents at least one case where the assistant was wrong.

> **I used no AI assistant on this assignment.** All code, analysis and prose are
> my own. I verified my statistical procedure against [cite the source you used
> instead]. — *signed, student ID, date*

A no-AI declaration is complete and unpenalized. It is scored on the evidence of
independent verification it cites.

---

## Section 2 — Interaction log

One entry per interaction that materially affected the submitted work. Routine
autocompletion does not need an entry; anything that shaped a design decision,
an implementation, or an analysis does.

### Entry template

```markdown
#### E-001 · 2026-09-14 · milestone M0

**Tool:** <name and version>

**Prompt:**
> <what you actually asked, verbatim>

**Response summary:** <what it produced, in your words — not a transcript dump>

**Verdict:** accepted | modified | rejected

**Justification:** <why. If modified, what you changed and why. If rejected,
what was wrong with it.>

**Verification performed:** <what you actually did to check. "It ran" is not
verification. "I compared its cooling schedule against Kirkpatrick's original
formulation and ran both on 30 seeds" is.>
```

### Your entries

<!-- add entries below -->

---

## Section 3 — Where it was wrong *(this is the graded section)*

Document **at least one** concrete case in which the assistant produced
something incorrect, and how you caught it.

This must be substantive: a wrong claim, an inappropriate method, a subtly
incorrect implementation, a confident statement that does not survive checking.
"It had a typo" or "it used an old API" does not qualify.

```markdown
### Case 1

**What it claimed or produced:**

**Why that is wrong:**

**How I detected it:** <the specific evidence — an experiment, a source, a
derivation, a failing check. Not "it seemed off".>

**What I did instead:**
```

If you genuinely encountered no error, say so explicitly and describe the
verification that would have caught one. That is a weaker but honest answer, and
it is marked as such.

---

## Section 4 — Reflection *(brief)*

Two or three sentences: where did assistance help most, and where did it cost
you more time than it saved?

---

## What scores well, and what does not

| | |
|---|---|
| ✅ One well-documented catch with real evidence | Top band |
| ✅ Rejected suggestions, with the reasoning | Strong |
| ✅ No-AI declaration citing independent verification | Top band |
| ❌ Fifty entries, all "accepted", no critique | Developing band, regardless of length |
| ❌ A transcript dump with no verdicts | Not a ledger |
| ❌ Ledger written after the fact to satisfy the requirement | Usually visible; marked accordingly |

## A hint about where to look

The single most likely place for an assistant to be confidently wrong in this
assignment is the **statistical comparison**. Asked to compare metaheuristics,
models very often reach for a t-test, or report best-of-N without dispersion.
Both are rejection-worthy errors in this literature. If you accepted such a
suggestion without noticing, the autograder will find it — and it would have
made an excellent Section 3.
