from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def parse_range_seconds(value: str | None, default_seconds: int) -> int:
    if not value:
        return default_seconds

    normalized = value.strip().lower()
    units = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
    }

    try:
        suffix = normalized[-1]
        multiplier = units[suffix]
        amount = int(normalized[:-1])
        return max(1, amount * multiplier)
    except (KeyError, ValueError, IndexError):
        return default_seconds

