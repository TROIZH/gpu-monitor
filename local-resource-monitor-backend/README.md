# Local Resource Monitor Backend

Local-first backend prototype for the Vibe / Voice Coding hardware monitor.

## What It Does

- Collects local CPU, per-core CPU, RAM, swap, storage, process, thermal, and GPU-availability metrics.
- Stores samples and bottleneck events in SQLite.
- Classifies current bottlenecks with rule-based analysis.
- Exposes a lightweight HTTP API for the frontend prototype.
- Defaults to local-only data storage and no network calls.

## Run

```bash
cd "/Users/troy/Documents/New project/local-resource-monitor-backend"
python3 -m resource_monitor_backend --port 8765
```

Then open:

```bash
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/metrics/current
curl http://127.0.0.1:8765/bottlenecks/current
```

## API

- `GET /health`
- `GET /dashboard/current`
- `GET /metrics/current`
- `GET /metrics/history?range=10m|1h|24h|7d`
- `GET /processes/top?sort=cpu|memory|disk&limit=10`
- `GET /bottlenecks/current`
- `GET /bottlenecks/history?range=24h|7d|30d`
- `GET /profile/current`
- `GET /insights/weekly`
- `GET /recommendations/upgrade`
- `GET /settings`
- `POST /settings`
- `POST /feedback/recommendation`

## Environment

- `RESOURCE_MONITOR_PORT`: default `8765`
- `RESOURCE_MONITOR_HOST`: default `127.0.0.1`
- `RESOURCE_MONITOR_DB_PATH`: default `./resource_monitor.sqlite3`
- `RESOURCE_MONITOR_SAMPLE_INTERVAL_SECONDS`: default `5`

## Dependencies

The backend runs with Python standard library fallbacks. If `psutil` is available, it will use it for richer CPU, memory, disk, and process metrics. Without `psutil`, it falls back to macOS commands including `top`, `ps`, `vm_stat`, `memory_pressure`, `sysctl`, `df`, and `pmset`.

Optional install:

```bash
python3 -m pip install ".[psutil]"
```

## Privacy Defaults

The backend stores metrics and process metadata only. It does not inspect code, file contents, terminal output, prompts, voice recordings, browser contents, or screenshots.
