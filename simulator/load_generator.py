"""High-Concurrency Load Test Runner and Latency Benchmarker.

Simulates thousands of concurrent transaction evaluation requests against the decision engine
to measure P50, P90, P99, and Max latency SLA compliance (<20ms).
"""

from __future__ import annotations
import time
import numpy as np
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from backend.app.services.decision_engine import DecisionEngine
from simulator.engine import TransactionSimulatorEngine


class LoadTestRunner:
    """Runs stress tests and benchmarks decision gateway latency."""

    def __init__(self, concurrency: int = 10):
        self.concurrency = concurrency
        self.engine = DecisionEngine()
        self.simulator = TransactionSimulatorEngine(seed=999)

    def run_benchmark(self, total_requests: int = 1000) -> Dict[str, Any]:
        """Execute concurrent benchmark and record latency distribution."""
        transactions = self.simulator.generate_next_batch(count=total_requests)
        latencies_ms: List[float] = []
        actions_count: Dict[str, int] = {"ALLOW": 0, "REVIEW": 0, "CHALLENGE_3DS": 0, "DECLINE": 0}

        def _worker(tx: Dict[str, Any]) -> float:
            t0 = time.perf_counter()
            res = self.engine.evaluate_transaction(tx)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            act = res.get("decision_action", "ALLOW")
            actions_count[act] = actions_count.get(act, 0) + 1
            return elapsed_ms

        wall_start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            latencies_ms = list(executor.map(_worker, transactions))
        wall_elapsed = time.perf_counter() - wall_start

        latencies_arr = np.array(latencies_ms)
        effective_rps = total_requests / max(wall_elapsed, 0.001)

        return {
            "total_requests": total_requests,
            "concurrency": self.concurrency,
            "wall_time_seconds": round(wall_elapsed, 3),
            "effective_rps": round(effective_rps, 1),
            "p50_latency_ms": round(float(np.percentile(latencies_arr, 50)), 2),
            "p90_latency_ms": round(float(np.percentile(latencies_arr, 90)), 2),
            "p95_latency_ms": round(float(np.percentile(latencies_arr, 95)), 2),
            "p99_latency_ms": round(float(np.percentile(latencies_arr, 99)), 2),
            "max_latency_ms": round(float(np.max(latencies_arr)), 2),
            "mean_latency_ms": round(float(np.mean(latencies_arr)), 2),
            "sub_20ms_sla_compliant": bool(float(np.percentile(latencies_arr, 99)) < 20.0),
            "decision_breakdown": actions_count,
        }
