import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

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

# --- Current pets & tasks ---------------------------------------------------
for pet in owner.pets:
    with st.expander(f"{pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if pet.tasks:
            st.table(
                [
                    {
                        "Task": t.title,
                        "Category": t.category,
                        "Duration (min)": t.duration_minutes,
                        "Priority": t.priority,
                        "Time": t.time or "—",
                        "Done": "✓" if t.done else "",
                    }
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("No tasks for this pet yet.")

st.divider()

# --- Generate schedule ------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    scheduler = Scheduler(day_start=owner.wake_time, available_minutes=owner.available_minutes)
    plan = scheduler.plan_for_owner(owner)
    if not plan:
        st.warning("No tasks to schedule. Add some tasks first.")
    else:
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
        st.text(scheduler.explain(plan))
        conflicts = scheduler.detect_conflicts(plan)
        for c in conflicts:
            st.warning(
                f"⚠ {c['first']} overlaps {c['second']} by {c['overlap_minutes']} min"
            )
