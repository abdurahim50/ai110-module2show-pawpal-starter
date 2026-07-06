"""PawPal+ backend logic layer.

Core domain classes (Owner, Pet, Task) and the Scheduler that turns a set
of tasks into an ordered daily plan. Skeleton generated from the UML in
diagrams/uml.mmd; method bodies are intentionally unimplemented (Phase 2+).
"""

from __future__ import annotations

from dataclasses import dataclass, field

PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single pet-care task (walk, feeding, meds, appointment, ...)."""

    title: str
    category: str = "general"
    duration_minutes: int = 15
    priority: str = "medium"
    recurrence: str = "none"        # none | daily | weekly
    fixed_time: str | None = None   # "HH:MM" for appointments, else None

    def priority_score(self) -> int:
        """Return a numeric weight for this task's priority."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own care tasks."""

    name: str
    species: str = "dog"
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, title: str) -> None:
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner and their scheduling preferences."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    available_minutes: int = 240
    wake_time: str = "08:00"

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_pet(self, name: str) -> Pet | None:
        raise NotImplementedError

    def all_tasks(self) -> list[Task]:
        """Collect tasks across all of this owner's pets."""
        raise NotImplementedError


class Scheduler:
    """Turns a collection of tasks into an ordered, time-boxed daily plan."""

    def __init__(self, day_start: str = "08:00", available_minutes: int = 240):
        self.day_start = day_start
        self.available_minutes = available_minutes

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (and tie-breakers)."""
        raise NotImplementedError

    def build_plan(self, tasks: list[Task]) -> list[dict]:
        """Assign start times, respecting available time and fixed slots."""
        raise NotImplementedError

    def detect_conflicts(self, plan: list[dict]) -> list[dict]:
        """Find overlapping time slots in a plan."""
        raise NotImplementedError

    def explain(self, plan: list[dict]) -> str:
        """Produce a human-readable rationale for the plan."""
        raise NotImplementedError
