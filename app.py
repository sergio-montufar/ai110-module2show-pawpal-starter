import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("A pet care planning assistant that helps schedule daily tasks for your pets.")

# --- Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_minutes=90)

st.divider()

# --- Owner Settings ---
st.subheader("Owner Settings")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
available_minutes = st.number_input(
    "Available minutes", min_value=1, max_value=480,
    value=st.session_state.owner.available_minutes,
)
st.session_state.owner.name = owner_name
st.session_state.owner.set_availability(available_minutes)

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=2)

if st.button("Add pet"):
    pet = Pet(name=pet_name, species=species, age=pet_age, owner=st.session_state.owner)
    st.session_state.owner.add_pet(pet)
    st.success(f"Added {pet_name} the {species}!")

if st.session_state.owner.pets:
    st.write("**Current pets:**")
    for pet in st.session_state.owner.pets:
        st.write(f"- {pet.get_summary()}")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a Task to a Pet ---
st.subheader("Add a Task")

if st.session_state.owner.pets:
    pet_names = [p.name for p in st.session_state.owner.pets]
    selected_pet_name = st.selectbox("Assign to pet", pet_names)

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    task_description = st.text_input("Description", value="")
    task_category = st.selectbox("Category", ["exercise", "health", "grooming", "feeding", "play"])
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
    task_time = st.text_input("Scheduled time (HH:MM)", value="", placeholder="e.g. 08:30")

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task = Task(
            title=task_title,
            description=task_description,
            duration_minutes=int(duration),
            priority=priority,
            category=task_category,
            frequency=task_frequency,
            scheduled_time=task_time if task_time else None,
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        for task in all_tasks:
            status = "done" if task.completed else "pending"
            pet_name = task.pet.name if task.pet else "unassigned"
            st.write(f"- **{task.title}** ({pet_name}) — {task.duration_minutes}min, "
                     f"{task.priority} priority, {status}")
else:
    st.info("Add a pet first before creating tasks.")

st.divider()

# --- Owner Preferences ---
st.subheader("Owner Preferences")
preference_options = ["exercise", "health", "grooming", "feeding", "play"]
selected_prefs = st.multiselect(
    "Preferred categories (boosted in scheduling)",
    preference_options,
    default=st.session_state.owner.preferences,
)
st.session_state.owner.update_preferences(selected_prefs)

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)

    # --- Conflict warnings ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            st.warning(warning)

    # --- Schedule table ---
    schedule = scheduler.generate_schedule()
    if schedule:
        st.success(f"Scheduled {len(schedule)} tasks within "
                   f"{st.session_state.owner.available_minutes} minutes.")

        table_data = []
        for entry in schedule:
            hours, mins = divmod(entry.start_time, 60)
            pet_name = entry.task.pet.name if entry.task.pet else "—"
            table_data.append({
                "Time": f"{hours:02d}:{mins:02d}",
                "Task": entry.task.title,
                "Pet": pet_name,
                "Duration": f"{entry.task.duration_minutes} min",
                "Priority": entry.task.priority.capitalize(),
                "Category": entry.task.category.capitalize(),
            })
        st.table(table_data)

        # --- Reasoning expander ---
        with st.expander("Why this order?"):
            for entry in schedule:
                st.write(f"**{entry.task.title}** — {entry.reasoning}")

        # --- Summary metrics ---
        used = sum(e.task.duration_minutes for e in schedule)
        remaining = st.session_state.owner.available_minutes - used
        col_used, col_remaining, col_tasks = st.columns(3)
        col_used.metric("Minutes used", used)
        col_remaining.metric("Minutes remaining", remaining)
        col_tasks.metric("Tasks scheduled", len(schedule))

        # --- Skipped tasks ---
        all_incomplete = [t for t in st.session_state.owner.get_all_tasks() if not t.completed]
        scheduled_tasks = {e.task for e in schedule}
        skipped = [t for t in all_incomplete if t not in scheduled_tasks]
        if skipped:
            st.warning(f"{len(skipped)} task(s) skipped (not enough time): "
                       + ", ".join(t.title for t in skipped))
    else:
        st.info("No tasks to schedule. Add pets and tasks first.")

st.divider()

# --- Mark Tasks Complete ---
st.subheader("Mark Tasks Complete")

incomplete_tasks = [t for t in st.session_state.owner.get_all_tasks() if not t.completed]
if incomplete_tasks:
    task_titles = [f"{t.title} ({t.pet.name})" if t.pet else t.title for t in incomplete_tasks]
    selected_title = st.selectbox("Select a task to complete", task_titles)

    if st.button("Mark complete"):
        idx = task_titles.index(selected_title)
        task = incomplete_tasks[idx]
        next_task = task.mark_complete()
        st.success(f"Marked '{task.title}' as complete!")
        if next_task:
            st.info(f"Recurring task: next '{next_task.title}' scheduled for {next_task.scheduled_date}.")
else:
    st.info("No incomplete tasks to mark.")
