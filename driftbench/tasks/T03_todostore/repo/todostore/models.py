"""Todo data model."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .timeutil import parse_iso_date

PRIORITIES = {1: "high", 2: "normal", 3: "low"}


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    priority: int = 2
    tags: list[str] = field(default_factory=list)
    created: date | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if self.priority not in PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(PRIORITIES)}, got {self.priority!r}")

    @property
    def priority_label(self) -> str:
        return PRIORITIES[self.priority]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "priority": self.priority,
            "tags": list(self.tags),
            "created": self.created.isoformat() if self.created else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Todo":
        created = data.get("created")
        return cls(
            id=int(data["id"]),
            title=data["title"],
            done=bool(data.get("done", False)),
            priority=int(data.get("priority", 2)),
            tags=list(data.get("tags", [])),
            created=parse_iso_date(created) if created else None,
        )
