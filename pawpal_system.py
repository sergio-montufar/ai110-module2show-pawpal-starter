from dataclasses import dataclass, field
from datetime import date, timedelta

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list["Pet"] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's preference list with a new one."""
        self.preferences = preferences

    def set_availability(self, minutes: int) -> None:
        """Set the number of minutes the owner has available today."""
        self.available_minutes = minutes

    def add_pet(self, pet: "Pet") -> None:
        """Add a pet to the owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list["Task"]:
        """Return a combined list of tasks from all the owner's pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Owner
    tasks: list["Task"] = field(default_factory=list)

    def get_summary(self) -> str:
        """Return a short description of the pet."""
        return f"{self.name} is a {self.age}-year-old {self.species} owned by {self.owner.name}."

    def add_task(self, task: "Task") -> None:
        """Assign a task to this pet and add it to the task list."""
        task.pet = self
        self.tasks.append(task)


@dataclass
class Task:
    title: str
    description: str
    duration_minutes: int
    priority: str
    category: str
    frequency: str = "daily"
    scheduled_time: str | None = None  # "HH:MM" format, e.g. "08:30"
    scheduled_date: date | None = None
    completed: bool = False
    pet: "Pet | None" = None

    FREQUENCY_DELTAS: dict[str, timedelta] = field(
        default_factory=lambda: {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
        },
        repr=False,
    )

    def priority_score(self) -> int:
        """Return a numeric score (1-3) based on the task's priority level."""
        scores = {"low": 1, "medium": 2, "high": 3}
        return scores.get(self.priority, 0)

    def schedule_score(self, preferences: list[str]) -> int:
        """Return a scheduling score that factors in priority and owner preferences.

        Combines the base priority score (1-3) with a +2 bonus when the task's
        category appears in the owner's preference list. Higher scores cause a
        task to be scheduled earlier when times are equal.

        Args:
            preferences: List of category strings the owner cares about most.

        Returns:
            An integer score used as a secondary sort key in generate_schedule().
        """
        s = self.priority_score()
        if self.category in preferences:
            s += 2
        return s

    def mark_complete(self) -> "Task | None":
        """Mark this task as completed. If it's recurring, create and return the next occurrence.

        Uses timedelta from FREQUENCY_DELTAS to compute the next scheduled_date.
        For "daily" tasks the next date is +1 day; for "weekly" tasks it is +7 days.
        One-time tasks (frequency not in FREQUENCY_DELTAS) return None.

        The new Task is automatically added to the same pet's task list if one
        is assigned.

        Returns:
            The newly created next-occurrence Task, or None for one-time tasks.
        """
        self.completed = True
        delta = self.FREQUENCY_DELTAS.get(self.frequency)
        if delta is None:
            return None

        current_date = self.scheduled_date if self.scheduled_date else date.today()
        next_date = current_date + delta

        next_task = Task(
            title=self.title,
            description=self.description,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            scheduled_time=self.scheduled_time,
            scheduled_date=next_date,
        )

        if self.pet:
            self.pet.add_task(next_task)

        return next_task

    def reset(self) -> None:
        """Reset this task's status back to incomplete."""
        self.completed = False

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        return f"Task('{self.title}', {self.duration_minutes}min, {self.priority}, {status})"


@dataclass
class ScheduleEntry:
    task: Task
    start_time: int
    reasoning: str


