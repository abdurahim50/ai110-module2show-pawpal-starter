# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Running the CLI demo (`python main.py`) produces:

```
(.venv) yongh@cyberOps:~/code/codepath/ai110-module2show-pawpal-starter$ python main.py
Today's Schedule for Jordan (sorted by time)
============================================
08:00  Morning walk       [high]
08:00  Feeding            [high]
12:00  Enrichment play    [medium]
18:00  Evening walk       [medium]
============================================

Pending tasks: 4
Biscuit's tasks: ['Evening walk', 'Morning walk']

Conflict check:
  ⚠ Conflict at 08:00: Morning walk, Feeding

Next free slot for a 45-min grooming session:
  earliest opening: 08:30

Completing Biscuit's 'Morning walk' (daily)...
  done=True; next occurrence due 2026-07-06
```

The demo adds tasks out of order to show `sort_by_time()`, filters by status
and pet, flags the 08:00 clash, finds the earliest free slot for a new 45-minute
task via `find_next_slot()`, and shows a completed daily task spawning its next
occurrence.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite (`tests/test_pawpal.py`, 14 tests) covers:

- **Core behavior** — marking a task complete, adding tasks to a pet.
- **Sorting** — `sort_by_time()` returns tasks in chronological order; `build_plan()` places high-priority tasks first.
- **Filtering** — by completion status and by pet name.
- **Recurrence** — completing a daily task creates the next day's instance; one-off tasks create nothing.
- **Conflict detection** — duplicate times are flagged, unique times are not.
- **Next available slot** — `find_next_slot()` returns `day_start` for an empty plan, finds the gap between fixed appointments, and returns `None` when the day is full.
- **Edge case** — an owner/pet with no tasks yields an empty plan.

Successful run:

```
(.venv) yongh@cyberOps:~/code/codepath/ai110-module2show-pawpal-starter$ python -m pytest
============================================================ test session starts =============================================================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yongh/code/codepath/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 14 items

tests/test_pawpal.py ..............                                                                                                     [100%]

============================================================= 14 passed in 0.03s =============================================================
```

**Confidence level: ★★★★☆ (4/5)** — every core behavior and the main edge cases
are covered and passing. Held back one star because the suite does not yet test
duration-overlap conflicts or invalid input (e.g., a malformed `HH:MM` time).

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time` orders by HH:MM (untimed last); `sort_tasks` orders by priority then duration for plan packing. |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_pet()` | Filter tasks by completion status, or narrow to a single pet's tasks. |
| Conflict handling | `Scheduler.find_time_conflicts()`, `Scheduler.detect_conflicts()` | `find_time_conflicts` returns warning strings for exact same-time tasks; `detect_conflicts` finds duration overlaps in a built plan. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task auto-creates the next instance with `due_date` advanced via `timedelta`. |
| Next available slot | `Scheduler.find_next_slot()` | Scans the day window for the earliest free gap long enough to hold a new flexible task, skipping around fixed appointments; returns `None` when the day is full. |

## 📸 Demo Walkthrough

Launch the app with `streamlit run app.py`. The single-page UI is organized top
to bottom: **Owner** preferences, **Pets**, **Add a task**, the live per-pet
task list, and **Build Schedule**.

### Main UI features and actions

- **Owner preferences** — set the owner's name, the time the day starts
  (`HH:MM`), and the total minutes available today. These become the
  `Scheduler`'s time budget.
- **Add a pet** — enter name, species, breed, and age; a green `st.success`
  banner confirms the add.
- **Add a task** — pick the pet, then set title, category, duration, priority,
  recurrence (`none` / `daily` / `weekly`), and an optional fixed `HH:MM` time.
- **Per-pet task list** — each pet expands to show its tasks with time,
  priority, and a **Mark done** button. Completing a `daily`/`weekly` task
  auto-spawns its next occurrence in the list.
- **Build Schedule** — generates the prioritized, time-boxed plan as a table,
  surfaces conflict warnings, and offers a "Why this plan?" explanation.

### Example workflow

1. Set the owner to **Jordan**, day start **08:00**, available minutes **180**.
2. Add a pet: **Biscuit** (dog).
3. Add two tasks for Biscuit: a **Morning walk** (30 min, high, `08:00`, daily)
   and an **Evening walk** (30 min, medium, `18:00`, daily).
4. Add a cat, **Mochi**, with a **Feeding** task (10 min, high, `08:00`) — the
   same `08:00` slot as the morning walk, on purpose.
5. Click **Generate schedule** to view today's plan and the conflict warning.
6. Click **Mark done** on the morning walk — it flips to ✓ and the next day's
   occurrence appears automatically.

### Key Scheduler behaviors shown

- **Sorting** — `build_plan()` orders the plan by priority (high first), then
  shorter duration, then title, and lays it out along the timeline; the table
  renders start/end times in chronological order.
- **Time-budget packing** — with only 180 minutes available, lower-priority
  tasks are skipped once the budget is spent, so essential care is guaranteed.
- **Conflict warnings** — `find_time_conflicts()` detects the two `08:00`
  tasks and the UI raises a yellow `st.warning` (`⚠ Conflict at 08:00: Morning
  walk, Feeding`), so a clash is visible *before* the owner commits to the day.
- **Daily recurrence** — completing the daily morning walk uses
  `Task.next_occurrence()` to enqueue tomorrow's instance with the `due_date`
  advanced by one day.
- **Explainability** — the "Why this plan?" expander prints
  `Scheduler.explain()`, a plain-language rationale for the ordering.

### Sample CLI output

The same logic layer runs headless via `python main.py`:

```
(.venv) yongh@cyberOps:~/code/codepath/ai110-module2show-pawpal-starter$ python main.py
Today's Schedule for Jordan (sorted by time)
============================================
08:00  Morning walk       [high]
08:00  Feeding            [high]
12:00  Enrichment play    [medium]
18:00  Evening walk       [medium]
============================================

Pending tasks: 4
Biscuit's tasks: ['Evening walk', 'Morning walk']

Conflict check:
  ⚠ Conflict at 08:00: Morning walk, Feeding

Next free slot for a 45-min grooming session:
  earliest opening: 08:30

Completing Biscuit's 'Morning walk' (daily)...
  done=True; next occurrence due 2026-07-06
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
