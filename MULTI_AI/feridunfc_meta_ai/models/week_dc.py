from dataclasses import dataclass, field
from typing import List
from .task_dc import Task

@dataclass
class Week:
    number: int
    start_date: str
    end_date: str
    tasks: List[Task] = field(default_factory=list)
    capacity_hours: float = 40.0
    status: str = "planned"
    def add_task(self, task: Task): self.tasks.append(task)
    def get_utilization(self) -> float:
        total = sum(t.estimated_hours for t in self.tasks)
        return (total/self.capacity_hours) if self.capacity_hours else 0.0
