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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
