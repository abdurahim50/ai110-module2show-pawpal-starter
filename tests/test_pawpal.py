"""Core behavior tests for PawPal+."""

from pawpal_system import Owner, Pet, Task, Scheduler


def test_mark_complete_changes_status():
    task = Task("Feeding", duration_minutes=10, priority="high")
    assert task.done is False
    task.mark_complete()
    assert task.done is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="cat")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", duration_minutes=10))
    assert len(pet.tasks) == 1


def test_plan_orders_high_priority_first():
    scheduler = Scheduler(day_start="08:00", available_minutes=120)
    tasks = [
        Task("Play", duration_minutes=20, priority="low"),
        Task("Walk", duration_minutes=30, priority="high"),
    ]
    plan = scheduler.build_plan(tasks)
    assert plan[0]["task"].title == "Walk"
