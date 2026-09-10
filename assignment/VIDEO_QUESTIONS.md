# Video defence — question bank

At recording time you will draw **two** questions from this bank. Draw them with

```bash
python scripts/draw_video_questions.py --student-id A01234567
```

and state the drawn numbers at the start of your recording.

**The bank is published on purpose.** Every question here can only be answered
by reference to *your own* instance, *your own* runs and *your own* decisions.
Knowing them in advance lets you prepare properly; it does not let you prepare a
generic answer, and an answer that would fit any submission scores as if no
answer were given.

Five minutes total, including the two questions. Have your figures on screen.

---

## A · Your instance

1. Show your instance. Point at the region that gave your algorithms the most
   trouble, and say how you know that rather than assuming it.
2. What fraction of random deployments on *your* instance are feasible? What did
   that number change about your approach?
3. Your instance has per-site power caps. Identify a site whose cap materially
   constrained your solution, and explain the consequence.
4. Where does your demand field concentrate, and how did that shape which sites
   you activated?

## B · Your convergence behaviour

5. Show one convergence curve. Explain what is happening at the point where it
   flattens.
6. Identify a run of yours that stagnated. What is your evidence that it
   stagnated rather than converged?
7. Your best and median runs differ. Show both and explain the gap.
8. Point to the iteration where your best-so-far last improved. What does the
   budget spent after that tell you about your configuration?
9. Show your diversity measure over time for one PSO run and read it aloud —
   what is it saying?

## C · Your parameters

10. Why *those* values of `w`, `c1` and `c2`? Show where they sit in the
    Clerc–Kennedy stability region.
11. What happens to your PSO if you raise `w` to 0.95? Predict it first, then
    justify the prediction from theory rather than from having tried it.
12. Justify your tabu tenure. What did you observe at a clearly wrong value?
13. Justify your cooling schedule. What is your acceptance rate at the start and
    at the end of a run?
14. Show that your MMAS pheromone bounds are actually binding. If they are not,
    say what that means.
15. Your evaporation rate: what did a much higher and a much lower value do to
    your search?

## D · Your budget

16. Where did your 5 000 evaluations go? Account for them.
17. Did you spend budget on tuning? How did you keep tuning from contaminating
    your reported comparison?
18. If your budget were cut to 1 000, which algorithm would you choose and why?

## E · Your comparison

19. State your main claim and the test that supports it. Why that test and not a
    t-test?
20. You applied a multiple-comparison correction. Show what your conclusion
    would have been without it.
21. Your effect size: is your significant difference also a difference that
    matters? Argue either way from your numbers.
22. What does your comparison *not* license you to claim?
23. **Teams:** did your ranking hold across both instances? If it inverted, what
    does that mean; if it held, why is that not proof of general superiority?

## F · Your process

24. Show one thing in your submission you would do differently, and why.
25. From your AI ledger: describe the case where the model was wrong and how you
    caught it.
26. Which design decision in your submission are you least confident about?

---

## How this is marked

The video produces an **individual multiplier** on your team's score, capped at
1.0 — it can confirm or reduce your grade, never raise it above the team's.
Bands are in [`RUBRIC.md`](RUBRIC.md).

In a team, **both members record separately**, each drawing their own questions.
No video means a zero multiplier regardless of how good the submission is.
