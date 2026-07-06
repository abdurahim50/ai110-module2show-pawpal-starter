"""CLI demo for PawPal+ — verifies the backend logic in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=180)
    biscuit = Pet("Biscuit", "dog", "Golden Retriever", 4)
    mochi = Pet("Mochi", "cat", "Tabby", 2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added out of time order on purpose, to show sort_by_time().
    biscuit.add_task(Task("Evening walk", "walk", 30, "medium", time="18:00", recurrence="daily"))
    biscuit.add_task(Task("Morning walk", "walk", 30, "high", time="08:00", recurrence="daily"))
    mochi.add_task(Task("Feeding", "feeding", 10, "high", time="08:00", recurrence="daily"))  # 08:00 clash
    mochi.add_task(Task("Enrichment play", "enrichment", 20, "medium", time="12:00"))

    scheduler = Scheduler(day_start=owner.wake_time, available_minutes=owner.available_minutes)
    tasks = owner.all_tasks()

    print(f"Today's Schedule for {owner.name} (sorted by time)")
    print("=" * 44)
    for t in scheduler.sort_by_time(tasks):
        print(f"{t.time or '  ?  '}  {t.title:18} [{t.priority}]")
    print("=" * 44)

    print(f"\nPending tasks: {len(scheduler.filter_by_status(tasks, done=False))}")
    print("Biscuit's tasks:", [t.title for t in scheduler.filter_by_pet(owner, "Biscuit")])

    print("\nConflict check:")
    conflicts = scheduler.find_time_conflicts(tasks)
    print("\n".join(f"  {w}" for w in conflicts) if conflicts else "  No conflicts.")

    print("\nCompleting Biscuit's 'Morning walk' (daily)...")
    morning = next(t for t in biscuit.tasks if t.title == "Morning walk")
    nxt = biscuit.complete_task(morning)
    print(f"  done={morning.done}; next occurrence due {nxt.due_date}")


if __name__ == "__main__":
    main()