class Scheduler:
    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.schedule: list[ScheduleEntry] = []

    def _collect_tasks(self) -> list[Task]:
        return [t for t in self.owner.get_all_tasks() if not t.completed]

    def generate_schedule(self) -> list[ScheduleEntry]:
        """Build a prioritized schedule of tasks that fit within the owner's available time.

        Algorithm:
            1. Collect all incomplete tasks across the owner's pets.
            2. Sort by scheduled_time (HH:MM string, ascending) as the primary
               key, then by schedule_score (descending) to break ties.
            3. Greedily assign each task if its duration fits in the remaining
               minutes, using the real scheduled_time (converted to minutes
               from midnight) as the start_time in the entry.

        Returns:
            A list of ScheduleEntry objects representing the final schedule.
        """
        self.schedule = []
        remaining = self.owner.available_minutes
        preferred = self.owner.preferences

        sorted_tasks = sorted(
            self._collect_tasks(),
            key=lambda t: (
                t.scheduled_time if t.scheduled_time is not None else "99:99",
                -t.schedule_score(preferred),
            ),
        )

        current_time = 0
        for task in sorted_tasks:
            if task.duration_minutes > remaining:
                continue

            start = self._time_to_minutes(task.scheduled_time) if task.scheduled_time else current_time
            reasoning = "Scheduled because: " + ", ".join(filter(None, [
                f"priority={task.priority} (score {task.priority_score()})",
                f"matches owner preference '{task.category}'" if task.category in preferred else None,
                f"for {task.pet.name}" if task.pet else None,
            ])) + "."

            self.schedule.append(ScheduleEntry(task=task, start_time=start, reasoning=reasoning))
            current_time = start + task.duration_minutes
            remaining -= task.duration_minutes

        return self.schedule

    def mark_task_complete(self, title: str) -> "Task | None":
        """Find a task by title, mark it complete, and return the next occurrence if recurring."""
        for task in self.owner.get_all_tasks():
            if task.title == title:
                return task.mark_complete()
        return None

    def explain_schedule(self) -> str:
        """Return a human-readable summary of the generated schedule."""
        if not self.schedule:
            return "No schedule generated yet."
        lines = [f"Daily plan for {self.owner.name}'s pets:"]
        for entry in self.schedule:
            pet_name = entry.task.pet.name if entry.task.pet else "unknown"
            lines.append(
                f"  Minute {entry.start_time}: {entry.task.title} [{pet_name}] "
                f"({entry.task.duration_minutes}min) — {entry.reasoning}"
            )
        used = sum(e.task.duration_minutes for e in self.schedule)
        lines.append(f"Total: {used}/{self.owner.available_minutes} minutes used.")
        all_tasks = self._collect_tasks()
        skipped = [t for t in all_tasks if t not in [e.task for e in self.schedule]]
        if skipped:
            lines.append("Skipped (not enough time): " + ", ".join(t.title for t in skipped))
        return "\n".join(lines)

    @staticmethod
    def _time_to_minutes(time_str: str) -> int:
        """Convert an 'HH:MM' time string to total minutes from midnight.

        Args:
            time_str: A string in 'HH:MM' format (e.g., '07:30' -> 450).

        Returns:
            Integer total minutes since 00:00.
        """
        hours, minutes = time_str.split(":")
        return int(hours) * 60 + int(minutes)

    def detect_conflicts(self) -> list[str]:
        """Check for overlapping tasks and return warning messages instead of raising errors.

        Algorithm:
            1. Filter to tasks that have a scheduled_time set.
            2. Compare every pair (O(n^2)) using the overlap condition:
               a_start < b_end AND b_start < a_end.
            3. For each conflict, generate a human-readable warning that
               identifies the two tasks, their time ranges, and whether
               they belong to the same pet or different pets.

        Returns:
            A list of warning strings. Empty list means no conflicts found.
        """
        warnings: list[str] = []
        timed = [t for t in self._collect_tasks() if t.scheduled_time is not None]

        for i, a in enumerate(timed):
            a_start = self._time_to_minutes(a.scheduled_time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = self._time_to_minutes(b.scheduled_time)
                b_end = b_start + b.duration_minutes
                if a_start < b_end and b_start < a_end:
                    a_pet = a.pet.name if a.pet else "unknown"
                    b_pet = b.pet.name if b.pet else "unknown"
                    if a_pet == b_pet:
                        label = f"same pet ({a_pet})"
                    else:
                        label = f"different pets ({a_pet} & {b_pet})"
                    warnings.append(
                        f"⚠️  Conflict: '{a.title}' ({a.scheduled_time}-{a_end // 60:02d}:{a_end % 60:02d}) "
                        f"overlaps with '{b.title}' ({b.scheduled_time}-{b_end // 60:02d}:{b_end % 60:02d}) "
                        f"— {label}"
                    )
        return warnings

    def get_schedule(self) -> list[ScheduleEntry]:
        """Return the current list of scheduled entries."""
        return self.schedule
