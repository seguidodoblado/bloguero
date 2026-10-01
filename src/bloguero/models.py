from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Blog:
    id: str
    name: str
    url: str


@dataclass
class Post:
    id: str
    blog_id: str
    title: str
    html: str
    status: str  # "live" | "draft" | "scheduled"
    labels: list[str] = field(default_factory=list)
    updated: datetime | None = None
    published: datetime | None = None
    dirty: bool = False
