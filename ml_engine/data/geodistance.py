"""Geographical distance and travel velocity calculations for fraud detection.

This module provides high-precision geodesic calculations to determine whether
consecutive transactions for a cardholder exhibit impossible physical travel speeds
(e.g., card present in London and 20 minutes later in Tokyo).
"""

from __future__ import annotations
import math
from datetime import datetime, timezone
from typing import Tuple, Optional, Dict, Any

EARTH_RADIUS_KM = 6371.0088
MAX_COMMERCIAL_FLIGHT_SPEED_KMH = 950.0  # Threshold above which travel without teleportation is impossible


def calculate_haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """Calculate the great-circle distance between two points on the Earth surface using Haversine formula.

    Args:
        lat1: Latitude of point 1 in degrees.
        lon1: Longitude of point 1 in degrees.
        lat2: Latitude of point 2 in degrees.
        lon2: Longitude of point 2 in degrees.

    Returns:
        Distance in kilometers (km).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clip to avoid domain errors due to floating-point rounding
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_KM * c


def calculate_vincenty_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    max_iterations: int = 200,
    tolerance: float = 1e-12
) -> float:
    """Calculate ellipsoidal geodesic distance using Vincenty's inverse formula.

    Falls back to Haversine if the algorithm does not converge (e.g. nearly antipodal points).

    Args:
        lat1: Latitude of point 1 in degrees.
        lon1: Longitude of point 1 in degrees.
        lat2: Latitude of point 2 in degrees.
        lon2: Longitude of point 2 in degrees.
        max_iterations: Maximum convergence iterations.
        tolerance: Convergence convergence tolerance.

    Returns:
        Distance in kilometers (km).
    """
    a = 6378137.0  # WGS-84 major axis in meters
    f = 1 / 298.257223563  # WGS-84 flattening
    b = (1 - f) * a

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    u1 = math.atan((1 - f) * math.tan(phi1))
    u2 = math.atan((1 - f) * math.tan(phi2))
    lon_diff = math.radians(lon2 - lon1)

    sin_u1, cos_u1 = math.sin(u1), math.cos(u1)
    sin_u2, cos_u2 = math.sin(u2), math.cos(u2)

    lambda_val = lon_diff
    for _ in range(max_iterations):
        sin_lambda = math.sin(lambda_val)
        cos_lambda = math.cos(lambda_val)

        sin_sigma = math.sqrt(
            (cos_u2 * sin_lambda) ** 2
            + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2
        )
        if sin_sigma == 0:
            return 0.0  # Coincident points

        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)

        sin_alpha = (cos_u1 * cos_u2 * sin_lambda) / sin_sigma
        cos_sq_alpha = 1 - sin_alpha**2

        if cos_sq_alpha != 0:
            cos2_sigma_m = cos_sigma - (2 * sin_u1 * sin_u2 / cos_sq_alpha)
        else:
            cos2_sigma_m = 0.0  # Equatorial line

        c_val = (f / 16) * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
        lambda_prev = lambda_val
        lambda_val = lon_diff + (1 - c_val) * f * sin_alpha * (
            sigma
            + c_val
            * sin_sigma
            * (
                cos2_sigma_m
                + c_val * cos_sigma * (-1 + 2 * cos2_sigma_m**2)
            )
        )

        if abs(lambda_val - lambda_prev) < tolerance:
            break
    else:
        # Fallback to Haversine on non-convergence
        return calculate_haversine_distance(lat1, lon1, lat2, lon2)

    u_sq = cos_sq_alpha * (a**2 - b**2) / (b**2)
    a_coef = 1 + (u_sq / 16384) * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    b_coef = (u_sq / 1024) * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))

    delta_sigma = (
        b_coef
        * sin_sigma
        * (
            cos2_sigma_m
            + (b_coef / 4)
            * (
                cos_sigma * (-1 + 2 * cos2_sigma_m**2)
                - (b_coef / 6)
                * cos2_sigma_m
                * (-3 + 4 * sin_sigma**2)
                * (-3 + 4 * cos2_sigma_m**2)
            )
        )
    )

    s = b * a_coef * (sigma - delta_sigma)
    return s / 1000.0  # Convert meters to kilometers


def calculate_travel_velocity(
    lat1: float,
    lon1: float,
    time1: datetime,
    lat2: float,
    lon2: float,
    time2: datetime
) -> Tuple[float, float, float]:
    """Calculate distance, elapsed time, and implied travel velocity between two points in time.

    Args:
        lat1: Latitude of first transaction.
        lon1: Longitude of first transaction.
        time1: Timestamp of first transaction.
        lat2: Latitude of second transaction.
        lon2: Longitude of second transaction.
        time2: Timestamp of second transaction.

    Returns:
        Tuple of (distance_km, elapsed_hours, velocity_kmh).
    """
    if time1.tzinfo is None:
        time1 = time1.replace(tzinfo=timezone.utc)
    if time2.tzinfo is None:
        time2 = time2.replace(tzinfo=timezone.utc)

    distance_km = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    elapsed_seconds = abs((time2 - time1).total_seconds())
    elapsed_hours = max(elapsed_seconds / 3600.0, 1.0 / 3600.0)  # Minimum 1 second

    velocity_kmh = distance_km / elapsed_hours
    return distance_km, elapsed_hours, velocity_kmh


def is_impossible_travel(
    lat1: float,
    lon1: float,
    time1: datetime,
    lat2: float,
    lon2: float,
    time2: datetime,
    max_kmh: float = MAX_COMMERCIAL_FLIGHT_SPEED_KMH,
    min_distance_threshold_km: float = 50.0
) -> Tuple[bool, Dict[str, Any]]:
    """Determine if consecutive transactions represent physically impossible travel.

    Args:
        lat1: Latitude of first transaction.
        lon1: Longitude of first transaction.
        time1: Timestamp of first transaction.
        lat2: Latitude of second transaction.
        lon2: Longitude of second transaction.
        time2: Timestamp of second transaction.
        max_kmh: Maximum physical velocity threshold (default 950 km/h).
        min_distance_threshold_km: Minimum distance before flag triggers (to ignore GPS jitter).

    Returns:
        Tuple of (is_impossible_bool, telemetry_dict).
    """
    distance_km, elapsed_hours, velocity_kmh = calculate_travel_velocity(
        lat1, lon1, time1, lat2, lon2, time2
    )

    impossible = (
        distance_km >= min_distance_threshold_km
        and velocity_kmh > max_kmh
    )

    telemetry = {
        "distance_km": round(distance_km, 2),
        "elapsed_hours": round(elapsed_hours, 4),
        "elapsed_minutes": round(elapsed_hours * 60, 2),
        "velocity_kmh": round(velocity_kmh, 2),
        "max_threshold_kmh": max_kmh,
        "is_impossible": impossible,
        "severity": "CRITICAL" if velocity_kmh > 2000 else "HIGH" if impossible else "NORMAL"
    }

    return impossible, telemetry
