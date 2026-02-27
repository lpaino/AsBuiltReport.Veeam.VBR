"""Modelos de dados do sistema RSVP."""
from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass
class Guest:
    """Representa um convidado principal cadastrado no evento."""

    name: str
    phone: str
    email: str
    invited_count: int = 1
    confirmed_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Guest":
        return cls(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            invited_count=int(data.get("invited_count", 1)),
            confirmed_count=int(data.get("confirmed_count", 0)),
        )
