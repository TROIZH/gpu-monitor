import unittest

from resource_monitor_backend.analyzer import BottleneckAnalyzer
from resource_monitor_backend.settings import MonitorSettings


def base_metrics() -> dict:
    return {
        "timestamp": "2026-06-12T00:00:00Z",
        "workload_hint": "agent_coding",
        "cpu": {
            "available": True,
            "total_percent": 20,
            "cores": [20, 18, 10, 8],
            "logical_cores": 4,
        },
        "gpu": {"available": False},
        "memory": {
            "available": True,
            "pressure": "green",
            "percent": 50,
            "swap_gb": 0.2,
        },
        "storage": {
            "available": True,
            "free_percent": 60,
            "free_gb": 300,
        },
        "thermal": {
            "available": True,
            "state": "nominal",
        },
    }


class AnalyzerTest(unittest.TestCase):
    def test_normal_event_when_no_rules_trigger(self):
        analyzer = BottleneckAnalyzer(MonitorSettings())
        event = analyzer.analyze_current(base_metrics(), [])

        self.assertEqual(event["type"], "normal")
        self.assertEqual(event["primary_type"], "normal")
        self.assertIn("当前没有检测到明确硬件瓶颈", event["summary"])

    def test_detects_ram_bound_with_evidence_and_recommendation(self):
        metrics = base_metrics()
        metrics["memory"]["pressure"] = "yellow"
        metrics["memory"]["percent"] = 88
        metrics["memory"]["swap_gb"] = 3.4
        processes = [
            {"process_name": "Codex", "app_group": "Agent Coding", "memory_mb": 2048, "cpu_percent": 8},
            {"process_name": "Chrome", "app_group": "Browser Heavy", "memory_mb": 1600, "cpu_percent": 5},
        ]

        analyzer = BottleneckAnalyzer(MonitorSettings())
        event = analyzer.analyze_current(metrics, processes)

        self.assertEqual(event["type"], "ram_bound")
        self.assertEqual(event["primary_type"], "ram_bound")
        self.assertEqual(event["severity"], "high")
        self.assertTrue(any("swap_used_gb" in item for item in event["evidence"]))
        self.assertTrue(any("32GB RAM" in item for item in event["recommendations"]))

    def test_detects_mixed_cpu_and_storage_bound(self):
        metrics = base_metrics()
        metrics["cpu"]["total_percent"] = 92
        metrics["storage"]["free_percent"] = 4.8
        metrics["storage"]["free_gb"] = 21

        analyzer = BottleneckAnalyzer(MonitorSettings())
        event = analyzer.analyze_current(metrics, [])

        self.assertEqual(event["type"], "mixed_bound")
        self.assertIn(event["primary_type"], {"cpu_bound", "storage_bound"})
        self.assertIn("cpu_bound", [event["primary_type"], *event["secondary_types"]])
        self.assertIn("storage_bound", [event["primary_type"], *event["secondary_types"]])

    def test_upgrade_recommendation_prefers_ram_for_memory_profile(self):
        analyzer = BottleneckAnalyzer(MonitorSettings())
        profile = {
            "device_fit_score": 58,
            "bottleneck_counts": {"ram_bound": 6, "cpu_bound": 1},
            "summary": "你的主要压力来自内存。",
        }
        latest_event = {
            "primary_type": "ram_bound",
            "evidence": ["memory_pressure = yellow", "swap_used_gb = 3.4"],
        }

        recommendation = analyzer.build_upgrade_recommendation(profile, latest_event)

        self.assertEqual(recommendation["primary_upgrade_axis"], "ram")
        self.assertEqual(recommendation["confidence"], "high")
        self.assertTrue(any("memory_pressure" in item for item in recommendation["evidence"]))


if __name__ == "__main__":
    unittest.main()
