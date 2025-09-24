from __future__ import annotations

from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from datetime import datetime
from uuid import uuid4
# models/sprint.py
import uuid
from pydantic import BaseModel, Field




class Task(BaseModel):
    """Plan ve yürütmede kullanılan görev modeli."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    task_id: str = Field(default_factory=lambda: f"t-{uuid.uuid4().hex[:8]}")

    title: str = ""
    description: str = ""
    agent_type: str = ""  # architect | codegen | tester | critic | debugger | integrator
    status: str = "pending"  # pending | in_progress | completed | failed
    priority: int = 1
    estimated_hours: float = 4.0
    actual_hours: float = 0.0
    dependencies: List[str] = Field(default_factory=list)
    result: Optional[Any] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # ---- geri uyum: t.id <-> t.task_id ----
    @property
    def id(self) -> str:
        return self.task_id

    @id.setter
    def id(self, v: str) -> None:
        self.task_id = v


class Week(BaseModel):
    """Haftalık plan kapsayıcısı."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    week_number: int
    tasks: List[Task] = Field(default_factory=list)


class Sprint(BaseModel):
    """ArchitectAgent’ın ürettiği JSON planı."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    sprint_id: str = Field(
        default_factory=lambda: str(uuid4()),
        validation_alias=AliasChoices("sprint_id", "id"),
    )
    sprint_title: str = Field(
        default="",
        validation_alias=AliasChoices("sprint_title", "title"),
    )
    sprint_goal: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("sprint_goal", "goal"),
    )
    weeks: List[Week] = Field(default_factory=list)

    # ---- yardımcı metotlar ----
    def get_all_tasks(self) -> List[Task]:
        return [t for w in self.weeks for t in w.tasks]

    def get_total_tasks(self) -> int:
        return len(self.get_all_tasks())

    def get_completed_tasks(self) -> int:
        return sum(1 for t in self.get_all_tasks() if t.status == "completed")

    # ---- geri uyum: sprint.id / sprint.title / sprint.goal beklentileri ----
    @property
    def id(self) -> str:
        return self.sprint_id

    @id.setter
    def id(self, v: str) -> None:
        self.sprint_id = v

    @property
    def title(self) -> str:
        return self.sprint_title

    @title.setter
    def title(self, v: str) -> None:
        self.sprint_title = v

    @property
    def goal(self) -> Optional[str]:
        return self.sprint_goal

    @goal.setter
    def goal(self, v: Optional[str]) -> None:
        self.sprint_goal = v
