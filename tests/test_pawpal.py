from pawpal_system import Owner, Pet, Task


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
