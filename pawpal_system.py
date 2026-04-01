from dataclasses import dataclass, field

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
    completed: bool = False
    pet: "Pet | None" = None

    def priority_score(self) -> int:
        """Return a numeric score (1-3) based on the task's priority level."""
        scores = {"low": 1, "medium": 2, "high": 3}
        return scores.get(self.priority, 0)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

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
        """Build a prioritized schedule of tasks that fit within the owner's available time."""
        self.schedule = []
        remaining_minutes = self.owner.available_minutes
        preferred = self.owner.preferences

        def score(task: Task) -> int:
            s = task.priority_score()
            if task.category in preferred:
                s += 2
            return s

        sorted_tasks = sorted(self._collect_tasks(), key=score, reverse=True)

        current_time = 0
        for task in sorted_tasks:
            if task.duration_minutes <= remaining_minutes:
                reasons = []
                reasons.append(f"priority={task.priority} (score {task.priority_score()})")
                if task.category in preferred:
                    reasons.append(f"matches owner preference '{task.category}'")
                if task.pet:
                    reasons.append(f"for {task.pet.name}")
                reasoning = f"Scheduled because: {', '.join(reasons)}."

                self.schedule.append(ScheduleEntry(
                    task=task,
                    start_time=current_time,
                    reasoning=reasoning,
                ))
                current_time += task.duration_minutes
                remaining_minutes -= task.duration_minutes

        return self.schedule

    def mark_task_complete(self, title: str) -> None:
        """Find a task by title and mark it as complete."""
        for task in self.owner.get_all_tasks():
            if task.title == title:
                task.mark_complete()
                return

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

    def get_schedule(self) -> list[ScheduleEntry]:
        """Return the current list of scheduled entries."""
        return self.schedule
