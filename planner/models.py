"""Data models for the planner package."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Represents a single task in the planner."""

    id: int
    title: str
    priority: str = "medium"
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())