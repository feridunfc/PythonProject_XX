
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import uuid, datetime

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    agent_type: str = ""
    status: str = "pending"  # pending, in_progress, completed, failed
    priority: int = 1
    estimated_hours: float = 4.0
    actual_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict] = None
    created_at: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
