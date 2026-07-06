"""CLI demo for PawPal+ — verifies the backend logic in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=180)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=4)
    mochi = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    biscuit.add_task(Task("Morning walk", "walk", 30, "high", recurrence="daily"))
    biscuit.add_task(Task("Vet appointment", "appointment", 30, "high", fixed_time="14:00"))
    mochi.add_task(Task("Feeding", "feeding", 10, "high", recurrence="daily"))
    mochi.add_task(Task("Enrichment play", "enrichment", 20, "medium"))

    scheduler = Scheduler(day_start=owner.wake_time, available_minutes=owner.available_minutes)
    plan = scheduler.plan_for_owner(owner)

    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    for entry in plan:
        task = entry["task"]
        print(f"{entry['start']}-{entry['end']}  {task.title:18} [{task.priority}]")
    print("=" * 40)

    conflicts = scheduler.detect_conflicts(plan)
    if conflicts:
        print("\n⚠ Conflicts detected:")
        for c in conflicts:
            print(f"  {c['first']} overlaps {c['second']} by {c['overlap_minutes']} min")


if __name__ == "__main__":
    main()
