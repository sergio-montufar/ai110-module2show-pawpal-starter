from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner
owner = Owner(name="Sergio", available_minutes=90, preferences=["health", "exercise"])

# Create two pets
bella = Pet(name="Bella", species="dog", age=3, owner=owner)
milo = Pet(name="Milo", species="cat", age=5, owner=owner)

owner.add_pet(bella)
owner.add_pet(milo)

# Add tasks to pets
bella.add_task(Task(
    title="Morning Walk",
    description="Walk Bella around the park",
    duration_minutes=30,
    priority="high",
    category="exercise",
))

bella.add_task(Task(
    title="Vet Checkup",
    description="Annual vaccination appointment",
    duration_minutes=45,
    priority="high",
    category="health",
))

milo.add_task(Task(
    title="Grooming",
    description="Brush Milo's fur and trim nails",
    duration_minutes=20,
    priority="medium",
    category="grooming",
))

# Generate and print the schedule
scheduler = Scheduler(owner)
scheduler.generate_schedule()

print("=" * 50)
print("        🐾 Today's Schedule 🐾")
print("=" * 50)
print(scheduler.explain_schedule())
print("=" * 50)
