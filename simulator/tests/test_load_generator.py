"""Unit and benchmark tests for LoadTestRunner."""

import unittest
from simulator.load_generator import LoadTestRunner


class TestLoadGenerator(unittest.TestCase):

    def test_benchmark_execution(self):
        runner = LoadTestRunner(concurrency=4)
        metrics = runner.run_benchmark(total_requests=20)

        self.assertEqual(metrics["total_requests"], 20)
        self.assertEqual(metrics["concurrency"], 4)
        self.assertIn("p99_latency_ms", metrics)
        self.assertIn("effective_rps", metrics)
        self.assertGreater(metrics["effective_rps"], 0)
        self.assertIn("decision_breakdown", metrics)


if __name__ == "__main__":
    unittest.main()
