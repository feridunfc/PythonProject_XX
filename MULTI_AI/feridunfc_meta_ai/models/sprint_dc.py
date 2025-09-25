from dataclasses import dataclass, field
from typing import List
import uuid, datetime
from .week_dc import Week

@dataclass
class Sprint:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    goal: str = ""
    weeks: List[Week] = field(default_factory=list)
    status: str = "planned"
    velocity: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    def add_week(self, week: Week): self.weeks.append(week)
    def get_total_tasks(self) -> int: return sum(len(w.tasks) for w in self.weeks)
    def get_completed_tasks(self) -> int: return sum(sum(1 for t in w.tasks if t.status=="completed") for w in self.weeks)
