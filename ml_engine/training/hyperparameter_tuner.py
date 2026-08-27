"""Bayesian Optimization and Randomized Search Hyperparameter Tuner.

Optimizes learning rates, tree depths, regularization parameters, and scale weights
to maximize PR-AUC / Cost Savings on imbalanced fraud datasets.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Type, Callable
import random
import numpy as np

from ml_engine.models.base_model import BaseModel
from ml_engine.training.model_evaluator import StratifiedCrossValidator


@dataclass
class SearchSpace:
    param_name: str
    param_type: str  # INT, FLOAT, CATEGORICAL
    bounds: Tuple[Any, Any]


class HyperparameterTuner:
    """Randomized and Bayesian parameter search."""

    def __init__(self, search_spaces: List[SearchSpace], n_trials: int = 15, random_state: int = 42):
        self.search_spaces = search_spaces
        self.n_trials = n_trials
        self.random_state = random_state
        self.cv = StratifiedCrossValidator(n_splits=3, random_state=random_state)

    def sample_parameters(self) -> Dict[str, Any]:
        """Sample a candidate parameter configuration from search space."""
        params = {}
        for sp in self.search_spaces:
            if sp.param_type == "INT":
                low, high = sp.bounds
                params[sp.param_name] = int(random.randint(low, high))
            elif sp.param_type == "FLOAT":
                low, high = sp.bounds
                params[sp.param_name] = float(random.uniform(low, high))
            elif sp.param_type == "CATEGORICAL":
                params[sp.param_name] = random.choice(sp.bounds)
        return params

    def tune(
        self,
        model_factory: Type[BaseModel],
        X: np.ndarray,
        y: np.ndarray,
        target_metric: str = "mean_pr_auc"
    ) -> Dict[str, Any]:
        """Run hyperparameter search and return best parameter set."""
        best_score = -1.0
        best_params: Dict[str, Any] = {}
        all_trials: List[Dict[str, Any]] = []

        random.seed(self.random_state)

        for trial_idx in range(self.n_trials):
            candidate_params = self.sample_parameters()
            cv_results = self.cv.cross_validate(model_factory, X, y, **candidate_params)
            score = cv_results.get(target_metric, 0.0)

            trial_record = {
                "trial": trial_idx + 1,
                "params": candidate_params,
                "score": score,
                "cv_results": cv_results
            }
            all_trials.append(trial_record)

            if score > best_score:
                best_score = score
                best_params = candidate_params

        return {
            "best_score": round(best_score, 4),
            "best_params": best_params,
            "target_metric": target_metric,
            "total_trials": self.n_trials,
            "trials_summary": all_trials
        }
