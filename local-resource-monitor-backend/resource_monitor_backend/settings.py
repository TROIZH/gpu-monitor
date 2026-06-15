from __future__ import annotations

from dataclasses import asdict, dataclass
import os


@dataclass
class MonitorSettings:
    sample_interval_seconds: float = 5.0
    raw_retention_hours: int = 24
    aggregate_retention_days: int = 30
    event_retention_days: int = 365
    cpu_bound_percent: float = 85.0
    cpu_core_bound_percent: float = 95.0
    memory_pressure_yellow_percent: float = 80.0
    memory_pressure_red_percent: float = 92.0
    swap_warning_gb: float = 2.0
    storage_low_free_percent: float = 10.0
    max_top_processes: int = 10
    enable_process_grouping: bool = True
    enable_network_recommendations: bool = False

    @classmethod
    def from_env(cls) -> "MonitorSettings":
        settings = cls()
        interval = os.getenv("RESOURCE_MONITOR_SAMPLE_INTERVAL_SECONDS")
        if interval:
            try:
                settings.sample_interval_seconds = max(1.0, float(interval))
            except ValueError:
                pass
        return settings

    def to_dict(self) -> dict:
        return asdict(self)

    def update_from_dict(self, payload: dict) -> None:
        for key, value in payload.items():
            if not hasattr(self, key):
                continue

            current_value = getattr(self, key)
            if isinstance(current_value, bool):
                setattr(self, key, bool(value))
            elif isinstance(current_value, int) and not isinstance(current_value, bool):
                setattr(self, key, int(value))
            elif isinstance(current_value, float):
                setattr(self, key, float(value))
            else:
                setattr(self, key, value)

