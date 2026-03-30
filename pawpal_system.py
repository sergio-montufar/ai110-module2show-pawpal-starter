from dataclasses import dataclass, field

@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)

    def update_preferences(self, preferences: list[str]) -> None:
        pass

    def set_availability(self, minutes: int) -> None:
        pass

@dataclass
class Pet:
    name: str
    species: str
    age: int
    owner: Owner

    def get_summary(self) -> str:
        pass

@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str

    def priority_score(self) -> int:
        pass

    def __repr__(self) -> str:
        return f"Task(title='{self.title}', duration={self.duration_minutes}min, priority='{self.priority}')"

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []
        self.schedule: list[dict] = []

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass

    def generate_schedule(self) -> list[dict]:
        pass

    def explain_schedule(self) -> str:
        pass

    def get_schedule(self) -> list[dict]:
        pass
