from pawpal_system import Task, Pet


def test_mark_complete_changes_task_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high", category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.tasks.append(Task(title="Feeding", duration_minutes=10, priority="high", category="feeding"))
    assert len(pet.tasks) == 1
