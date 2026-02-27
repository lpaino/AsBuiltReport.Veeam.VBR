"""Utilitários de validação e busca aproximada."""
from __future__ import annotations

import re
from difflib import get_close_matches

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_REGEX = re.compile(r"^[0-9+()\-\s]{8,}$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_REGEX.match(value.strip()))


def is_valid_phone(value: str) -> bool:
    return bool(PHONE_REGEX.match(value.strip()))


def similar_names(query: str, names: list[str], limit: int = 5) -> list[str]:
    """Retorna nomes mais próximos usando a lógica do difflib (Levenshtein-like)."""
    query = query.strip()
    if not query:
        return []
    lower_map = {name.lower(): name for name in names}
    candidates = get_close_matches(query.lower(), list(lower_map.keys()), n=limit, cutoff=0.55)
    return [lower_map[c] for c in candidates]
