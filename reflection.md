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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
