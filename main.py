from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# Create an owner
owner = Owner(name="Sergio", available_minutes=120, preferences=["health", "exercise"])

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
    frequency="daily",
    scheduled_time="07:00",
    scheduled_date=date.today(),
))

bella.add_task(Task(
    title="Vet Checkup",
    description="Annual vaccination appointment",
    duration_minutes=45,
    priority="high",
    category="health",
    frequency="once",
    scheduled_time="14:30",
    scheduled_date=date.today(),
))

milo.add_task(Task(
    title="Grooming",
    description="Brush Milo's fur and trim nails",
    duration_minutes=20,
    priority="medium",
    category="grooming",
    frequency="weekly",
    scheduled_time="10:00",
    scheduled_date=date.today(),
))

# Add conflicting tasks to test conflict detection
bella.add_task(Task(
    title="Fetch Training",
    description="Practice fetch at the park",
    duration_minutes=30,
    priority="medium",
    category="exercise",
    scheduled_time="07:15",
    scheduled_date=date.today(),
))

milo.add_task(Task(
    title="Nail Trim",
    description="Quick nail trim for Milo",
    duration_minutes=15,
    priority="low",
    category="grooming",
    scheduled_time="07:20",
    scheduled_date=date.today(),
))

# Generate and print the schedule
scheduler = Scheduler(owner)
scheduler.generate_schedule()

# --- Conflict Detection ---
conflicts = scheduler.detect_conflicts()
if conflicts:
    print("=" * 50)
    print("     🐾 Schedule Conflict Warnings 🐾")
    print("=" * 50)
    for warning in conflicts:
        print(warning)
    print("=" * 50)

print("=" * 50)
print("        🐾 Today's Schedule 🐾")
print("=" * 50)
print(scheduler.explain_schedule())
print("=" * 50)

# --- Demo: mark a recurring task complete and see next occurrence ---
print("\n✅ Completing 'Morning Walk' (daily)...")
next_task = scheduler.mark_task_complete("Morning Walk")
if next_task:
    print(f"   ↪ Next occurrence created: {next_task.title} on {next_task.scheduled_date}")

print("✅ Completing 'Grooming' (weekly)...")
next_task = scheduler.mark_task_complete("Grooming")
if next_task:
    print(f"   ↪ Next occurrence created: {next_task.title} on {next_task.scheduled_date}")

print("✅ Completing 'Vet Checkup' (once)...")
next_task = scheduler.mark_task_complete("Vet Checkup")
if next_task:
    print(f"   ↪ Next occurrence created: {next_task.title} on {next_task.scheduled_date}")
else:
    print("   ↪ One-time task — no next occurrence")

# Regenerate to show the new pending tasks
print("\n" + "=" * 50)
print("     🐾 Tomorrow's Pending Tasks 🐾")
print("=" * 50)
scheduler.generate_schedule()
print(scheduler.explain_schedule())
print("=" * 50)
