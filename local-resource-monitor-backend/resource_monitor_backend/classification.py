from __future__ import annotations


AGENT_KEYWORDS = (
    "codex",
    "claude",
    "cursor",
    "openclaw",
    "gemini",
    "aider",
)
IDE_KEYWORDS = ("code", "xcode", "zed", "jetbrains", "idea", "pycharm", "webstorm", "cursor")
BROWSER_KEYWORDS = ("chrome", "safari", "arc", "firefox", "brave", "edge")
MODEL_KEYWORDS = ("ollama", "llama", "whisper", "mlx", "pytorch", "python", "transformers")
VIDEO_KEYWORDS = ("final cut", "premiere", "resolve", "ffmpeg", "compressor", "media encoder")
BUILD_KEYWORDS = ("clang", "swiftc", "rustc", "tsc", "webpack", "vite", "node", "npm", "pnpm", "yarn")
INFRA_KEYWORDS = ("docker", "colima", "postgres", "redis", "localstack", "mysql", "mongod")


def normalize_process_name(name: str | None) -> str:
    return (name or "").strip().lower()


def classify_app_group(process_name: str | None, command_line: str | None = None) -> str:
    text = f"{normalize_process_name(process_name)} {(command_line or '').lower()}"

    if any(keyword in text for keyword in AGENT_KEYWORDS):
        return "Agent Coding"
    if any(keyword in text for keyword in VIDEO_KEYWORDS):
        return "Video Editing"
    if any(keyword in text for keyword in INFRA_KEYWORDS):
        return "Docker / Infra"
    if any(keyword in text for keyword in MODEL_KEYWORDS):
        return "Local Model"
    if any(keyword in text for keyword in IDE_KEYWORDS):
        return "IDE"
    if any(keyword in text for keyword in BROWSER_KEYWORDS):
        return "Browser Heavy"
    if any(keyword in text for keyword in BUILD_KEYWORDS):
        return "Compile / Build"

    return "Other"


def infer_workload(processes: list[dict]) -> str:
    groups: dict[str, float] = {}
    for process in processes:
        group = process.get("app_group") or "Other"
        weight = float(process.get("cpu_percent") or 0) + float(process.get("memory_mb") or 0) / 1024
        groups[group] = groups.get(group, 0.0) + weight

    if not groups:
        return "unknown"

    top_group = max(groups, key=groups.get)
    mapping = {
        "Agent Coding": "agent_coding",
        "Local Model": "local_model",
        "Video Editing": "video_editing",
        "Browser Heavy": "browser_heavy",
        "Compile / Build": "compile_build",
        "Docker / Infra": "docker_infra",
        "IDE": "agent_coding",
    }
    return mapping.get(top_group, "general")

