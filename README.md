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

Completing Biscuit's 'Morning walk' (daily)...
  done=True; next occurrence due 2026-07-06
```

The demo adds tasks out of order to show `sort_by_time()`, filters by status
and pet, flags the 08:00 clash, and shows a completed daily task spawning its
next occurrence.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

The suite (`tests/test_pawpal.py`, 11 tests) covers:

- **Core behavior** — marking a task complete, adding tasks to a pet.
- **Sorting** — `sort_by_time()` returns tasks in chronological order; `build_plan()` places high-priority tasks first.
- **Filtering** — by completion status and by pet name.
- **Recurrence** — completing a daily task creates the next day's instance; one-off tasks create nothing.
- **Conflict detection** — duplicate times are flagged, unique times are not.
- **Edge case** — an owner/pet with no tasks yields an empty plan.

Successful run:

```
(.venv) yongh@cyberOps:~/code/codepath/ai110-module2show-pawpal-starter$ python -m pytest
============================================================ test session starts =============================================================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/yongh/code/codepath/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 11 items

tests/test_pawpal.py ...........                                                                                                       [100%]

============================================================= 11 passed in 0.01s =============================================================
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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
