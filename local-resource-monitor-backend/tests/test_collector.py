import unittest

from resource_monitor_backend.collector import BYTES_PER_GB, ResourceCollector


class CollectorMemoryTest(unittest.TestCase):
    def test_vm_stat_memory_counts_file_backed_cache_as_available(self):
        collector = ResourceCollector()
        page_size = 16 * 1024
        total_bytes = 48 * BYTES_PER_GB
        pages_per_gb = BYTES_PER_GB // page_size

        collector._read_sysctl_int = lambda _name: total_bytes
        collector._read_vm_stat = lambda: {
            "page_size": page_size,
            "Pages free": int(0.8 * pages_per_gb),
            "Pages speculative": int(0.2 * pages_per_gb),
            "Pages wired down": int(4.5 * pages_per_gb),
            "Pages occupied by compressor": int(20 * pages_per_gb),
            "File-backed pages": int(8 * pages_per_gb),
        }
        collector._read_swap_usage = lambda: {
            "used_gb": 0.0,
            "total_gb": 0.0,
            "percent": None,
        }

        memory = collector._collect_memory_with_vm_stat(memory_pressure_free_percent=46)

        self.assertEqual(memory["physical_gb"], 48.0)
        self.assertAlmostEqual(memory["available_gb"], 9.0, places=1)
        self.assertAlmostEqual(memory["used_gb"], 39.0, places=1)
        self.assertEqual(memory["pressure"], "green")


if __name__ == "__main__":
    unittest.main()
