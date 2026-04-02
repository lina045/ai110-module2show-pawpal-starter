from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str          # "low", "medium", "high"
    category: str          # "walk", "feeding", "meds", "grooming", "enrichment"
    completed: bool = False

    def is_high_priority(self) -> bool:
        pass


@dataclass
class Pet:
    name: str
    species: str           # "dog", "cat", "other"
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pet: "Pet | None" = None

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_schedule(self) -> "DailySchedule":
        pass


@dataclass
class DailySchedule:
    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        pass

    def display(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def build_schedule(self) -> DailySchedule:
        pass

    def fits_within_time(self, tasks: list[Task], available: int) -> bool:
        pass

    def rank_tasks(self) -> list[Task]:
        pass
