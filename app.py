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

    if st.button("Add task"):
        selected_pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet_name)
        task = Task(
            title=task_title,
            description=task_description,
            duration_minutes=int(duration),
            priority=priority,
            category=task_category,
        )
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    all_tasks = st.session_state.owner.get_all_tasks()
    if all_tasks:
        st.write("**Current tasks:**")
        for task in all_tasks:
            st.write(f"- {task}")
else:
    st.info("Add a pet first before creating tasks.")

st.divider()

# --- Generate Schedule ---
st.subheader("Generate Schedule")

if st.button("Generate schedule"):
    scheduler = Scheduler(st.session_state.owner)
    schedule = scheduler.generate_schedule()
    if schedule:
        st.text(scheduler.explain_schedule())
    else:
        st.warning("No tasks to schedule. Add pets and tasks first.")
