# FraudGuard AI: Enterprise Real-Time Credit Card Fraud Detection Platform

[![CI Backend](https://github.com/fraudguard/fraudguard-ai/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/fraudguard/fraudguard-ai/actions)
[![CI Frontend](https://github.com/fraudguard/fraudguard-ai/actions/workflows/ci-frontend.yml/badge.svg)](https://github.com/fraudguard/fraudguard-ai/actions)
[![ML Benchmarks](https://github.com/fraudguard/fraudguard-ai/actions/workflows/ml-model-benchmark.yml/badge.svg)](https://github.com/fraudguard/fraudguard-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js: 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)

**FraudGuard AI** is a production-grade, distributed Credit Card Fraud Detection and Prevention Engine engineered to process high-throughput financial transactions with sub-20ms latency. The system combines multi-model ensemble machine learning (XGBoost, LightGBM, CatBoost, Deep Autoencoders), dynamic AST-based business rules, graph network analytics, explainable AI (SHAP/LIME), real-time WebSocket threat monitoring, and an enterprise case management suite.

---

## Key Features

- **Multi-Model Intelligence Layer**:
  - Supervised ensemble (XGBoost, LightGBM, CatBoost, Balanced Random Forest).
  - Unsupervised anomaly detection (PyTorch Autoencoders, Isolation Forests, LOF).
  - Bipartite graph network analytics for fraud syndicate and device fingerprint ring detection.
  - Population Stability Index (PSI) & Kolmogorov-Smirnov continuous concept drift detection.
  - Explainable AI (XAI) with TreeSHAP, KernelSHAP, LIME, and counterfactual generation.
- **Ultra-Low Latency Decision Engine**:
  - FastAPI asynchronous server delivering sub-20ms p99 inference.
  - Dynamic AST-based rule engine with zero-downtime hot reloading.
  - Real-time sliding window velocity counters and in-memory feature caching.
- **Analyst Investigation Workbench**:
  - Modern Next.js 14 / React 18 / TypeScript frontend with Tailwind CSS.
  - Real-time WebSocket streaming feed with live risk scoring.
  - Deep-dive case management with evidence locker and chargeback dispute workflows.
  - Interactive SHAP waterfall plots and decision boundary visualizers.
  - Visual rule studio with historical backtesting simulator.
- **Attack Simulation & Stress Testing**:
  - Built-in transaction streaming engine with Poisson process arrival distributions.
  - Pre-configured attack injectors (Card Testing, Impossible Travel, Account Takeover, Bust-out).

---

## System Architecture

```
[ Financial Ingestion Gateway ]
             │
             ▼
[ Real-Time Feature Store (Redis / In-Memory) ]
             │
             ├──► [ Dynamic AST Rule Engine ] ────────┐
             │                                        │
             └──► [ ML Ensemble (XGB+LGBM+Cat+AE) ] ──┴─► [ Decision Orchestrator (<20ms) ]
                                                                      │
                         ┌────────────────────────────────────────────┴──────────────────────┐
                         ▼                                                                   ▼
           [ Database & Case Management ]                                    [ Real-Time WebSocket Push ]
                         │                                                                   │
                         ▼                                                                   ▼
       [ Analyst Investigation Portal ]                                     [ Live Threat Radar & UI ]
```

---

## Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/your-username/fraudguard-ai.git
cd fraudguard-ai

# Start all services (Backend, Frontend, Redis, Simulator)
docker compose up --build
```

Access the services:
- **Analyst Dashboard**: `http://localhost:3000`
- **FastAPI API & OpenAPI Docs**: `http://localhost:8000/docs`
- **Metrics & Health**: `http://localhost:8000/api/v1/health`

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
