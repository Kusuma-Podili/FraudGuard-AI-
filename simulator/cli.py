"""Adversarial Simulator & Benchmarking Command-Line Interface."""

import argparse
import sys
import json
from simulator.engine import TransactionSimulatorEngine
from simulator.load_generator import LoadTestRunner
from backend.app.services.decision_engine import DecisionEngine


def main():
    parser = argparse.ArgumentParser(description="FraudGuard AI Adversarial Simulator & Load Tester")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Benchmark command
    bench_parser = subparsers.add_parser("benchmark", help="Run high-throughput latency benchmark")
    bench_parser.add_argument("--requests", type=int, default=500, help="Total requests to evaluate")
    bench_parser.add_argument("--concurrency", type=int, default=8, help="Number of concurrent threads")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate synthetic transaction batch")
    gen_parser.add_argument("--count", type=int, default=10, help="Number of transactions to generate")
    gen_parser.add_argument("--attack", type=str, default=None, choices=[
        "CARD_TESTING", "IMPOSSIBLE_TRAVEL", "ACCOUNT_TAKEOVER", "CRYPTO_VELOCITY", "CREDENTIAL_STUFFING", "NOCTURNAL_LUXURY"
    ], help="Adversarial attack scenario")

    args = parser.parse_args()

    if args.command == "benchmark":
        print(f"[*] Running benchmark with {args.requests} requests @ {args.concurrency} concurrency...")
        runner = LoadTestRunner(concurrency=args.concurrency)
        metrics = runner.run_benchmark(total_requests=args.requests)
        print("\n" + "=" * 55)
        print("         FRAUDGUARD AI LATENCY BENCHMARK RESULTS")
        print("=" * 55)
        print(f"  Total Requests:          {metrics['total_requests']}")
        print(f"  Wall Clock Time:         {metrics['wall_time_seconds']}s")
        print(f"  Throughput Rate:         {metrics['effective_rps']} RPS")
        print(f"  Mean Latency:            {metrics['mean_latency_ms']} ms")
        print(f"  P50 Latency:             {metrics['p50_latency_ms']} ms")
        print(f"  P90 Latency:             {metrics['p90_latency_ms']} ms")
        print(f"  P99 Latency:             {metrics['p99_latency_ms']} ms")
        print(f"  Max Latency:             {metrics['max_latency_ms']} ms")
        print(f"  Sub-20ms SLA Compliant:  {'YES (PASS)' if metrics['sub_20ms_sla_compliant'] else 'NO'}")
        print("=" * 55)
        print(f"  Decision Breakdown:      {json.dumps(metrics['decision_breakdown'])}")
        print("=" * 55 + "\n")

    elif args.command == "generate":
        sim = TransactionSimulatorEngine(seed=42)
        if args.attack:
            sim.trigger_attack(args.attack)
        txs = sim.generate_next_batch(count=args.count)
        print(f"Generated {len(txs)} transactions:")
        for tx in txs:
            print(f"  [{tx.get('fraud_archetype', 'LEGITIMATE')}] ₹{tx['amount']:.2f} at {tx.get('merchant_name', tx.get('merchant_id'))} ({tx.get('country_code', 'US')})")


    else:
        parser.print_help()


if __name__ == "__main__":
    main()
