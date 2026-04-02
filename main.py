from pawpal_system import Owner, Pet, Task

# --- Create owner ---
jordan = Owner(name="Jordan", available_minutes=90)

# --- Create pets ---
mochi = Pet(name="Mochi", species="dog", age=3)
luna = Pet(name="Luna", species="cat", age=5)

# --- Add tasks to Mochi ---
mochi.tasks = [
    Task(title="Morning walk",       duration_minutes=30, priority="high",   category="walk"),
    Task(title="Breakfast feeding",  duration_minutes=10, priority="high",   category="feeding"),
    Task(title="Flea medication",    duration_minutes=5,  priority="high",   category="meds"),
    Task(title="Fetch/play session", duration_minutes=20, priority="medium", category="enrichment"),
    Task(title="Brush coat",         duration_minutes=15, priority="low",    category="grooming"),
]

# --- Add tasks to Luna ---
luna.tasks = [
    Task(title="Breakfast feeding",  duration_minutes=5,  priority="high",   category="feeding"),
    Task(title="Litter box cleaning",duration_minutes=10, priority="medium", category="grooming"),
    Task(title="Interactive play",   duration_minutes=15, priority="medium", category="enrichment"),
]

# --- Run schedules ---
for pet in [mochi, luna]:
    jordan.add_pet(pet)
    schedule = jordan.get_schedule()

    print(f"\n{'='*40}")
    print(f"  Today's Schedule for {pet.name}")
    print(f"{'='*40}")
    print(schedule.explain())
