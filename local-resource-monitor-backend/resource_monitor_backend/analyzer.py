from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .settings import MonitorSettings
from .timeutils import utc_now_iso


@dataclass
class BottleneckRuleResult:
    type: str
    severity: str
    confidence: float
    summary: str
    evidence: list[str]
    recommendations: list[str]


class BottleneckAnalyzer:
    def __init__(self, settings: MonitorSettings | None = None):
        self.settings = settings or MonitorSettings()

    def analyze_current(self, metrics: dict[str, Any], processes: list[dict[str, Any]]) -> dict[str, Any]:
        rule_results: list[BottleneckRuleResult] = []
        rule_results.extend(self._analyze_cpu(metrics))
        rule_results.extend(self._analyze_memory(metrics, processes))
        rule_results.extend(self._analyze_storage(metrics))
        rule_results.extend(self._analyze_thermal(metrics))
        rule_results.extend(self._analyze_gpu(metrics))

        if not rule_results:
            return self._normal_event(metrics, processes)

        primary = self._choose_primary(rule_results)
        mixed_types = [result.type for result in rule_results if result.type != primary.type]
        event_type = "mixed_bound" if len(rule_results) > 1 else primary.type

        summary = primary.summary
        if mixed_types:
            readable = ", ".join(sorted(set(mixed_types)))
            summary = f"{primary.summary} 同时检测到其他压力：{readable}。"

        evidence = []
        recommendations = []
        for result in sorted(rule_results, key=lambda item: item.confidence, reverse=True):
            evidence.extend(result.evidence)
            recommendations.extend(result.recommendations)

        return {
            "id": f"event-{metrics.get('timestamp', utc_now_iso())}",
            "timestamp": metrics.get("timestamp") or utc_now_iso(),
            "start_time": metrics.get("timestamp") or utc_now_iso(),
            "end_time": None,
            "type": event_type,
            "primary_type": primary.type,
            "secondary_types": sorted(set(mixed_types)),
            "severity": self._max_severity(rule_results),
            "confidence": round(max(result.confidence for result in rule_results), 2),
            "summary": summary,
            "evidence": self._dedupe(evidence)[:8],
            "recommendations": self._dedupe(recommendations)[:5],
            "workload_hint": metrics.get("workload_hint") or "unknown",
        }

    def build_profile(self, events: list[dict[str, Any]], metrics: list[dict[str, Any]], processes: list[dict[str, Any]]) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for event in events:
            event_type = event.get("primary_type") or event.get("type") or "normal"
            counts[event_type] = counts.get(event_type, 0) + 1
        bottleneck_event_count = sum(
            count for event_type, count in counts.items() if event_type != "normal"
        )

        primary_type = max(counts, key=counts.get) if counts else "normal"
        user_type = self._map_user_type(primary_type, processes)
        device_fit_score = self._device_fit_score(counts)
        top_apps = self._top_apps(processes)

        summary = self._profile_summary(user_type, primary_type, device_fit_score)
        return {
            "period": "current",
            "generated_at": utc_now_iso(),
            "primary_user_type": user_type,
            "secondary_user_type": self._secondary_user_type(processes),
            "device_fit_score": device_fit_score,
            "bottleneck_counts": counts,
            "sample_count": len(metrics),
            "event_count": len(events),
            "bottleneck_event_count": bottleneck_event_count,
            "top_apps": top_apps,
            "hourly_bottlenecks": self._hourly_bottlenecks(events),
            "summary": summary,
        }

    def build_upgrade_recommendation(self, profile: dict[str, Any], latest_event: dict[str, Any] | None) -> dict[str, Any]:
        primary_type = latest_event.get("primary_type") if latest_event else None
        if not primary_type or primary_type == "normal":
            primary_type = self._primary_from_profile(profile)

        axis_map = {
            "ram_bound": ("ram", "下一台设备优先选择更大内存。Agent、多浏览器标签页、本地模型都会放大 RAM 压力。"),
            "cpu_bound": ("cpu", "下一台设备优先考虑更强 CPU 和更多性能核心，尤其适合编译、测试和多任务场景。"),
            "single_core_bound": ("cpu_single_core", "优先关注单核性能；当前瓶颈可能来自单线程任务。"),
            "gpu_bound": ("gpu", "优先关注 GPU/统一内存或云端 GPU；适合本地模型、视频导出和图形任务。"),
            "storage_bound": ("storage", "优先增加 SSD 容量并保留足够剩余空间；swap 和缓存会放大磁盘压力。"),
            "thermal_bound": ("thermal", "优先考虑有主动散热的设备，或降低持续并发负载。"),
            "mixed_bound": ("balanced", "当前是混合瓶颈，建议优先处理证据最多的 RAM/CPU/散热问题。"),
        }
        axis, recommendation = axis_map.get(primary_type, ("none", "当前没有足够证据建议升级，先继续观察。"))

        confidence = "high" if profile.get("device_fit_score", 100) < 65 else "medium"
        if axis == "none":
            confidence = "low"

        evidence = []
        if latest_event:
            evidence.extend(latest_event.get("evidence") or [])
        if profile.get("summary"):
            evidence.append(profile["summary"])

        return {
            "generated_at": utc_now_iso(),
            "primary_upgrade_axis": axis,
            "secondary_upgrade_axis": self._secondary_axis(profile, exclude_axis=axis),
            "recommendation": recommendation,
            "confidence": confidence,
            "evidence": self._dedupe(evidence)[:6],
            "not_recommended": self._not_recommended(axis),
            "network_search_enabled": self.settings.enable_network_recommendations,
        }

    def _analyze_cpu(self, metrics: dict[str, Any]) -> list[BottleneckRuleResult]:
        cpu = metrics.get("cpu") or {}
        if not cpu.get("available"):
            return []

        results: list[BottleneckRuleResult] = []
        total = float(cpu.get("total_percent") or 0)
        cores = [float(value) for value in cpu.get("cores") or []]
        hot_cores = [index for index, value in enumerate(cores) if value >= self.settings.cpu_core_bound_percent]

        if total >= self.settings.cpu_bound_percent:
            results.append(
                BottleneckRuleResult(
                    type="cpu_bound",
                    severity="high" if total >= 95 else "medium",
                    confidence=min(0.95, total / 100),
                    summary="CPU 正在成为主要瓶颈，多任务或构建任务可能导致卡顿。",
                    evidence=[
                        f"CPU total_percent = {total:.1f}%",
                        f"logical_cores = {cpu.get('logical_cores')}",
                    ],
                    recommendations=[
                        "减少并行构建、测试或 Agent 会话数量。",
                        "如果这种情况经常出现在编译/测试场景，下一台设备优先考虑更多性能核心。",
                    ],
                )
            )

        if hot_cores and total < self.settings.cpu_bound_percent:
            results.append(
                BottleneckRuleResult(
                    type="single_core_bound",
                    severity="medium",
                    confidence=0.78,
                    summary="检测到单核心压力过高，可能是某个单线程任务拖慢体验。",
                    evidence=[f"hot_core_indexes = {hot_cores[:6]}", f"CPU total_percent = {total:.1f}%"],
                    recommendations=[
                        "检查 top CPU 进程，优先处理单个高占用进程。",
                        "如果常见于某个开发工具，优先升级单核性能更强的设备。",
                    ],
                )
            )

        return results

    def _analyze_memory(self, metrics: dict[str, Any], processes: list[dict[str, Any]]) -> list[BottleneckRuleResult]:
        memory = metrics.get("memory") or {}
        if not memory.get("available") and memory.get("pressure") == "unknown":
            return []

        pressure = memory.get("pressure")
        used_percent = float(memory.get("percent") or 0)
        swap_gb = float(memory.get("swap_gb") or 0)
        is_pressure = pressure in {"yellow", "red"}
        is_swap_warning = swap_gb >= self.settings.swap_warning_gb and used_percent >= self.settings.memory_pressure_yellow_percent

        if not is_pressure and not is_swap_warning:
            return []

        top_memory = sorted(processes, key=lambda item: float(item.get("memory_mb") or 0), reverse=True)[:3]
        process_names = ", ".join(process.get("process_name", "unknown") for process in top_memory)
        severity = "critical" if pressure == "red" or used_percent >= self.settings.memory_pressure_red_percent else "high"

        return [
            BottleneckRuleResult(
                type="ram_bound",
                severity=severity,
                confidence=0.9 if pressure == "red" else 0.82,
                summary="内存正在成为瓶颈，系统可能开始依赖 swap，交互会变慢。",
                evidence=[
                    f"memory_pressure = {pressure}",
                    f"memory_used_percent = {used_percent:.1f}%",
                    f"swap_used_gb = {swap_gb:.2f}",
                    f"top_memory_processes = {process_names}",
                ],
                recommendations=[
                    "暂停部分 Agent 会话或本地服务，优先关闭高内存浏览器标签页。",
                    "如果 RAM-bound 在一周内多次出现，下一台设备建议至少 32GB RAM。",
                    "本地模型场景频繁出现 RAM-bound 时，考虑 64GB+ 统一内存或云端推理。",
                ],
            )
        ]

    def _analyze_storage(self, metrics: dict[str, Any]) -> list[BottleneckRuleResult]:
        storage = metrics.get("storage") or {}
        if not storage.get("available"):
            return []

        free_percent = storage.get("free_percent")
        if free_percent is None or float(free_percent) >= self.settings.storage_low_free_percent:
            return []

        return [
            BottleneckRuleResult(
                type="storage_bound",
                severity="high" if float(free_percent) < 5 else "medium",
                confidence=0.8,
                summary="存储空间偏低，缓存、swap 和构建产物可能进一步拖慢系统。",
                evidence=[
                    f"storage_free_percent = {float(free_percent):.1f}%",
                    f"storage_free_gb = {storage.get('free_gb')}",
                ],
                recommendations=[
                    "清理构建产物、Docker 镜像、本地模型缓存和下载目录。",
                    "如果长期低于 10% 可用空间，下一台设备应选择更大 SSD。",
                ],
            )
        ]

    def _analyze_thermal(self, metrics: dict[str, Any]) -> list[BottleneckRuleResult]:
        thermal = metrics.get("thermal") or {}
        state = thermal.get("state")
        if state not in {"fair", "serious", "critical"}:
            return []

        return [
            BottleneckRuleResult(
                type="thermal_bound",
                severity="critical" if state == "critical" else "medium",
                confidence=0.72 if state == "fair" else 0.88,
                summary="设备出现热压力，持续负载下性能可能下降。",
                evidence=[f"thermal_state = {state}"],
                recommendations=[
                    "降低长时间并行任务数量，必要时接电并保持散热环境。",
                    "如果经常出现在 MacBook Air 等无风扇设备上，下一台设备建议考虑主动散热机型。",
                ],
            )
        ]

    def _analyze_gpu(self, metrics: dict[str, Any]) -> list[BottleneckRuleResult]:
        gpu = metrics.get("gpu") or {}
        if not gpu.get("available"):
            return []

        usage = gpu.get("usage_percent")
        if usage is None or float(usage) < 85:
            return []

        return [
            BottleneckRuleResult(
                type="gpu_bound",
                severity="high" if float(usage) >= 95 else "medium",
                confidence=0.8,
                summary="GPU 正在成为瓶颈，图形、本地模型或视频任务可能导致卡顿。",
                evidence=[f"gpu_usage_percent = {float(usage):.1f}%"],
                recommendations=[
                    "暂停视频导出、本地模型推理或图形密集任务。",
                    "如果 GPU-bound 高频，升级时优先关注 GPU/统一内存或云端 GPU。",
                ],
            )
        ]

    def _normal_event(self, metrics: dict[str, Any], processes: list[dict[str, Any]]) -> dict[str, Any]:
        cpu_total = (metrics.get("cpu") or {}).get("total_percent")
        memory_pressure = (metrics.get("memory") or {}).get("pressure")
        free_percent = (metrics.get("storage") or {}).get("free_percent")
        return {
            "id": f"event-{metrics.get('timestamp', utc_now_iso())}",
            "timestamp": metrics.get("timestamp") or utc_now_iso(),
            "start_time": metrics.get("timestamp") or utc_now_iso(),
            "end_time": None,
            "type": "normal",
            "primary_type": "normal",
            "secondary_types": [],
            "severity": "normal",
            "confidence": 0.7,
            "summary": "当前没有检测到明确硬件瓶颈。",
            "evidence": [
                f"CPU total_percent = {cpu_total}",
                f"memory_pressure = {memory_pressure}",
                f"storage_free_percent = {free_percent}",
            ],
            "recommendations": ["继续观察即可；当前没有足够证据建议升级。"],
            "workload_hint": metrics.get("workload_hint") or "unknown",
        }

    def _choose_primary(self, results: list[BottleneckRuleResult]) -> BottleneckRuleResult:
        severity_rank = {"normal": 0, "medium": 1, "high": 2, "critical": 3}
        return max(results, key=lambda item: (severity_rank.get(item.severity, 0), item.confidence))

    def _max_severity(self, results: list[BottleneckRuleResult]) -> str:
        severity_rank = {"normal": 0, "medium": 1, "high": 2, "critical": 3}
        return max((result.severity for result in results), key=lambda value: severity_rank.get(value, 0))

    def _dedupe(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for value in values:
            if value in seen:
                continue
            seen.add(value)
            deduped.append(value)
        return deduped

    def _map_user_type(self, primary_type: str, processes: list[dict[str, Any]]) -> str:
        if primary_type == "ram_bound":
            return "multi_agent_memory_bound" if self._has_agent_process(processes) else "memory_hungry"
        if primary_type == "cpu_bound":
            return "compile_build_or_multi_agent"
        if primary_type == "single_core_bound":
            return "single_thread_bound"
        if primary_type == "gpu_bound":
            return "local_model_or_creator"
        if primary_type == "storage_bound":
            return "storage_constrained"
        if primary_type == "thermal_bound":
            return "thermal_limited"
        return "lightweight_or_balanced"

    def _secondary_user_type(self, processes: list[dict[str, Any]]) -> str:
        groups: dict[str, int] = {}
        for process in processes:
            group = process.get("app_group") or "Other"
            groups[group] = groups.get(group, 0) + 1
        if not groups:
            return "unknown"
        return max(groups, key=groups.get).lower().replace(" / ", "_").replace(" ", "_")

    def _device_fit_score(self, counts: dict[str, int]) -> int:
        if not counts:
            return 90

        penalty = 0
        for event_type, count in counts.items():
            if event_type == "normal":
                continue
            penalty += min(count * 6, 30)
        return max(25, 100 - penalty)

    def _top_apps(self, processes: list[dict[str, Any]]) -> list[str]:
        ordered = sorted(
            processes,
            key=lambda item: float(item.get("cpu_percent") or 0) + float(item.get("memory_mb") or 0) / 512,
            reverse=True,
        )
        names: list[str] = []
        for process in ordered:
            name = process.get("process_name")
            if name and name not in names:
                names.append(name)
            if len(names) >= 5:
                break
        return names

    def _profile_summary(self, user_type: str, primary_type: str, score: int) -> str:
        if primary_type == "normal":
            return f"目前这台电脑基本够用，匹配度 {score}/100。"
        if primary_type == "ram_bound":
            return f"卡顿主要来自内存不够用，匹配度 {score}/100。AI 编程工具、浏览器标签页和本地模型同时运行时会更明显。"
        if primary_type == "cpu_bound":
            return f"主要压力来自 CPU 长时间高负载，匹配度 {score}/100。编译、测试和多任务并发时会更容易卡。"
        if primary_type == "single_core_bound":
            return f"主要压力来自某个任务长期占住单个核心，匹配度 {score}/100。单线程脚本或老项目更容易触发。"
        if primary_type == "gpu_bound":
            return f"主要压力来自图形或本地模型任务，匹配度 {score}/100。视频导出和本地推理同时运行时会更吃力。"
        if primary_type == "storage_bound":
            return f"主要压力来自可用磁盘空间偏低，匹配度 {score}/100。缓存、swap 和大型项目会放大卡顿。"
        if primary_type == "thermal_bound":
            return f"主要压力来自持续高负载和发热降速，匹配度 {score}/100。有主动散热的设备更适合这类工作流。"
        if primary_type == "mixed_bound":
            return f"这次不是单一问题，内存、CPU、存储或散热可能同时吃紧，匹配度 {score}/100。"
        return f"当前设备匹配度 {score}/100，建议继续观察几天后再判断是否升级。"

    def _primary_from_profile(self, profile: dict[str, Any]) -> str:
        counts = profile.get("bottleneck_counts") or {}
        if not counts:
            return "normal"
        return max(counts, key=counts.get)

    def _secondary_axis(self, profile: dict[str, Any], exclude_axis: str | None = None) -> str | None:
        counts = profile.get("bottleneck_counts") or {}
        ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        axis_map = {
            "ram_bound": "ram",
            "cpu_bound": "cpu",
            "single_core_bound": "cpu_single_core",
            "gpu_bound": "gpu",
            "storage_bound": "storage",
            "thermal_bound": "thermal",
        }
        axes = []
        for event_type, _ in ordered:
            axis = axis_map.get(event_type)
            if not axis or axis == exclude_axis or axis in axes:
                continue
            axes.append(axis)
        return axes[0] if axes else None

    def _hourly_bottlenecks(self, events: list[dict[str, Any]]) -> list[int]:
        counts = [0] * 24
        for event in events:
            event_type = event.get("primary_type") or event.get("type")
            if event_type in {None, "normal"}:
                continue
            timestamp = event.get("timestamp") or event.get("start_time")
            if not isinstance(timestamp, str):
                continue
            try:
                parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            counts[parsed.hour] += 1
        return counts

    def _not_recommended(self, axis: str) -> list[str]:
        if axis == "ram":
            return ["只升级存储容量但保持小内存。", "只看 CPU 分数而忽略统一内存容量。"]
        if axis == "thermal":
            return ["继续选择无主动散热设备承载长时间高负载。"]
        if axis == "storage":
            return ["继续把可用空间长期维持在 10% 以下。"]
        if axis == "none":
            return ["在没有长期瓶颈证据前盲目升级硬件。"]
        return ["只升级单一指标，忽略 RAM、散热和存储的组合瓶颈。"]

    def _has_agent_process(self, processes: list[dict[str, Any]]) -> bool:
        return any((process.get("app_group") or "") == "Agent Coding" for process in processes)
