"""Unit tests for Population Stability Index (PSI) and Drift Detection."""

import unittest
import numpy as np

from ml_engine.monitoring.drift_detector import DriftDetector


class TestDriftDetection(unittest.TestCase):

    def test_no_drift_identical_distributions(self):
        rng = np.random.default_rng(42)
        base = rng.normal(0, 1, size=(1000, 3))
        curr = rng.normal(0, 1, size=(1000, 3))

        detector = DriftDetector(baseline_data=base, feature_names=["f1", "f2", "f3"])
        report = detector.evaluate_drift(curr)
        self.assertEqual(report.overall_drift_status, "NO_DRIFT")
        self.assertFalse(report.retraining_recommended)

    def test_severe_drift_shifted_distribution(self):
        np.random.seed(42)
        base = np.random.normal(0, 1, size=(200, 3))
        # Severe shift in mean and variance
        curr = np.random.normal(5.0, 3.0, size=(200, 3))

        detector = DriftDetector(baseline_data=base, feature_names=["f1", "f2", "f3"])
        report = detector.evaluate_drift(curr)
        self.assertIn(report.overall_drift_status, ["WARNING", "CRITICAL"])
        self.assertGreater(report.drifted_features_count, 0)


if __name__ == "__main__":
    unittest.main()
