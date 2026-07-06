# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions the app supports: (1) add a pet to the owner's profile,
(2) add care tasks (walks, feeding, meds, appointments) to a pet with a
duration and priority, and (3) generate and view today's ordered plan with a
short explanation.

I designed four classes:

- **Task** (dataclass) — what a care activity is: title, category, duration,
  priority, recurrence, and an optional fixed time for appointments.
- **Pet** (dataclass) — owns a list of its Tasks and can add/remove them.
- **Owner** (dataclass) — holds one or more Pets plus scheduling preferences
  (available minutes per day, wake time) and can aggregate every pet's tasks.
- **Scheduler** (behavior class, not a data record) — the algorithms: sorting
  tasks by priority, packing them into the available time, detecting time
  conflicts, and explaining the resulting plan.

I split data (Task/Pet/Owner as dataclasses) from behavior (Scheduler) so the
scheduling logic can evolve without changing the domain model.

**b. Design changes**

Two changes surfaced during implementation:

1. **Added `done` + `mark_complete()` to `Task`.** The original skeleton had no
   completion state, but a daily planner needs to drop finished tasks from the
   schedule, so I added a boolean status and a method to flip it.
2. **Added `Scheduler.plan_for_owner(owner)`.** Originally the Scheduler only
   took a raw list of tasks. It felt cleaner for the Scheduler to pull tasks
   straight from the Owner (via `owner.all_tasks()`), so I added a convenience
   method. This makes the Owner the single source of truth for "what needs
   doing" and keeps the CLI/UI callers simple.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: the owner's total available minutes
for the day, each task's priority (high/medium/low), and each task's fixed time
of day (for appointments that can't move). Priority mattered most — when time
runs short, `build_plan()` packs high-priority tasks first and simply skips the
lowest-priority ones, because a busy owner would rather guarantee the walk and
meds happen than fit in an optional play session.

**b. Tradeoffs**

`find_time_conflicts()` only flags tasks that share the **exact same** HH:MM
start time — it does not check whether two tasks with different start times
overlap because of their durations (e.g., a 30-minute task at 08:00 running
into a task at 08:15). I chose exact-match because it is simple, fast, and
returns a clear warning string without crashing, which is enough to alert the
owner to the most common clash. The heavier duration-overlap check lives
separately in `detect_conflicts()`, which runs against a fully built plan; I
kept the two apart so the lightweight per-task check stays cheap and readable.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI across every phase but in different modes:

- **Design brainstorming** — I described the scenario and asked the assistant to
  help pressure-test my four-class split (Task/Pet/Owner/Scheduler). The most
  useful prompts were constraint-first ones like *"which of these belong on the
  data classes vs. the Scheduler?"* rather than *"write the app for me."*
- **Refactoring** — after the logic worked, I asked for help tightening method
  names and docstrings so the UML and the code would stay in sync.
- **Debugging** — the assistant helped me reason about the Streamlit rerun model,
  which is why the Owner lives in `st.session_state` and the mark-done loop
  iterates over a `list(pet.tasks)` snapshot (completing a recurring task appends
  a new occurrence mid-iteration).

The most helpful prompts were specific and included the actual file, e.g.
*"here is `pawpal_system.py` — does the UML still match, and what's missing?"*
Vague prompts produced generic code; grounded prompts produced targeted edits.

**b. Judgment and verification**

- **A suggestion I modified to keep the design clean:** the assistant proposed
  folding all conflict logic into one method that checked both same-time clashes
  and duration overlaps. I split it back into `find_time_conflicts()` (cheap,
  exact `HH:MM` match, returns owner-friendly warning strings) and
  `detect_conflicts()` (heavier overlap check against a fully built plan). Keeping
  them apart matched how the UI actually uses them — a quick warning before
  scheduling vs. a post-plan sanity check — and kept each method small.
- **How I verified suggestions:** I treated AI output as a draft, not an answer. I
  ran `python main.py` to eyeball behavior, kept the pytest suite (11 tests)
  green after each change, and checked that any new method appeared in both the
  code and `diagrams/uml_final.mmd`. When a suggestion didn't map to a test or a
  concrete UI action, I dropped it.

**c. AI strategy: features and session hygiene**

- **Most effective features:** attaching the actual source file to a prompt (so
  feedback was grounded in my real code, not a hallucinated version) and asking
  the assistant to explain *why* before generating code, which let me catch
  design mismatches early. Inline refactor/rename help was the biggest time-saver
  for the Scheduler.
- **Separate sessions per phase:** I kept design, implementation, testing, and
  documentation in separate chats. Each session started clean with only the
  context that phase needed, so the assistant didn't drag stale assumptions
  forward, and I could revisit a phase's reasoning later without scrolling past
  unrelated code.
- **Being the lead architect:** the AI was fast at producing options, but it had
  no opinion about *my* constraints — that a busy owner would rather guarantee
  the walk than fit an optional play session, or that the data/behavior split
  matters. Every accept/reject decision, the class boundaries, and the tradeoffs
  were mine; the AI accelerated the typing, not the judgment.

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`, 14 tests) covers the behaviors that would
silently corrupt a daily plan if they broke:

- **Sorting** — `sort_by_time()` returns chronological order and `build_plan()`
  places high-priority tasks first.
- **Filtering** — by completion status and by pet name.
- **Recurrence** — completing a `daily` task creates the next day's instance; a
  one-off task creates nothing.
- **Conflict detection** — duplicate times are flagged, unique times are not.
- **Next available slot** — `find_next_slot()` returns the day start for an empty
  plan, finds the gap between fixed appointments, and returns `None` on a full day.
- **Core + edge case** — marking a task complete, and an owner/pet with no tasks
  yielding an empty plan.

These matter because sorting, recurrence, and conflict flagging are the whole
value of the app — a wrong sort or a missing recurrence is worse than an obvious
crash because the owner wouldn't notice.

**b. Confidence**

Confidence: **★★★★☆ (4/5)**. Every core behavior and the main edge cases pass.
With more time I'd next test **duration overlaps** (a 30-min task at 08:00
running into an 08:15 task, which `find_time_conflicts()` intentionally ignores)
and **invalid input** — a malformed `HH:MM` string currently reaches
`_to_minutes()` and would raise.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean split between the data classes and the
`Scheduler`. Because scheduling lives in one place, I could evolve the algorithm
(add packing, conflict checks, an `explain()` rationale) without touching the
domain model, and the same logic layer powers both the CLI (`main.py`) and the
Streamlit UI unchanged.

**b. What you would improve**

I'd replace `HH:MM` strings with real `datetime`/`time` objects to remove the
brittle `_to_minutes()`/`_to_hhmm()` conversions and get input validation for
free, and I'd unify the two conflict methods behind one interval-overlap check so
the UI can warn about duration clashes, not just exact-time collisions.

**c. Key takeaway**

The most important lesson is that the leverage in AI-assisted engineering is
still *system design and judgment*. The AI produced working code quickly, but the
decisions that made the project coherent — the class boundaries, the
data/behavior split, choosing to guarantee high-priority tasks over fitting
everything in — were mine to own and to verify against tests. I stayed the
architect; the AI was a very fast pair of hands.
