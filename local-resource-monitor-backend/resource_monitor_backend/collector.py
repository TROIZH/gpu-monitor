from __future__ import annotations

from dataclasses import dataclass
import os
import platform
import re
import shutil
import subprocess
import time
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover - exercised only on minimal systems
    psutil = None

from .classification import classify_app_group
from .timeutils import utc_now_iso


BYTES_PER_GB = 1024**3


@dataclass
class CollectResult:
    metrics: dict[str, Any]
    processes: list[dict[str, Any]]


class ResourceCollector:
    def __init__(self):
        self._previous_process_io: dict[int, tuple[float, int, int]] = {}

    def collect(self) -> CollectResult:
        processes = self.collect_processes()
        metrics = {
            "id": utc_now_iso(),
            "timestamp": utc_now_iso(),
            "host": self._collect_host(),
            "cpu": self._collect_cpu(),
            "gpu": self._collect_gpu(),
            "memory": self._collect_memory(),
            "storage": self._collect_storage(),
            "thermal": self._collect_thermal(),
        }
        metrics["workload_hint"] = self._infer_metrics_workload(processes)
        return CollectResult(metrics=metrics, processes=processes)

    def collect_processes(self, limit: int = 30) -> list[dict[str, Any]]:
        if psutil is None:
            return self._collect_processes_with_ps(limit)

        rows: list[dict[str, Any]] = []
        now = time.time()
        seen_pids: set[int] = set()
        for proc in psutil.process_iter(["pid", "name", "username", "memory_info", "cmdline"]):
            try:
                pid = int(proc.info.get("pid") or 0)
                seen_pids.add(pid)
                name = proc.info.get("name") or ""
                cmdline_items = proc.info.get("cmdline") or []
                cmdline = " ".join(cmdline_items[:6])
                memory_info = proc.info.get("memory_info")
                memory_mb = (memory_info.rss / (1024**2)) if memory_info else 0.0
                cpu_percent = proc.cpu_percent(interval=None)

                disk_read_mb_s = 0.0
                disk_write_mb_s = 0.0
                try:
                    io_counters = proc.io_counters()
                    read_bytes = int(getattr(io_counters, "read_bytes", 0))
                    write_bytes = int(getattr(io_counters, "write_bytes", 0))
                    previous = self._previous_process_io.get(pid)
                    if previous:
                        previous_time, previous_read, previous_write = previous
                        elapsed = max(0.001, now - previous_time)
                        disk_read_mb_s = max(0, read_bytes - previous_read) / (1024**2) / elapsed
                        disk_write_mb_s = max(0, write_bytes - previous_write) / (1024**2) / elapsed
                    self._previous_process_io[pid] = (now, read_bytes, write_bytes)
                except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
                    pass

                rows.append(
                    {
                        "timestamp": utc_now_iso(),
                        "pid": pid,
                        "process_name": name,
                        "app_group": classify_app_group(name, cmdline),
                        "username": proc.info.get("username"),
                        "cpu_percent": round(cpu_percent, 2),
                        "memory_mb": round(memory_mb, 2),
                        "disk_read_mb_s": round(disk_read_mb_s, 2),
                        "disk_write_mb_s": round(disk_write_mb_s, 2),
                        "gpu_hint": False,
                    }
                )
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

        stale_pids = set(self._previous_process_io) - seen_pids
        for pid in stale_pids:
            self._previous_process_io.pop(pid, None)

        rows.sort(key=lambda item: (item["cpu_percent"], item["memory_mb"]), reverse=True)
        return rows[:limit]

    def _collect_processes_with_ps(self, limit: int) -> list[dict[str, Any]]:
        result = self._run_command(["ps", "-axo", "pid=,pcpu=,rss=,comm="], timeout=2)
        if not result:
            return []

        rows: list[dict[str, Any]] = []
        for line in result.splitlines():
            match = re.match(r"\s*(\d+)\s+([\d.]+)\s+(\d+)\s+(.+?)\s*$", line)
            if not match:
                continue
            pid, cpu_percent, rss_kb, command = match.groups()
            memory_mb = int(rss_kb) / 1024
            rows.append(
                {
                    "timestamp": utc_now_iso(),
                    "pid": int(pid),
                    "process_name": os.path.basename(command),
                    "app_group": classify_app_group(command, command),
                    "username": None,
                    "cpu_percent": round(float(cpu_percent), 2),
                    "memory_mb": round(memory_mb, 2),
                    "disk_read_mb_s": 0.0,
                    "disk_write_mb_s": 0.0,
                    "gpu_hint": False,
                }
            )

        rows.sort(key=lambda item: (item["cpu_percent"], item["memory_mb"]), reverse=True)
        return rows[:limit]

    def _collect_host(self) -> dict[str, Any]:
        host = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }

        if psutil is not None:
            boot_time = getattr(psutil, "boot_time", None)
            if boot_time:
                host["boot_time_epoch"] = int(boot_time())

        return host

    def _collect_cpu(self) -> dict[str, Any]:
        if psutil is None:
            return self._collect_cpu_with_top()

        try:
            per_core = psutil.cpu_percent(interval=0.2, percpu=True)
            total = psutil.cpu_percent(interval=None, percpu=False)
            times = psutil.cpu_times_percent(interval=None, percpu=False)
        except Exception:
            return self._collect_cpu_with_top()

        try:
            freq = psutil.cpu_freq()
        except Exception:
            freq = None

        return {
            "available": True,
            "total_percent": round(total, 2),
            "user_percent": round(getattr(times, "user", 0.0), 2),
            "system_percent": round(getattr(times, "system", 0.0), 2),
            "idle_percent": round(getattr(times, "idle", 0.0), 2),
            "cores": [round(value, 2) for value in per_core],
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "frequency_mhz": round(freq.current, 2) if freq else None,
            "source": "psutil",
        }

    def _collect_cpu_with_top(self) -> dict[str, Any]:
        result = self._run_command(["top", "-l", "1", "-n", "0"], timeout=3)
        match = re.search(r"CPU usage:\s+([\d.]+)% user,\s+([\d.]+)% sys,\s+([\d.]+)% idle", result or "")
        if not match:
            return {"available": False, "reason": "cpu metrics unavailable"}

        user, system, idle = (float(value) for value in match.groups())
        return {
            "available": True,
            "total_percent": round(user + system, 2),
            "user_percent": round(user, 2),
            "system_percent": round(system, 2),
            "idle_percent": round(idle, 2),
            "cores": [],
            "physical_cores": None,
            "logical_cores": os.cpu_count(),
            "frequency_mhz": None,
            "source": "top",
        }

    def _collect_gpu(self) -> dict[str, Any]:
        return {
            "available": False,
            "usage_percent": None,
            "source": "not_configured",
            "reason": "GPU utilization requires a privileged powermetrics sampler on macOS. Install an authorized helper to enable precise GPU metrics.",
        }

    def _collect_memory(self) -> dict[str, Any]:
        memory_pressure_free_percent = self._read_memory_pressure_free_percent()

        if psutil is None:
            return self._collect_memory_with_vm_stat(memory_pressure_free_percent)

        virtual = psutil.virtual_memory()
        swap = psutil.swap_memory()
        used_gb = (virtual.total - virtual.available) / BYTES_PER_GB
        pressure = self._classify_memory_pressure(memory_pressure_free_percent, virtual.percent)

        return {
            "available": True,
            "physical_gb": round(virtual.total / BYTES_PER_GB, 2),
            "used_gb": round(used_gb, 2),
            "available_gb": round(virtual.available / BYTES_PER_GB, 2),
            "percent": round(virtual.percent, 2),
            "app_gb": None,
            "wired_gb": round(getattr(virtual, "wired", 0) / BYTES_PER_GB, 2) if hasattr(virtual, "wired") else None,
            "compressed_gb": None,
            "cached_gb": round(getattr(virtual, "cached", 0) / BYTES_PER_GB, 2) if hasattr(virtual, "cached") else None,
            "swap_gb": round(swap.used / BYTES_PER_GB, 2),
            "swap_total_gb": round(swap.total / BYTES_PER_GB, 2),
            "swap_percent": round(swap.percent, 2),
            "pressure": pressure,
            "memory_pressure_free_percent": memory_pressure_free_percent,
            "source": "psutil+memory_pressure",
        }

    def _collect_memory_with_vm_stat(self, memory_pressure_free_percent: int | None) -> dict[str, Any]:
        total_bytes = self._read_sysctl_int("hw.memsize")
        vm_stat = self._read_vm_stat()
        swap = self._read_swap_usage()

        if total_bytes is None:
            return {
                "available": False,
                "pressure": self._classify_memory_pressure(memory_pressure_free_percent, None),
                "memory_pressure_free_percent": memory_pressure_free_percent,
                "source": "memory_pressure",
            }

        page_size = vm_stat.get("page_size", 16384)
        free_pages = vm_stat.get("Pages free", 0) + vm_stat.get("Pages speculative", 0)
        wired_pages = vm_stat.get("Pages wired down", 0)
        compressor_pages = vm_stat.get("Pages occupied by compressor", 0)
        cached_pages = vm_stat.get("File-backed pages", 0)

        # File-backed pages are reclaimable cache on macOS. Counting only free pages
        # makes memory look permanently full on unified-memory Macs.
        available_bytes = (free_pages + cached_pages) * page_size
        used_bytes = max(0, total_bytes - available_bytes)
        used_percent = (used_bytes / total_bytes) * 100 if total_bytes else None

        return {
            "available": True,
            "physical_gb": round(total_bytes / BYTES_PER_GB, 2),
            "used_gb": round(used_bytes / BYTES_PER_GB, 2),
            "available_gb": round(available_bytes / BYTES_PER_GB, 2),
            "percent": round(used_percent, 2) if used_percent is not None else None,
            "app_gb": None,
            "wired_gb": round((wired_pages * page_size) / BYTES_PER_GB, 2),
            "compressed_gb": round((compressor_pages * page_size) / BYTES_PER_GB, 2),
            "cached_gb": round((cached_pages * page_size) / BYTES_PER_GB, 2),
            "swap_gb": swap.get("used_gb"),
            "swap_total_gb": swap.get("total_gb"),
            "swap_percent": swap.get("percent"),
            "pressure": self._classify_memory_pressure(memory_pressure_free_percent, used_percent),
            "memory_pressure_free_percent": memory_pressure_free_percent,
            "source": "vm_stat+memory_pressure",
        }

    def _read_memory_pressure_free_percent(self) -> int | None:
        if not shutil.which("memory_pressure"):
            return None

        result = self._run_command(["memory_pressure", "-Q"], timeout=3)
        if not result:
            return None

        match = re.search(r"System-wide memory free percentage:\s+(\d+)%", result)
        return int(match.group(1)) if match else None

    def _classify_memory_pressure(self, free_percent: int | None, used_percent: float | None) -> str:
        if free_percent is not None:
            if free_percent <= 5:
                return "red"
            if free_percent <= 20:
                return "yellow"
            return "green"

        if used_percent is None:
            return "unknown"
        if used_percent >= 92:
            return "red"
        if used_percent >= 80:
            return "yellow"
        return "green"

    def _read_sysctl_int(self, name: str) -> int | None:
        result = self._run_command(["sysctl", "-n", name], timeout=2)
        if not result:
            return None
        try:
            return int(result.strip())
        except ValueError:
            return None

    def _read_vm_stat(self) -> dict[str, int]:
        result = self._run_command(["vm_stat"], timeout=2)
        if not result:
            return {}

        values: dict[str, int] = {}
        page_size_match = re.search(r"page size of (\d+) bytes", result)
        if page_size_match:
            values["page_size"] = int(page_size_match.group(1))

        for line in result.splitlines():
            if ":" not in line:
                continue
            key, raw_value = line.split(":", 1)
            digits = re.sub(r"[^\d]", "", raw_value)
            if digits:
                values[key.strip().strip('"')] = int(digits)
        return values

    def _read_swap_usage(self) -> dict[str, float | None]:
        result = self._run_command(["sysctl", "vm.swapusage"], timeout=2)
        if not result:
            return {"total_gb": None, "used_gb": None, "percent": None}

        match = re.search(r"total = ([\d.]+)M\s+used = ([\d.]+)M\s+free = ([\d.]+)M", result)
        if not match:
            return {"total_gb": None, "used_gb": None, "percent": None}

        total_m, used_m, _free_m = (float(value) for value in match.groups())
        total_gb = total_m / 1024
        used_gb = used_m / 1024
        return {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "percent": round((used_gb / total_gb) * 100, 2) if total_gb else None,
        }

    def _collect_storage(self) -> dict[str, Any]:
        path = "/"
        if psutil is not None:
            usage = psutil.disk_usage(path)
            return {
                "available": True,
                "path": path,
                "total_gb": round(usage.total / BYTES_PER_GB, 2),
                "used_gb": round(usage.used / BYTES_PER_GB, 2),
                "free_gb": round(usage.free / BYTES_PER_GB, 2),
                "free_percent": round((usage.free / usage.total) * 100, 2) if usage.total else None,
                "percent": round(usage.percent, 2),
                "source": "psutil",
            }

        total, used, free = shutil.disk_usage(path)
        return {
            "available": True,
            "path": path,
            "total_gb": round(total / BYTES_PER_GB, 2),
            "used_gb": round(used / BYTES_PER_GB, 2),
            "free_gb": round(free / BYTES_PER_GB, 2),
            "free_percent": round((free / total) * 100, 2) if total else None,
            "percent": round((used / total) * 100, 2) if total else None,
            "source": "shutil",
        }

    def _collect_thermal(self) -> dict[str, Any]:
        if platform.system() != "Darwin" or not shutil.which("pmset"):
            return {"available": False, "state": "unknown", "reason": "thermal state unavailable on this platform"}

        result = self._run_command(["pmset", "-g", "therm"], timeout=3)
        if not result:
            return {"available": False, "state": "unknown", "reason": "pmset thermal output unavailable"}

        lowered = result.lower()
        if "cpu_speed_limit" in lowered or "gpu_speed_limit" in lowered:
            return {"available": True, "state": "fair", "raw": result.strip(), "source": "pmset"}

        return {"available": True, "state": "nominal", "raw": result.strip(), "source": "pmset"}

    def _infer_metrics_workload(self, processes: list[dict[str, Any]]) -> str:
        from .classification import infer_workload

        return infer_workload(processes)

    def _run_command(self, args: list[str], timeout: float) -> str | None:
        try:
            completed = subprocess.run(
                args,
                check=False,
                capture_output=True,
                timeout=timeout,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None

        stdout = completed.stdout.decode("utf-8", errors="replace") if completed.stdout else ""
        stderr = completed.stderr.decode("utf-8", errors="replace") if completed.stderr else ""
        output = stdout.strip() or stderr.strip()
        return output or None
