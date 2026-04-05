import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Session state — initialize once, persist across reruns
# ---------------------------------------------------------------------------
# st.session_state works like a dictionary that survives page refreshes.
# The "not in" check means we only create these objects the first time;
# on every subsequent rerun Streamlit reuses the existing instances.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=60)

if "pet" not in st.session_state:
    st.session_state.pet = Pet(name="Mochi", species="dog", age=3)
    st.session_state.owner.add_pet(st.session_state.pet)

# ---------------------------------------------------------------------------
# Owner info
# ---------------------------------------------------------------------------
st.subheader("Owner Info")

owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
available = st.number_input("Available time (minutes)", min_value=10, max_value=480,
                            value=st.session_state.owner.available_minutes)

if st.button("Save owner"):
    # Directly update the persisted Owner object's attributes
    st.session_state.owner.name = owner_name
    st.session_state.owner.available_minutes = available
    st.success(f"Saved! {owner_name} has {available} minutes available today.")

st.divider()

# ---------------------------------------------------------------------------
# Add a new pet — wired to owner.add_pet()
# ---------------------------------------------------------------------------
st.subheader("Add / Switch Pet")
st.caption("Creates a new Pet and registers it with the owner via `owner.add_pet()`.")

col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
with col_b2:
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
with col_b3:
    new_age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add / switch pet"):
    # owner.add_pet() is the single method responsible for linking a Pet to an Owner
    new_pet = Pet(name=new_pet_name, species=new_species, age=int(new_age))
    st.session_state.owner.add_pet(new_pet)   # <-- wired to Owner.add_pet()
    st.session_state.pet = new_pet
    st.success(f"Pet '{new_pet_name}' added and set as the active pet.")

# Show which pet is currently active
active = st.session_state.pet
st.info(f"Active pet: **{active.name}** ({active.species}, age {active.age})")

st.divider()

# ---------------------------------------------------------------------------
# Tasks — add tasks, display sorted via Scheduler.rank_tasks()
# ---------------------------------------------------------------------------
st.subheader("Tasks")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    start_time = st.number_input("Start time (min from midnight)", min_value=0,
                                 max_value=1439, value=480,
                                 help="e.g. 480 = 8:00 am, 720 = 12:00 pm")

if st.button("Add task"):
    new_task = Task(
        title=task_title,
        duration_minutes=int(duration),
        priority=priority,
        category="general",
        start_time=int(start_time),
    )
    st.session_state.pet.get_tasks().append(new_task)
    st.success(f"Task '{task_title}' added to {st.session_state.pet.name}.")

current_tasks = st.session_state.pet.get_tasks()

if current_tasks:
    # Use Scheduler.rank_tasks() to display tasks sorted by priority
    scheduler = Scheduler(st.session_state.owner, st.session_state.pet)
    ranked = scheduler.rank_tasks()

    st.write(f"Tasks for **{st.session_state.pet.name}** (sorted by priority):")
    st.table([
        {
            "Title": t.title,
            "Duration (min)": t.duration_minutes,
            "Priority": t.priority,
            "Start time": f"{t.start_time // 60:02d}:{t.start_time % 60:02d}" if t.start_time is not None else "—",
        }
        for t in ranked
    ])

    # Use Scheduler.has_conflicts() to surface time overlap warnings
    conflicts = scheduler.has_conflicts()
    if conflicts:
        for a, b in conflicts:
            st.warning(
                f"Conflict: **{a.title}** and **{b.title}** overlap in time. "
                f"Consider adjusting their start times."
            )
    else:
        st.success("No scheduling conflicts detected.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule generation — wired to owner.get_schedule()
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    schedule = st.session_state.owner.get_schedule()

    if schedule.scheduled_tasks:
        st.success(f"Scheduled {len(schedule.scheduled_tasks)} task(s) — "
                   f"{schedule.total_minutes} min of {st.session_state.owner.available_minutes} min used.")
        st.table([
            {
                "Title": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
            }
            for t in schedule.scheduled_tasks
        ])
    else:
        st.warning("No tasks could be scheduled. Try adding tasks or increasing available time.")

    if schedule.skipped_tasks:
        with st.expander(f"Skipped tasks ({len(schedule.skipped_tasks)})"):
            st.table([
                {
                    "Title": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": t.priority,
                }
                for t in schedule.skipped_tasks
            ])
            st.caption("These tasks were skipped because they didn't fit within the available time.")
