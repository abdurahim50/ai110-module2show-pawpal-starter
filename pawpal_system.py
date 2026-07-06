"""PawPal+ backend logic layer.

Core domain classes (Owner, Pet, Task) and the Scheduler that turns a set
of tasks into an ordered daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


def _to_minutes(hhmm: str) -> int:
    """Convert an 'HH:MM' string into minutes past midnight."""
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


def _to_hhmm(minutes: int) -> str:
    """Convert minutes past midnight back into an 'HH:MM' string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, appointment, ...)."""

    title: str
    category: str = "general"
    duration_minutes: int = 15
    priority: str = "medium"
    recurrence: str = "none"        # none | daily | weekly
    fixed_time: str | None = None   # "HH:MM" for appointments, else None
    done: bool = False

    def priority_score(self) -> int:
        """Return this task's priority as a number (high=3 .. low=1)."""
        return PRIORITY_RANK.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.done = True


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own care tasks."""

    name: str
    species: str = "dog"
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove every task with the given title from this pet."""
        self.tasks = [t for t in self.tasks if t.title != title]


@dataclass
class Owner:
    """The pet owner and their scheduling preferences."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 240
    wake_time: str = "08:00"

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the owner's pet with the given name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def all_tasks(self) -> list[Task]:
        """Collect every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Turns a collection of tasks into an ordered, time-boxed daily plan."""

    def __init__(self, day_start: str = "08:00", available_minutes: int = 240):
        self.day_start = day_start
        self.available_minutes = available_minutes

    def plan_for_owner(self, owner: Owner) -> list[dict]:
        """Build a plan from all of an owner's pets' tasks."""
        return self.build_plan(owner.all_tasks())

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (high first), then shorter, then title."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_score(), t.duration_minutes, t.title),
        )

    def build_plan(self, tasks: list[Task]) -> list[dict]:
        """Pack unfinished tasks into the day, honoring fixed times and budget."""
        ordered = self.sort_tasks([t for t in tasks if not t.done])
        plan: list[dict] = []
        cursor = _to_minutes(self.day_start)
        used = 0
        for task in ordered:
            if used + task.duration_minutes > self.available_minutes:
                continue  # out of time — skip this (lower-priority) task
            start = _to_minutes(task.fixed_time) if task.fixed_time else cursor
            end = start + task.duration_minutes
            plan.append(
                {
                    "task": task,
                    "start": _to_hhmm(start),
                    "end": _to_hhmm(end),
                    "start_min": start,
                    "end_min": end,
                }
            )
            used += task.duration_minutes
            cursor = max(cursor, end)
        plan.sort(key=lambda entry: entry["start_min"])
        return plan

    def detect_conflicts(self, plan: list[dict]) -> list[dict]:
        """Return pairs of plan entries whose time slots overlap."""
        conflicts: list[dict] = []
        ordered = sorted(plan, key=lambda entry: entry["start_min"])
        for first, second in zip(ordered, ordered[1:]):
            if second["start_min"] < first["end_min"]:
                conflicts.append(
                    {
                        "first": first["task"].title,
                        "second": second["task"].title,
                        "overlap_minutes": first["end_min"] - second["start_min"],
                    }
                )
        return conflicts

    def explain(self, plan: list[dict]) -> str:
        """Return a human-readable rationale for the ordered plan."""
        if not plan:
            return "No tasks scheduled — nothing to plan today."
        lines = ["Plan (highest priority first, packed into available time):"]
        for entry in plan:
            task = entry["task"]
            lines.append(
                f"  {entry['start']}-{entry['end']}  {task.title} "
                f"({task.duration_minutes} min, {task.priority} priority)"
            )
        return "\n".join(lines)
