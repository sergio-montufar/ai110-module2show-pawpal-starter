from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task(title="Walk", description="Walk the dog", duration_minutes=30, priority="high", category="exercise")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    owner = Owner(name="Sergio", available_minutes=60)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feed", description="Morning meal", duration_minutes=10, priority="high", category="health"))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Walk", description="Evening walk", duration_minutes=30, priority="medium", category="exercise"))
    assert len(pet.tasks) == 2


# ---------- Sorting Correctness ----------

def test_schedule_sorted_by_time():
    """Tasks with different scheduled_times are returned in chronological order."""
    owner = Owner(name="Sergio", available_minutes=120)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    owner.add_pet(pet)

    # Add tasks in reverse chronological order
    pet.add_task(Task(title="Evening walk", description="Walk", duration_minutes=30,
                      priority="high", category="exercise", scheduled_time="17:00"))
    pet.add_task(Task(title="Morning feed", description="Feed", duration_minutes=10,
                      priority="medium", category="health", scheduled_time="07:00"))
    pet.add_task(Task(title="Midday play", description="Play", duration_minutes=20,
                      priority="low", category="exercise", scheduled_time="12:00"))

    scheduler = Scheduler(owner)
    entries = scheduler.generate_schedule()

    times = [e.start_time for e in entries]
    assert times == sorted(times), f"Schedule not in chronological order: {times}"


def test_schedule_tiebreak_by_score():
    """When two tasks share the same scheduled_time, higher-score task comes first."""
    owner = Owner(name="Sergio", available_minutes=120, preferences=["health"])
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    owner.add_pet(pet)

    pet.add_task(Task(title="Low priority walk", description="Walk", duration_minutes=20,
                      priority="low", category="exercise", scheduled_time="08:00"))
    pet.add_task(Task(title="High priority meds", description="Meds", duration_minutes=10,
                      priority="high", category="health", scheduled_time="08:00"))

    scheduler = Scheduler(owner)
    entries = scheduler.generate_schedule()

    # "High priority meds" has priority=high (3) + preference bonus (2) = 5
    # "Low priority walk" has priority=low (1) + no bonus = 1
    assert entries[0].task.title == "High priority meds"
    assert entries[1].task.title == "Low priority walk"


# ---------- Recurrence Logic ----------

def test_daily_recurrence_creates_next_day_task():
    """Marking a daily task complete creates a new task scheduled for the next day."""
    owner = Owner(name="Sergio", available_minutes=60)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    owner.add_pet(pet)

    today = date(2026, 4, 1)
    task = Task(title="Morning walk", description="Walk", duration_minutes=30,
                priority="high", category="exercise", frequency="daily",
                scheduled_time="08:00", scheduled_date=today)
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.scheduled_date == today + timedelta(days=1)
    assert next_task.completed is False
    # The new task should have been added to the same pet
    assert next_task in pet.tasks


def test_onetime_task_returns_none():
    """A one-time task returns None on completion and creates no follow-up."""
    owner = Owner(name="Sergio", available_minutes=60)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)

    task = Task(title="Vet visit", description="Annual checkup", duration_minutes=60,
                priority="high", category="health", frequency="once")
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is None
    assert len(pet.tasks) == 1  # no new task added


# ---------- Conflict Detection ----------

def test_detect_conflicts_overlapping_tasks():
    """Two tasks that overlap in time produce a conflict warning."""
    owner = Owner(name="Sergio", available_minutes=120)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    owner.add_pet(pet)

    # Task A: 08:00 – 08:30
    pet.add_task(Task(title="Walk", description="Walk", duration_minutes=30,
                      priority="high", category="exercise", scheduled_time="08:00"))
    # Task B: 08:15 – 08:45  (overlaps with A)
    pet.add_task(Task(title="Feed", description="Feed", duration_minutes=30,
                      priority="high", category="health", scheduled_time="08:15"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feed" in warnings[0]


def test_no_conflict_for_adjacent_tasks():
    """Tasks that are back-to-back (no overlap) should not be flagged."""
    owner = Owner(name="Sergio", available_minutes=120)
    pet = Pet(name="Bella", species="dog", age=3, owner=owner)
    owner.add_pet(pet)

    # Task A: 08:00 – 08:30
    pet.add_task(Task(title="Walk", description="Walk", duration_minutes=30,
                      priority="high", category="exercise", scheduled_time="08:00"))
    # Task B: 08:30 – 09:00  (starts exactly when A ends)
    pet.add_task(Task(title="Feed", description="Feed", duration_minutes=30,
                      priority="high", category="health", scheduled_time="08:30"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 0
