from dataclasses import dataclass, field

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """Represents a single pet care activity with a duration and priority level."""

    title: str
    duration_minutes: int
    priority: str          # "low", "medium", "high"
    category: str          # "walk", "feeding", "meds", "grooming", "enrichment"
    completed: bool = False
    recur: bool = False    # True = repeats daily
    start_time: int | None = None  # minutes from midnight, e.g. 480 = 8:00 am

    def is_high_priority(self) -> bool:
        """Return True if the task's priority is high."""
        return self.priority == "high"

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> "Task":
        """Return a fresh copy of this task for the next day (completed reset to False)."""
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            completed=False,
            recur=self.recur,
            start_time=self.start_time,
        )


@dataclass
class Pet:
    """Represents a pet and the care tasks assigned to it."""

    name: str
    species: str           # "dog", "cat", "other"
    age: int
    tasks: list[Task] = field(default_factory=list)

    def get_tasks(self) -> list[Task]:
        """Return the list of tasks assigned to this pet."""
        return self.tasks


@dataclass
class Owner:
    """Represents the pet owner, their available time, and their pet."""

    name: str
    available_minutes: int
    preferences: dict = field(default_factory=dict)
    pet: "Pet | None" = None

    def add_pet(self, pet: Pet) -> None:
        """Assign a pet to this owner."""
        self.pet = pet

    def get_schedule(self) -> "DailySchedule":
        """Build and return a daily schedule for the owner's current pet."""
        if self.pet is None:
            return DailySchedule()
        scheduler = Scheduler(self, self.pet)
        return scheduler.build_schedule()


@dataclass
class DailySchedule:
    """Holds the result of a scheduling run, including scheduled and skipped tasks."""

    scheduled_tasks: list[Task] = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        """Return a Markdown-formatted explanation of the schedule and why tasks were included or skipped."""
        lines = []

        if not self.scheduled_tasks:
            return "No tasks were scheduled."

        lines.append("## Scheduled Tasks\n")
        for task in self.scheduled_tasks:
            lines.append(
                f"- **{task.title}** ({task.duration_minutes} min) "
                f"[{task.priority} priority] — included because it fits within available time."
            )

        if self.skipped_tasks:
            lines.append("\n## Skipped Tasks\n")
            for task in self.skipped_tasks:
                lines.append(
                    f"- **{task.title}** ({task.duration_minutes} min) "
                    f"[{task.priority} priority] — skipped due to time constraints."
                )

        lines.append(f"\n**Total scheduled time:** {self.total_minutes} minutes.")
        return "\n".join(lines)

    def display(self) -> None:
        """Print the schedule explanation to the terminal."""
        print(self.explain())


class Scheduler:
    """Builds a daily care schedule by ranking tasks and fitting them within available time."""

    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = pet.get_tasks()

    def rank_tasks(self) -> list[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(self.tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 99))

    def fits_within_time(self, tasks: list[Task], available: int) -> bool:
        """Return True if the total duration of the given tasks fits within available minutes."""
        return sum(t.duration_minutes for t in tasks) <= available

    def has_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose start_time values overlap."""
        timed = [t for t in self.tasks if t.start_time is not None]
        conflicts = []
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_end = a.start_time + a.duration_minutes
                b_end = b.start_time + b.duration_minutes
                if a.start_time < b_end and b.start_time < a_end:
                    conflicts.append((a, b))
        return conflicts

    def build_schedule(self) -> DailySchedule:
        """Greedily select tasks by priority until available time is exhausted."""
        ranked = self.rank_tasks()
        scheduled = []
        skipped = []
        time_used = 0

        for task in ranked:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                scheduled.append(task)
                time_used += task.duration_minutes
            else:
                skipped.append(task)

        return DailySchedule(
            scheduled_tasks=scheduled,
            skipped_tasks=skipped,
            total_minutes=time_used,
        )
