from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Sorting correctness — tasks come back high → medium → low
# ---------------------------------------------------------------------------

def test_rank_tasks_returns_high_before_medium_before_low():
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.tasks = [
        Task(title="Grooming",  duration_minutes=15, priority="low",    category="grooming"),
        Task(title="Play",      duration_minutes=20, priority="medium", category="enrichment"),
        Task(title="Meds",      duration_minutes=5,  priority="high",   category="meds"),
    ]
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    ranked = scheduler.rank_tasks()

    assert ranked[0].priority == "high"
    assert ranked[1].priority == "medium"
    assert ranked[2].priority == "low"


def test_rank_tasks_stable_within_same_priority():
    """Tasks with identical priority should preserve their original relative order."""
    pet = Pet(name="Luna", species="cat", age=2)
    pet.tasks = [
        Task(title="First",  duration_minutes=10, priority="medium", category="feeding"),
        Task(title="Second", duration_minutes=10, priority="medium", category="enrichment"),
    ]
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    ranked = scheduler.rank_tasks()

    assert ranked[0].title == "First"
    assert ranked[1].title == "Second"


# ---------------------------------------------------------------------------
# Recurrence logic — next_occurrence() creates a fresh task for tomorrow
# ---------------------------------------------------------------------------

def test_next_occurrence_resets_completed_flag():
    """Calling next_occurrence on a completed recurring task returns an incomplete copy."""
    task = Task(title="Evening walk", duration_minutes=20, priority="high",
                category="walk", recur=True)
    task.mark_complete()
    assert task.completed is True

    tomorrow = task.next_occurrence()

    assert tomorrow.completed is False


def test_next_occurrence_preserves_task_attributes():
    """next_occurrence keeps the same title, duration, priority, and category."""
    task = Task(title="Feeding", duration_minutes=10, priority="high",
                category="feeding", recur=True)
    task.mark_complete()

    tomorrow = task.next_occurrence()

    assert tomorrow.title == task.title
    assert tomorrow.duration_minutes == task.duration_minutes
    assert tomorrow.priority == task.priority
    assert tomorrow.category == task.category
    assert tomorrow.recur is True


def test_next_occurrence_is_independent_of_original():
    """Modifying the new task must not affect the original."""
    task = Task(title="Walk", duration_minutes=30, priority="high", category="walk", recur=True)
    tomorrow = task.next_occurrence()
    tomorrow.mark_complete()

    assert task.completed is False


# ---------------------------------------------------------------------------
# Conflict detection — overlapping start_times are flagged
# ---------------------------------------------------------------------------

def test_no_conflicts_when_tasks_do_not_overlap():
    """Tasks scheduled back-to-back should produce no conflicts."""
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.tasks = [
        Task(title="Walk",    duration_minutes=30, priority="high", category="walk",    start_time=480),
        Task(title="Feeding", duration_minutes=10, priority="high", category="feeding", start_time=510),
    ]
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    assert scheduler.has_conflicts() == []


def test_conflict_detected_when_tasks_overlap():
    """Two tasks whose time windows overlap should be returned as a conflict pair."""
    pet = Pet(name="Mochi", species="dog", age=3)
    walk    = Task(title="Walk",    duration_minutes=30, priority="high",   category="walk",    start_time=480)
    feeding = Task(title="Feeding", duration_minutes=10, priority="medium", category="feeding", start_time=490)
    pet.tasks = [walk, feeding]

    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    conflicts = scheduler.has_conflicts()

    assert len(conflicts) == 1
    assert (walk, feeding) in conflicts


def test_tasks_without_start_time_are_ignored_in_conflict_check():
    """Tasks with no start_time set should never appear in conflict results."""
    pet = Pet(name="Luna", species="cat", age=2)
    pet.tasks = [
        Task(title="Play",    duration_minutes=20, priority="medium", category="enrichment"),  # no start_time
        Task(title="Feeding", duration_minutes=10, priority="high",   category="feeding"),     # no start_time
    ]
    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner, pet)

    assert scheduler.has_conflicts() == []
