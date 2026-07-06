"""Automated test suite for PawPal+."""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


# --- Core class behavior ----------------------------------------------------
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


# --- Sorting ----------------------------------------------------------------
def test_sort_by_time_is_chronological():
    scheduler = Scheduler()
    tasks = [
        Task("Evening", time="18:00"),
        Task("Morning", time="08:00"),
        Task("Noon", time="12:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.time for t in ordered] == ["08:00", "12:00", "18:00"]


def test_plan_orders_high_priority_first():
    scheduler = Scheduler(day_start="08:00", available_minutes=120)
    tasks = [
        Task("Play", duration_minutes=20, priority="low"),
        Task("Walk", duration_minutes=30, priority="high"),
    ]
    plan = scheduler.build_plan(tasks)
    assert plan[0]["task"].title == "Walk"


# --- Filtering --------------------------------------------------------------
def test_filter_by_status_returns_only_pending():
    scheduler = Scheduler()
    pending_task = Task("Walk")
    done_task = Task("Feed")
    done_task.mark_complete()
    assert scheduler.filter_by_status([pending_task, done_task], done=False) == [pending_task]


def test_filter_by_pet_returns_that_pets_tasks():
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog")
    biscuit.add_task(Task("Walk"))
    owner.add_pet(biscuit)
    owner.add_pet(Pet("Mochi", "cat"))
    scheduler = Scheduler()
    assert [t.title for t in scheduler.filter_by_pet(owner, "Biscuit")] == ["Walk"]


# --- Recurrence -------------------------------------------------------------
def test_completing_daily_task_creates_next_day():
    pet = Pet("Biscuit", "dog")
    task = Task("Walk", priority="high", recurrence="daily", due_date=date(2026, 1, 1))
    pet.add_task(task)
    nxt = pet.complete_task(task)
    assert task.done is True
    assert len(pet.tasks) == 2          # original + next occurrence
    assert nxt.due_date == date(2026, 1, 2)
    assert nxt.done is False


def test_completing_one_off_task_creates_no_new_task():
    pet = Pet("Mochi", "cat")
    task = Task("Vet visit", recurrence="none")
    pet.add_task(task)
    assert pet.complete_task(task) is None
    assert len(pet.tasks) == 1


# --- Conflict detection -----------------------------------------------------
def test_find_time_conflicts_flags_duplicate_times():
    scheduler = Scheduler()
    tasks = [Task("Walk", time="08:00"), Task("Feed", time="08:00")]
    conflicts = scheduler.find_time_conflicts(tasks)
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_find_time_conflicts_none_when_times_unique():
    scheduler = Scheduler()
    tasks = [Task("Walk", time="08:00"), Task("Feed", time="09:00")]
    assert scheduler.find_time_conflicts(tasks) == []


# --- Next available slot ----------------------------------------------------
def test_next_slot_is_day_start_when_plan_empty():
    scheduler = Scheduler(day_start="08:00", available_minutes=240)
    assert scheduler.find_next_slot([], 30) == "08:00"


def test_next_slot_finds_gap_between_fixed_tasks():
    scheduler = Scheduler(day_start="08:00", available_minutes=600)
    # Fixed appointments at 08:00-08:30 and 10:00-10:30 leave a wide gap after 08:30.
    plan = scheduler.build_plan(
        [
            Task("Walk", duration_minutes=30, priority="high", time="08:00"),
            Task("Vet", duration_minutes=30, priority="high", time="10:00"),
        ]
    )
    # A 30-minute task fits starting at 08:30, right after the first appointment.
    assert scheduler.find_next_slot(plan, 30) == "08:30"


def test_next_slot_returns_none_when_day_is_full():
    scheduler = Scheduler(day_start="08:00", available_minutes=30)
    plan = scheduler.build_plan([Task("Walk", duration_minutes=30, priority="high", time="08:00")])
    assert scheduler.find_next_slot(plan, 30) is None


# --- Edge case: no tasks ----------------------------------------------------
def test_plan_for_owner_with_no_tasks_is_empty():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "cat"))
    assert Scheduler().plan_for_owner(owner) == []
