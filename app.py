import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A smart pet-care planner: add pets, add tasks, and generate a prioritized daily schedule.")

# --- Application memory -----------------------------------------------------
# Streamlit reruns top-to-bottom on every interaction, so we keep the Owner
# (with its pets and tasks) in session_state instead of rebuilding it.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
owner: Owner = st.session_state.owner

# --- Owner + preferences ----------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
col_a, col_b = st.columns(2)
with col_a:
    owner.wake_time = st.text_input("Day starts at (HH:MM)", value=owner.wake_time)
with col_b:
    owner.available_minutes = st.number_input(
        "Available minutes today", min_value=15, max_value=1440,
        value=owner.available_minutes, step=15,
    )

st.divider()

# --- Add a pet --------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    c1, c2, c3 = st.columns(3)
    with c1:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with c2:
        breed = st.text_input("Breed", value="")
    with c3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet") and pet_name.strip():
        owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed, age=int(age)))
        st.success(f"Added {pet_name.strip()}.")

if not owner.pets:
    st.info("No pets yet. Add one above.")

# --- Add a task to a pet ----------------------------------------------------
if owner.pets:
    st.subheader("Add a task")
    with st.form("add_task", clear_on_submit=True):
        target = st.selectbox("For pet", [p.name for p in owner.pets])
        title = st.text_input("Task title", value="Morning walk")
        t1, t2, t3 = st.columns(3)
        with t1:
            category = st.selectbox(
                "Category",
                ["walk", "feeding", "meds", "appointment", "enrichment", "grooming", "general"],
            )
        with t2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with t3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        f1, f2 = st.columns(2)
        with f1:
            recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
        with f2:
            time_of_day = st.text_input("Time (HH:MM, optional)", value="")
        if st.form_submit_button("Add task") and title.strip():
            pet = owner.get_pet(target)
            if pet is not None:
                pet.add_task(
                    Task(
                        title=title.strip(),
                        category=category,
                        duration_minutes=int(duration),
                        priority=priority,
                        recurrence=recurrence,
                        time=time_of_day.strip() or None,
                    )
                )
                st.success(f"Added '{title.strip()}' for {target}.")

# --- Current pets & tasks (with mark-complete) ------------------------------
for pet in owner.pets:
    with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if not pet.tasks:
            st.caption("No tasks for this pet yet.")
        # Iterate a snapshot: complete_task() may append a new occurrence.
        for i, task in enumerate(list(pet.tasks)):
            r1, r2, r3, r4 = st.columns([3, 2, 2, 2])
            r1.write(f"**{task.title}**  \n_{task.category}_")
            r2.write(task.time or "—")
            r3.write(task.priority)
            if task.done:
                r4.write("✓ done")
            elif r4.button("Mark done", key=f"done_{pet.name}_{i}"):
                pet.complete_task(task)  # spawns next occurrence if recurring
                st.rerun()

st.divider()

# --- Generate schedule ------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(day_start=owner.wake_time, available_minutes=owner.available_minutes)
    tasks = owner.all_tasks()
    plan = scheduler.build_plan(tasks)

    conflicts = scheduler.find_time_conflicts(tasks)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No time conflicts detected.")

    if not plan:
        st.info("No tasks to schedule. Add some tasks first.")
    else:
        st.success(f"Planned {len(plan)} task(s) for {owner.name}.")
        st.table(
            [
                {
                    "Start": e["start"],
                    "End": e["end"],
                    "Task": e["task"].title,
                    "Priority": e["task"].priority,
                }
                for e in plan
            ]
        )
        with st.expander("Why this plan?"):
            st.text(scheduler.explain(plan))

st.divider()

# --- Find the next free slot for a flexible task ----------------------------
st.subheader("Find a free slot")
st.caption("Where could a new, flexible task fit around today's fixed appointments?")
slot_duration = st.number_input(
    "New task duration (min)", min_value=1, max_value=240, value=45, step=5
)
if st.button("Find next free slot"):
    scheduler = Scheduler(day_start=owner.wake_time, available_minutes=owner.available_minutes)
    plan = scheduler.build_plan(owner.all_tasks())
    slot = scheduler.find_next_slot(plan, int(slot_duration))
    if slot:
        st.success(f"Earliest opening for a {int(slot_duration)}-min task: **{slot}**")
    else:
        st.warning("No free slot that long remains in today's available time.")
