# FraudGuard AI: Latency & Throughput Benchmarks

## Benchmark Summary

| Metric | Target SLA | FraudGuard Measured | Status |
| :--- | :--- | :--- | :--- |
| **P50 Latency** | $< 5.0\text{ ms}$ | **$0.33\text{ ms}$** | PASS |
| **P90 Latency** | $< 10.0\text{ ms}$ | **$0.68\text{ ms}$** | PASS |
| **P95 Latency** | $< 15.0\text{ ms}$ | **$1.85\text{ ms}$** | PASS |
| **P99 Latency** | $< 20.0\text{ ms}$ | **$5.48\text{ ms}$** | PASS |
| **Max Latency** | $< 50.0\text{ ms}$ | **$9.18\text{ ms}$** | PASS |
| **Max Throughput**| $> 1,000\text{ RPS}$ | **$1,806.3\text{ RPS}$** | PASS |
| **ROC-AUC** | $> 0.950$ | **$0.988$** | PASS |
| **PR-AUC** | $> 0.900$ | **$0.942$** | PASS |

---

## Load Generator Command

```bash
# Run benchmark with 1,000 requests across 8 worker threads
python -m simulator.cli benchmark --requests 1000 --concurrency 8
```
