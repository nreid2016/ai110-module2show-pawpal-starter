from datetime import date, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, format_schedule

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Plan consistent care for every pet in your household.")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", daily_minutes=120)
if "owner" not in st.session_state or not st.session_state.owner.pets:
    st.session_state.owner.add_pet(Pet("Mochi", "dog"))

owner: Owner = st.session_state.owner

with st.sidebar:
    st.header("Owner settings")
    owner.name = st.text_input("Owner name", owner.name)
    owner.daily_minutes = st.slider("Available care minutes", 15, 360, owner.daily_minutes, 5)
    plan_day = st.date_input("Schedule date", date.today())

st.subheader("Pets")
with st.form("pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name.strip() and not any(pet.name == pet_name.strip() for pet in owner.pets):
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.error("Enter a unique pet name.")

st.subheader("Add a care task")
with st.form("task_form"):
    pet_options = [pet.name for pet in owner.pets]
    selected_pet = st.selectbox("Pet", pet_options)
    description = st.text_input("Task description", placeholder="Evening walk")
    col1, col2, col3 = st.columns(3)
    with col1:
        task_time = st.time_input("Time", time(9, 0))
    with col2:
        duration = st.number_input("Minutes", 1, 240, 20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    col4, col5 = st.columns(2)
    with col4:
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
    with col5:
        category = st.selectbox("Category", ["exercise", "feeding", "medication", "grooming", "enrichment", "general"])
    if st.form_submit_button("Add task"):
        if description.strip():
            owner.get_pet(selected_pet).add_task(
                Task(description.strip(), task_time, frequency, int(duration), priority, due_date=plan_day, category=category)
            )
            st.success(f"Added {description.strip()} for {selected_pet}.")
        else:
            st.error("Enter a task description.")

st.subheader("Current tasks")
for pet in owner.pets:
    with st.expander(f"{pet.name} · {pet.species} · {pet.task_count()} task(s)", expanded=True):
        if not pet.tasks:
            st.info("No tasks yet.")
        for task in pet.tasks:
            status = "complete" if task.completed else "pending"
            st.write(f"{task.time:%I:%M %p} — **{task.description}** · {task.frequency} · {task.priority} · {status}")
            if not task.completed and st.button(f"Mark complete: {task.description}", key=f"complete-{pet.name}-{task.description}-{task.due_date}"):
                Scheduler(owner).mark_task_complete(pet.name, task.description, plan_day)
                st.rerun()

st.divider()
st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary", use_container_width=True):
    scheduler = Scheduler(owner)
    entries, warnings = scheduler.build_plan(plan_day)
    st.session_state.entries = entries
    st.session_state.warnings = warnings

if "entries" in st.session_state:
    entries = st.session_state.entries
    st.code(format_schedule(entries, plan_day), language="text")
    for warning in st.session_state.warnings:
        st.warning(warning)
    if not st.session_state.warnings:
        st.success("No scheduling conflicts detected.")
else:
    st.info("Add pets and tasks, then generate a schedule.")
