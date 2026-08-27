# FraudGuard AI: Enterprise System Architecture

FraudGuard AI is an enterprise-grade real-time credit card fraud detection and risk intelligence platform engineered for sub-20ms P99 inference latency, high throughput (2,000+ RPS), multi-model ensemble detection, and complete explainability under Fair Credit Reporting Act (FCRA) compliance.

---

## 1. High-Level Architecture Diagram

```mermaid
flowchart TD
    subgraph Ingestion["1. Multi-Channel Authorization Ingestion"]
        POS["POS Terminals (EMV/Magstripe)"]
        CNP["E-Commerce CNP Gateways"]
        ATM["ATM Cash Machines"]
        SIM["Adversarial Stream Simulator"]
    end

    subgraph Gateway["2. Real-Time Decision Gateway (FastAPI / Sub-20ms)"]
        Ingress["POST /api/v1/transactions/score"]
        Preproc["Real-Time Feature Enrichment Engine"]
        GeoEngine["Haversine / Vincenty Geodesic Distance"]
        VelocityEngine["Sliding Window Ring Buffers (5m, 1h, 6h, 24h, 7d)"]
        Rules["AST Safe Rule Evaluator (Microsecond Hot Path)"]
    end

    subgraph Ensemble["3. Hybrid Machine Learning Ensemble Subsystem"]
        XGB["XGBoost (Focal Loss & Dynamic Scale-Pos-Weight)"]
        LGBM["LightGBM (Leaf-Wise Histogram Gradient Booster)"]
        CB["CatBoost (Oblivious Symmetric Decision Trees)"]
        RF["Balanced Random Forest (Stratified Under-Sampling)"]
        AE["Deep Autoencoder (Reconstruction Error Anomaly)"]
        IF["Isolation Forest (Subsampling Path Length)"]
        Graph["Fraud Graph Network (Bipartite Ring Detector)"]
        Meta["Meta-Ensemble Calibrator & Decision Arbitrator"]
    end

    subgraph Explainability["4. Explainable AI & Governance Subsystem"]
        SHAP["TreeSHAP Waterfall Attribution"]
        LIME["Local Interpretable Surrogate (LIME)"]
        CF["Counterfactual Adverse Action Generator (FCRA)"]
        Drift["Population Stability Index (PSI) & 2-Sample KS Drift"]
    end

    subgraph Output["5. Operations, Storage & Workbench"]
        DB[(SQLite / PostgreSQL Immutable Ledger)]
        WS["WebSocket Broadcast Hub"]
        Triage["Automated Case Triage & SLA Engine"]
        UI["Next.js 14 Fraud Analyst Dashboard"]
    end

    POS --> Ingress
    CNP --> Ingress
    ATM --> Ingress
    SIM --> Ingress

    Ingress --> Preproc
    Preproc --> GeoEngine
    Preproc --> VelocityEngine
    GeoEngine --> Rules
    VelocityEngine --> Rules

    Rules --> Ensemble
    Ensemble --> XGB & LGBM & CB & RF & AE & IF & Graph
    XGB & LGBM & CB & RF & AE & IF & Graph --> Meta

    Meta --> Output
    Meta --> Explainability
    Explainability --> Triage
    Output --> DB
    Output --> WS
    WS --> UI
    Triage --> UI
```

---

## 2. Core Architectural Subsystems

### 2.1 Low-Latency Ingestion & Feature Store
- **Sliding-Window Velocity Engine**: Employs in-memory ring buffers across 5 temporal windows ($5\text{ min}$, $1\text{ hr}$, $6\text{ hrs}$, $24\text{ hrs}$, $7\text{ days}$). Tracks rolling transaction frequencies, velocity sums, distinct device count, and rapid IP rotation without incurring database I/O bottlenecks.
- **Geodesic Anomaly Detection**: Calculates great-circle Haversine and ellipsoidal Vincenty distances between authorization latitude/longitude coordinates and the cardholder's home address, flagging physical impossibility speeds ($>900\text{ km/h}$).
- **Categorical & Cyclical Encoders**: Converts transaction timestamps into periodic sine/cosine cyclical embeddings ($\sin(2\pi t/24)$, $\cos(2\pi t/24)$) and calculates Weight of Evidence (WoE) and empirical Bayes Target Encoding for merchant categories.

### 2.2 Microsecond Abstract Syntax Tree (AST) Rule Engine
- Evaluates dynamically compiled business rules in safe Python AST expression trees (`ast.parse`) without unsafe `eval()` executions.
- Sub-50 microsecond execution time per rule.
- Gating dispositions: `ALLOW`, `REVIEW`, `CHALLENGE_3DS`, `DECLINE`.

### 2.3 Hybrid Machine Learning Ensemble
1. **XGBoost Fraud Classifier**: Optimized tree-depth with focal loss penalty on false positives.
2. **LightGBM Classifier**: Fast leaf-wise histogram tree construction with $L_1/L_2$ regularization.
3. **CatBoost Classifier**: Oblivious symmetric decision trees preventing catastrophic overfitting on rare cardholder features.
4. **Balanced Random Forest**: Stratified majority under-sampling to counteract $1:200$ fraud class imbalances.
5. **Deep Autoencoder Anomaly Detector**: Unsupervised reconstruction error ($MSE$) mapping unobserved novel fraud zero-days.
6. **Isolation Forest**: Sub-sampled binary tree path-length isolation scores.
7. **Graph Syndicate Detector**: Bipartite projection graph identifying coordinated credential/device rings across multiple cardholders.

### 2.4 Explainable AI (XAI) & Regulatory Compliance
- **TreeSHAP Attributions**: Exact Shapley value attributions for each feature on every individual authorization.
- **Counterfactual Generator**: Computes minimum-distance actionable changes for adverse action reporting under the Fair Credit Reporting Act (FCRA).
- **Drift Monitoring**: Evaluates continuous Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) two-sample divergence against production baselines.
