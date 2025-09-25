
from dataclasses import dataclass, field
from typing import List
from .task import Task

@dataclass
class Week:
    number: int
    start_date: str
    end_date: str
    tasks: List[Task] = field(default_factory=list)
    capacity_hours: float = 40.0
    status: str = "planned"  # planned, active, completed

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_utilization(self) -> float:
        total_hours = sum(task.estimated_hours for task in self.tasks)
        return (total_hours / self.capacity_hours) if self.capacity_hours else 0.0
