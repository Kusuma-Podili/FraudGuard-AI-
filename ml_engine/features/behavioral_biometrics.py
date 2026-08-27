"""Behavioral Biometrics Feature Extraction & User Dynamics Engine.

Extracts dynamic continuous biometric features from:
- Keystroke dynamics (flight time, dwell time, typing cadence entropy)
- Mouse trajectory movement (velocity jitter, curvature, angular acceleration)
- Mobile touch dynamics (swipe angle, touch contact area, pressure variance)
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class BiometricDynamicsVector:
    mean_dwell_time_ms: float
    mean_flight_time_ms: float
    keystroke_jitter_ms: float
    mouse_velocity_px_ms: float
    mouse_trajectory_curvature: float
    touch_pressure_variance: float
    bot_heuristic_score: float  # 0.0 (Human) to 1.0 (Script/Bot)


class BehavioralBiometricsExtractor:
    """Extracts continuous behavioral biometrics from raw client interaction events."""

    def extract_keystroke_features(self, keydown_events: List[Dict[str, float]], keyup_events: List[Dict[str, float]]) -> Tuple[float, float, float]:
        """Compute dwell time (press duration) and flight time (inter-key latency)."""
        if not keydown_events or not keyup_events:
            return 85.0, 120.0, 15.0

        dwell_times = []
        for kd in keydown_events:
            matching_ku = [ku for ku in keyup_events if ku.get("key") == kd.get("key") and ku.get("t", 0) >= kd.get("t", 0)]
            if matching_ku:
                dwell_times.append(matching_ku[0]["t"] - kd["t"])

        flight_times = []
        for i in range(1, len(keydown_events)):
            flight_times.append(keydown_events[i]["t"] - keydown_events[i - 1]["t"])

        mean_dwell = float(np.mean(dwell_times)) if dwell_times else 85.0
        mean_flight = float(np.mean(flight_times)) if flight_times else 120.0
        jitter = float(np.std(flight_times)) if flight_times else 15.0

        return mean_dwell, mean_flight, jitter

    def extract_mouse_trajectory_features(self, mouse_points: List[Tuple[float, float, float]]) -> Tuple[float, float]:
        """Compute average velocity and curvature from (x, y, timestamp_ms) coordinates."""
        if len(mouse_points) < 3:
            return 1.2, 0.05

        velocities = []
        curvatures = []

        for i in range(1, len(mouse_points)):
            x0, y0, t0 = mouse_points[i - 1]
            x1, y1, t1 = mouse_points[i]
            dt = max(1.0, t1 - t0)
            dist = math.hypot(x1 - x0, y1 - y0)
            velocities.append(dist / dt)

        for i in range(1, len(mouse_points) - 1):
            x0, y0, _ = mouse_points[i - 1]
            x1, y1, _ = mouse_points[i]
            x2, y2, _ = mouse_points[i + 1]

            # Angular deviation
            v1 = (x1 - x0, y1 - y0)
            v2 = (x2 - x1, y2 - y1)
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            m1 = math.hypot(*v1)
            m2 = math.hypot(*v2)
            if m1 > 0 and m2 > 0:
                cos_theta = max(-1.0, min(1.0, dot / (m1 * m2)))
                curvatures.append(math.acos(cos_theta))

        mean_vel = float(np.mean(velocities)) if velocities else 1.0
        mean_curv = float(np.mean(curvatures)) if curvatures else 0.05
        return mean_vel, mean_curv

    def compute_bot_probability(self, mean_flight: float, jitter: float, curvature: float) -> float:
        """Heuristic bot score: zero jitter and linear mouse paths indicate automated Selenium/Puppeteer scripts."""
        bot_score = 0.0
        if jitter < 2.0:  # Perfectly robotic keystroke timing
            bot_score += 0.60
        if curvature < 0.005:  # Perfectly straight synthetic mouse movement
            bot_score += 0.35
        return min(1.0, bot_score)
