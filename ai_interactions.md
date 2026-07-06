# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

For the optional-extensions phase I asked the agent to add a third algorithmic
capability — a **"next available slot" finder** — that, given today's built plan
and a proposed task duration, returns the earliest `HH:MM` opening that fits
around the fixed appointments, and to integrate it end-to-end (logic, tests,
CLI, UI, and docs).

**What did the agent do?**

Files modified:

- `pawpal_system.py` — added `Scheduler.find_next_slot(plan, duration_minutes)`,
  a greedy gap scan over the day window `[day_start, day_start + available_minutes)`
  that walks the sorted busy intervals and returns the first gap ≥ the requested
  duration, or `None` when the day is full.
- `tests/test_pawpal.py` — added 3 tests: empty plan → returns `day_start`; a gap
  between two fixed appointments is found (08:30); and a full day returns `None`.
  Suite went from 11 → 14 passing.
- `main.py` — added a CLI demo line printing the earliest opening for a 45-minute
  grooming session (`earliest opening: 08:30`).
- `app.py` — added a **"Find a free slot"** section with a duration input and a
  button that reports the slot via `st.success` / `st.warning`.
- `diagrams/uml_final.mmd` — added `find_next_slot` to the `Scheduler` class.
- `README.md` — added a Features-table row and refreshed the sample CLI output.

Commands run: `pytest` (14 passed) and `python main.py` to confirm the demo
output before documenting it.

**What did you have to verify or fix manually?**

I checked the gap-scan by hand against the demo data: with 08:00 appointments
ending at 08:30 and the next fixed task at 12:00, the earliest 45-minute opening
should be 08:30 — which matched. The key thing I verified was the boundary
condition: the method must advance the cursor with `max(cursor, end)` so
overlapping/duplicate-time entries (the intentional 08:00 clash) don't produce a
spurious earlier slot. I also confirmed it returns `None` (not `"08:00"`) when
`available_minutes` leaves no room, and kept the "gap must be ≥ duration, not >"
semantics so a task can fill a slot exactly.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
