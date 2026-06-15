from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from threading import Event, RLock, Thread
import time
from typing import Any
from urllib.parse import parse_qs, urlparse

from .analyzer import BottleneckAnalyzer
from .collector import ResourceCollector
from .settings import MonitorSettings
from .store import ResourceStore
from .timeutils import utc_now_iso


DEFAULT_DB_PATH = str(Path(__file__).resolve().parents[1] / "resource_monitor.sqlite3")


class MonitorRuntime:
    def __init__(self, settings: MonitorSettings, store: ResourceStore):
        self.settings = settings
        self.store = store
        self.collector = ResourceCollector()
        self.analyzer = BottleneckAnalyzer(settings)
        self._lock = RLock()
        self._stop_event = Event()
        self._thread: Thread | None = None
        self.started_at = utc_now_iso()
        self.last_error: str | None = None
        self.last_collected_at: str | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = Thread(target=self._run_loop, name="resource-monitor-collector", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)

    def collect_once(self) -> dict[str, Any]:
        with self._lock:
            result = self.collector.collect()
            event = self.analyzer.analyze_current(result.metrics, result.processes)
            self.store.save_sample(result.metrics, result.processes, event)
            self.store.purge_old(
                raw_retention_hours=self.settings.raw_retention_hours,
                event_retention_days=self.settings.event_retention_days,
            )
            self.last_error = None
            self.last_collected_at = result.metrics.get("timestamp") or utc_now_iso()
            return {"metrics": result.metrics, "processes": result.processes, "event": event}

    def status(self) -> dict[str, Any]:
        return {
            "ok": self.last_error is None,
            "version": "0.1.0",
            "started": self._thread is not None,
            "collector_alive": bool(self._thread and self._thread.is_alive()),
            "last_collected_at": self.last_collected_at,
            "last_error": self.last_error,
            "privacy": {
                "local_only": True,
                "stores_file_contents": False,
                "stores_code_contents": False,
                "stores_prompts": False,
                "stores_voice": False,
                "network_recommendations_enabled": self.settings.enable_network_recommendations,
            },
        }

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self.collect_once()
            except Exception as exc:  # pragma: no cover - defensive for long-running server
                self.last_error = f"{type(exc).__name__}: {exc}"
            self._stop_event.wait(self.settings.sample_interval_seconds)


class AppState:
    def __init__(self, runtime: MonitorRuntime):
        self.runtime = runtime


