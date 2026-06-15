import tempfile
import unittest

from resource_monitor_backend.store import ResourceStore


class StoreTest(unittest.TestCase):
    def test_store_saves_and_reads_latest_sample_and_event(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResourceStore(f"{tmpdir}/monitor.sqlite3")
            metrics = {"timestamp": "2026-06-12T00:00:00Z", "cpu": {"total_percent": 20}}
            processes = [{"pid": 1, "process_name": "Codex", "cpu_percent": 10}]
            event = {"timestamp": "2026-06-12T00:00:00Z", "type": "normal", "severity": "normal"}

            store.save_sample(metrics, processes, event)

            self.assertEqual(store.get_latest_metric()["cpu"]["total_percent"], 20)
            self.assertEqual(store.get_latest_processes()[0]["process_name"], "Codex")
            self.assertEqual(store.get_latest_event()["type"], "normal")

    def test_store_history_filters_recent_rows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResourceStore(f"{tmpdir}/monitor.sqlite3")
            old_metrics = {"timestamp": "2020-01-01T00:00:00Z", "cpu": {"total_percent": 99}}
            new_metrics = {"timestamp": "2026-06-12T00:00:00Z", "cpu": {"total_percent": 20}}
            event = {"timestamp": "2026-06-12T00:00:00Z", "type": "normal", "severity": "normal"}

            store.save_sample(old_metrics, [], event)
            store.save_sample(new_metrics, [], event)

            history = store.get_metrics_history("3650d")

            self.assertGreaterEqual(len(history), 1)
            self.assertTrue(any(item["cpu"]["total_percent"] == 20 for item in history))


if __name__ == "__main__":
    unittest.main()
