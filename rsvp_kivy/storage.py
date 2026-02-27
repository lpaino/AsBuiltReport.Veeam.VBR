"""Persistência local (JSON) e exportação CSV."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from models import Guest


class GuestRepository:
    def __init__(self, data_file: Path):
        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> list[Guest]:
        if not self.data_file.exists():
            return []
        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Guest.from_dict(item) for item in raw]

    def save_all(self, guests: list[Guest]) -> None:
        with self.data_file.open("w", encoding="utf-8") as f:
            json.dump([g.to_dict() for g in guests], f, ensure_ascii=False, indent=2)

    @staticmethod
    def export_csv(guests: list[Guest], output_file: Path) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Nome", "Telefone", "Email", "Convites", "Confirmados"])
            for g in guests:
                writer.writerow([g.name, g.phone, g.email, g.invited_count, g.confirmed_count])
        return output_file