def create_handler(state: AppState) -> type[BaseHTTPRequestHandler]:
    class MonitorRequestHandler(BaseHTTPRequestHandler):
        server_version = "ResourceMonitorBackend/0.1"

        def do_OPTIONS(self) -> None:
            self._send_empty(HTTPStatus.NO_CONTENT)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)

            try:
                if parsed.path == "/health":
                    self._send_json(state.runtime.status())
                elif parsed.path == "/metrics/current":
                    self._send_json(self._current_metrics(query))
                elif parsed.path == "/dashboard/current":
                    self._send_json(self._dashboard_current(query))
                elif parsed.path == "/metrics/history":
                    range_value = self._first(query, "range")
                    self._send_json({"items": state.runtime.store.get_metrics_history(range_value)})
                elif parsed.path == "/processes/top":
                    self._send_json(self._top_processes(query))
                elif parsed.path == "/bottlenecks/current":
                    self._send_json(self._current_bottleneck(query))
                elif parsed.path == "/bottlenecks/history":
                    range_value = self._first(query, "range")
                    self._send_json({"items": state.runtime.store.get_events_history(range_value)})
                elif parsed.path == "/profile/current":
                    self._send_json(self._current_profile(query))
                elif parsed.path == "/insights/weekly":
                    self._send_json(self._weekly_insights())
                elif parsed.path == "/recommendations/upgrade":
                    self._send_json(self._upgrade_recommendation())
                elif parsed.path == "/settings":
                    self._send_json(state.runtime.settings.to_dict())
                else:
                    self._send_json({"error": "not_found", "path": parsed.path}, status=HTTPStatus.NOT_FOUND)
            except Exception as exc:
                self._send_json(
                    {"error": "internal_error", "message": f"{type(exc).__name__}: {exc}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            try:
                payload = self._read_json_body()
                if parsed.path == "/settings":
                    state.runtime.settings.update_from_dict(payload)
                    self._send_json(state.runtime.settings.to_dict())
                elif parsed.path == "/feedback/recommendation":
                    payload.setdefault("timestamp", utc_now_iso())
                    state.runtime.store.save_feedback(payload)
                    self._send_json({"ok": True})
                else:
                    self._send_json({"error": "not_found", "path": parsed.path}, status=HTTPStatus.NOT_FOUND)
            except ValueError as exc:
                self._send_json({"error": "bad_request", "message": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            except Exception as exc:
                self._send_json(
                    {"error": "internal_error", "message": f"{type(exc).__name__}: {exc}"},
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )

        def log_message(self, format: str, *args: Any) -> None:
            if os.getenv("RESOURCE_MONITOR_ACCESS_LOG") == "1":
                super().log_message(format, *args)

        def _current_metrics(self, query: dict[str, list[str]]) -> dict[str, Any]:
            refresh = self._first(query, "refresh") == "true"
            if refresh:
                sample = state.runtime.collect_once()
                return sample["metrics"]

            latest = state.runtime.store.get_latest_metric()
            if latest is None:
                sample = state.runtime.collect_once()
                return sample["metrics"]
            return latest

        def _current_bottleneck(self, query: dict[str, list[str]]) -> dict[str, Any]:
            refresh = self._first(query, "refresh") == "true"
            if refresh:
                sample = state.runtime.collect_once()
                return sample["event"]

            latest = state.runtime.store.get_latest_event()
            if latest is None:
                sample = state.runtime.collect_once()
                return sample["event"]
            return latest

        def _top_processes(self, query: dict[str, list[str]]) -> dict[str, Any]:
            sort_key = self._first(query, "sort") or "cpu"
            limit = self._int_param(query, "limit", state.runtime.settings.max_top_processes)
            processes = state.runtime.store.get_latest_processes()
            if not processes:
                processes = state.runtime.collect_once()["processes"]

            key_map = {
                "cpu": "cpu_percent",
                "memory": "memory_mb",
                "disk": "disk_write_mb_s",
            }
            field = key_map.get(sort_key, "cpu_percent")
            ordered = sorted(processes, key=lambda item: float(item.get(field) or 0), reverse=True)
            return {"sort": sort_key, "items": ordered[: max(1, min(limit, 100))]}

        def _current_profile(self, query: dict[str, list[str]]) -> dict[str, Any]:
            range_value = self._first(query, "range") or "7d"
            events = state.runtime.store.get_events_history(range_value)
            metrics = state.runtime.store.get_metrics_history(range_value)
            processes = state.runtime.store.get_latest_processes()
            profile = state.runtime.analyzer.build_profile(events, metrics, processes)
            return profile

        def _dashboard_current(self, query: dict[str, list[str]]) -> dict[str, Any]:
            refresh = self._first(query, "refresh") == "true"
            if refresh or state.runtime.store.get_latest_metric() is None:
                sample = state.runtime.collect_once()
                metrics = sample["metrics"]
                event = sample["event"]
                processes = sample["processes"]
            else:
                metrics = state.runtime.store.get_latest_metric()
                event = state.runtime.store.get_latest_event()
                processes = state.runtime.store.get_latest_processes()

            events = state.runtime.store.get_events_since(state.runtime.started_at)
            history = state.runtime.store.get_metrics_since(state.runtime.started_at)
            profile = state.runtime.analyzer.build_profile(events, history, processes)
            profile["period"] = "runtime"
            recommendation = state.runtime.analyzer.build_upgrade_recommendation(profile, event)
            top_cpu = sorted(processes, key=lambda item: float(item.get("cpu_percent") or 0), reverse=True)[:8]
            top_memory = sorted(processes, key=lambda item: float(item.get("memory_mb") or 0), reverse=True)[:8]

            return {
                "generated_at": utc_now_iso(),
                "metrics": metrics,
                "bottleneck": event,
                "top_processes": {
                    "cpu": top_cpu,
                    "memory": top_memory,
                },
                "profile": profile,
                "recommendation": recommendation,
                "history": history[-120:],
            }

        def _weekly_insights(self) -> dict[str, Any]:
            profile = self._current_profile({"range": ["7d"]})
            latest_event = state.runtime.store.get_latest_event()
            return {
                "generated_at": utc_now_iso(),
                "period": "7d",
                "profile": profile,
                "current_bottleneck": latest_event,
                "highlights": self._insight_highlights(profile, latest_event),
            }

        def _upgrade_recommendation(self) -> dict[str, Any]:
            profile = self._current_profile({"range": ["30d"]})
            latest_event = state.runtime.store.get_latest_event()
            return state.runtime.analyzer.build_upgrade_recommendation(profile, latest_event)

        def _insight_highlights(self, profile: dict[str, Any], latest_event: dict[str, Any] | None) -> list[str]:
            highlights = [profile.get("summary") or "暂无足够数据生成画像。"]
            if latest_event:
                highlights.append(latest_event.get("summary") or "当前没有明确瓶颈。")
            if profile.get("device_fit_score", 100) < 70:
                highlights.append("设备匹配度偏低，建议先观察 RAM、散热和 CPU 的长期趋势。")
            return highlights

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("Request body must be valid JSON") from exc
            if not isinstance(payload, dict):
                raise ValueError("Request body must be a JSON object")
            return payload

        def _first(self, query: dict[str, list[str]], key: str) -> str | None:
            values = query.get(key)
            return values[0] if values else None

        def _int_param(self, query: dict[str, list[str]], key: str, default: int) -> int:
            value = self._first(query, key)
            if value is None:
                return default
            try:
                return int(value)
            except ValueError:
                return default

        def _send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(body)

        def _send_empty(self, status: HTTPStatus) -> None:
            self.send_response(status)
            self._send_cors_headers()
            self.end_headers()

        def _send_cors_headers(self) -> None:
            origin = self.headers.get("Origin") or ""
            allowed_origins = {
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:8000",
                "http://127.0.0.1:8000",
                "null",
            }
            allow_origin = origin if origin in allowed_origins else "http://127.0.0.1:8000"
            self.send_header("Access-Control-Allow-Origin", allow_origin)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    return MonitorRequestHandler


def build_runtime(db_path: str | None = None) -> MonitorRuntime:
    settings = MonitorSettings.from_env()
    store = ResourceStore(db_path or os.getenv("RESOURCE_MONITOR_DB_PATH") or DEFAULT_DB_PATH)
    return MonitorRuntime(settings=settings, store=store)


def serve(host: str, port: int, db_path: str | None = None) -> ThreadingHTTPServer:
    runtime = build_runtime(db_path)
    runtime.start()
    state = AppState(runtime)
    handler = create_handler(state)
    server = ThreadingHTTPServer((host, port), handler)
    server.runtime = runtime  # type: ignore[attr-defined]
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local resource monitor backend.")
    parser.add_argument("--host", default=os.getenv("RESOURCE_MONITOR_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("RESOURCE_MONITOR_PORT", "8765")))
    parser.add_argument("--db-path", default=os.getenv("RESOURCE_MONITOR_DB_PATH", DEFAULT_DB_PATH))
    args = parser.parse_args()

    server = serve(args.host, args.port, args.db_path)
    print(f"Resource monitor backend listening on http://{args.host}:{args.port}")
    print(f"SQLite DB: {args.db_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.runtime.stop()  # type: ignore[attr-defined]
        server.server_close()


if __name__ == "__main__":
    main()
