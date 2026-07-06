"""CLI demo for PawPal+ — verifies the backend logic in the terminal."""

from tabulate import tabulate

from pawpal_system import Owner, Pet, Task, Scheduler

# --- Output formatting helpers (SF4: professional formatting) ----------------
CATEGORY_EMOJI = {
    "walk": "🚶", "feeding": "🍽️", "meds": "💊", "appointment": "🏥",
    "enrichment": "🧸", "grooming": "✂️", "general": "📌",
}
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def _emoji(task: Task) -> str:
    """Return a category icon for a task (falls back to the general pin)."""
    return CATEGORY_EMOJI.get(task.category, "📌")


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

    # Structured, emoji-labeled table via tabulate (SF4).
    print(f"Today's Schedule for {owner.name} (sorted by time)")
    rows = [
        [t.time or "  ?  ", f"{_emoji(t)} {t.title}", f"{PRIORITY_EMOJI[t.priority]} {t.priority}"]
        for t in scheduler.sort_by_time(tasks)
    ]
    print(tabulate(rows, headers=["Time", "Task", "Priority"], tablefmt="rounded_outline"))

    print(f"\nPending tasks: {len(scheduler.filter_by_status(tasks, done=False))}")
    print("Biscuit's tasks:", [t.title for t in scheduler.filter_by_pet(owner, "Biscuit")])

    print("\nConflict check:")
    conflicts = scheduler.find_time_conflicts(tasks)
    print("\n".join(f"  {w}" for w in conflicts) if conflicts else "  No conflicts.")

    print("\nNext free slot for a 45-min grooming session:")
    plan = scheduler.build_plan(tasks)
    slot = scheduler.find_next_slot(plan, 45)
    print(f"  earliest opening: {slot}" if slot else "  no room left today.")

    print("\nCompleting Biscuit's 'Morning walk' (daily)...")
    morning = next(t for t in biscuit.tasks if t.title == "Morning walk")
    nxt = biscuit.complete_task(morning)
    print(f"  done={morning.done}; next occurrence due {nxt.due_date}")

    # Persistence round trip (SF2): save the profile and read it straight back.
    print("\nPersistence check (data.json):")
    owner.save_to_json("data.json")
    reloaded = Owner.load_from_json("data.json")
    print(f"  saved and reloaded {len(reloaded.pets)} pets, {len(reloaded.all_tasks())} tasks.")


if __name__ == "__main__":
    main()
