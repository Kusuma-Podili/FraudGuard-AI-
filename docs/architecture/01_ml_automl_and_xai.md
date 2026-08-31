# ML AutoML & Explainability (XAI) Architecture

## Overview
FraudGuard AI incorporates a zero-compromise tabular AutoML optimization engine alongside deep model explainability (XAI) attribution suites.

### Core Modules
1. **Automated Hyperparameter Optimization (`ml_engine/tabular_automl/optuna_hyperparam_search.py`)**:
   - Multi-objective Bayesian tuning optimizing Precision-Recall AUC under severe 0.17% class imbalance.
2. **Attribution Engines (`ml_engine/explainability/`)**:
   - **Integrated Gradients**: Path-integral gradient accumulation from neutral baselines.
   - **Layer-wise Relevance Propagation (LRP)**: Conservation property propagation through dense and convolutional layers.
   - **Fast TreeSHAP**: Exact polynomial-time Shapley value computation.
3. **Model Fairness Auditor (`ml_engine/advanced/fairness_auditor.py`)**:
   - Enforces ECOA 80% four-fifths rule and equalized odds across demographic protected attributes.
