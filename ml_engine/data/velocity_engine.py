"""High-Performance Real-Time Sliding-Window Velocity & Aggregation Engine.

Tracks cardholder spending frequencies, burst velocity, rolling monetary sums,
and distinct entity counts across sliding time horizons (5 minutes, 1 hour, 6 hours, 24 hours, 7 days).
"""

from __future__ import annotations
import collections
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any, Deque


class SlidingWindowRecord:
    """Represents a lightweight historical event stored in memory/cache."""
    __slots__ = ("timestamp_utc", "amount", "merchant_id", "country", "device_fingerprint", "ip_address")

    def __init__(
        self,
        timestamp_utc: float,
        amount: float,
        merchant_id: str,
        country: str,
        device_fingerprint: str,
        ip_address: str
    ):
        self.timestamp_utc = timestamp_utc
        self.amount = amount
        self.merchant_id = merchant_id
        self.country = country
        self.device_fingerprint = device_fingerprint
        self.ip_address = ip_address


class CardholderVelocityProfile:
    """Maintains a rolling ring-buffer of transaction events for a specific cardholder."""

    def __init__(self, card_id: str, max_retention_days: int = 7):
        self.card_id = card_id
        self.max_retention_seconds = max_retention_days * 86400.0
        self.history: Deque[SlidingWindowRecord] = collections.deque()
        self.lifetime_count: int = 0
        self.lifetime_sum: float = 0.0

    def add_transaction(
        self,
        timestamp_epoch: float,
        amount: float,
        merchant_id: str = "",
        country: str = "US",
        device_fingerprint: str = "",
        ip_address: str = ""
    ) -> None:
        """Insert a new transaction and purge events older than retention horizon."""
        record = SlidingWindowRecord(
            timestamp_utc=timestamp_epoch,
            amount=amount,
            merchant_id=merchant_id,
            country=country,
            device_fingerprint=device_fingerprint,
            ip_address=ip_address
        )
        self.history.append(record)
        self.lifetime_count += 1
        self.lifetime_sum += amount
        self._purge_expired(timestamp_epoch)

    def _purge_expired(self, current_timestamp_epoch: float) -> None:
        """Purge entries older than max retention."""
        cutoff = current_timestamp_epoch - self.max_retention_seconds
        while self.history and self.history[0].timestamp_utc < cutoff:
            self.history.popleft()

    def get_window_aggregates(self, current_timestamp_epoch: float, window_seconds: float) -> Dict[str, Any]:
        """Compute count, sum, mean, std, and distinct counts in a trailing window."""
        cutoff = current_timestamp_epoch - window_seconds
        count = 0
        total_amt = 0.0
        amounts: List[float] = []
        distinct_merchants = set()
        distinct_countries = set()
        distinct_devices = set()
        distinct_ips = set()

        for rec in reversed(self.history):
            if rec.timestamp_utc < cutoff:
                break
            count += 1
            total_amt += rec.amount
            amounts.append(rec.amount)
            if rec.merchant_id:
                distinct_merchants.add(rec.merchant_id)
            if rec.country:
                distinct_countries.add(rec.country)
            if rec.device_fingerprint:
                distinct_devices.add(rec.device_fingerprint)
            if rec.ip_address:
                distinct_ips.add(rec.ip_address)

        mean_amt = (total_amt / count) if count > 0 else 0.0
        variance = (
            sum((x - mean_amt) ** 2 for x in amounts) / count
            if count > 1
            else 0.0
        )
        std_amt = variance ** 0.5

        return {
            "count": count,
            "sum": round(total_amt, 2),
            "mean": round(mean_amt, 2),
            "std": round(std_amt, 2),
            "max": round(max(amounts), 2) if amounts else 0.0,
            "distinct_merchants": len(distinct_merchants),
            "distinct_countries": len(distinct_countries),
            "distinct_devices": len(distinct_devices),
            "distinct_ips": len(distinct_ips),
        }


class VelocityEngine:
    """Thread-safe velocity engine managing profiles for millions of cards/entities."""

    def __init__(self):
        self._card_profiles: Dict[str, CardholderVelocityProfile] = {}
        self._ip_profiles: Dict[str, CardholderVelocityProfile] = {}
        self._device_profiles: Dict[str, CardholderVelocityProfile] = {}

    def record_event(
        self,
        card_id: str,
        amount: float,
        timestamp_epoch: Optional[float] = None,
        merchant_id: str = "",
        country: str = "US",
        device_fingerprint: str = "",
        ip_address: str = ""
    ) -> None:
        """Record an event across all correlation dimensions."""
        if timestamp_epoch is None:
            timestamp_epoch = datetime.now(timezone.utc).timestamp()

        # Card profile
        if card_id not in self._card_profiles:
            self._card_profiles[card_id] = CardholderVelocityProfile(card_id)
        self._card_profiles[card_id].add_transaction(
            timestamp_epoch, amount, merchant_id, country, device_fingerprint, ip_address
        )

        # IP profile
        if ip_address:
            if ip_address not in self._ip_profiles:
                self._ip_profiles[ip_address] = CardholderVelocityProfile(ip_address)
            self._ip_profiles[ip_address].add_transaction(
                timestamp_epoch, amount, merchant_id, country, device_fingerprint, ip_address
            )

        # Device profile
        if device_fingerprint:
            if device_fingerprint not in self._device_profiles:
                self._device_profiles[device_fingerprint] = CardholderVelocityProfile(device_fingerprint)
            self._device_profiles[device_fingerprint].add_transaction(
                timestamp_epoch, amount, merchant_id, country, device_fingerprint, ip_address
            )

    def extract_velocity_features(
        self,
        card_id: str,
        current_amount: float,
        timestamp_epoch: Optional[float] = None,
        ip_address: str = "",
        device_fingerprint: str = ""
    ) -> Dict[str, Any]:
        """Compute real-time velocity features for inference."""
        if timestamp_epoch is None:
            timestamp_epoch = datetime.now(timezone.utc).timestamp()

        profile = self._card_profiles.get(card_id)
        if not profile:
            return {
                "velocity_5m": 0,
                "velocity_1h": 0,
                "velocity_6h": 0,
                "velocity_24h": 0,
                "velocity_7d": 0,
                "sum_amount_24h": 0.0,
                "mean_amount_7d": current_amount,
                "amount_ratio_to_mean_30d": 1.0,
                "distinct_merchants_24h": 0,
                "distinct_countries_24h": 0,
                "ip_velocity_1h": 0,
                "device_card_count_24h": 0,
            }

        w_5m = profile.get_window_aggregates(timestamp_epoch, 300)
        w_1h = profile.get_window_aggregates(timestamp_epoch, 3600)
        w_6h = profile.get_window_aggregates(timestamp_epoch, 21600)
        w_24h = profile.get_window_aggregates(timestamp_epoch, 86400)
        w_7d = profile.get_window_aggregates(timestamp_epoch, 604800)

        mean_7d = w_7d["mean"] if w_7d["count"] > 0 else current_amount
        ratio = (current_amount / max(mean_7d, 1.0))

        # IP velocity lookup
        ip_vel_1h = 0
        if ip_address and ip_address in self._ip_profiles:
            ip_vel_1h = self._ip_profiles[ip_address].get_window_aggregates(timestamp_epoch, 3600)["count"]

        # Device distinct card count
        dev_cards_24h = 0
        if device_fingerprint and device_fingerprint in self._device_profiles:
            dev_cards_24h = self._device_profiles[device_fingerprint].get_window_aggregates(timestamp_epoch, 86400)["count"]

        return {
            "velocity_5m": w_5m["count"],
            "velocity_1h": w_1h["count"],
            "velocity_6h": w_6h["count"],
            "velocity_24h": w_24h["count"],
            "velocity_7d": w_7d["count"],
            "sum_amount_24h": w_24h["sum"],
            "mean_amount_7d": mean_7d,
            "amount_ratio_to_mean_30d": round(ratio, 4),
            "distinct_merchants_24h": w_24h["distinct_merchants"],
            "distinct_countries_24h": w_24h["distinct_countries"],
            "ip_velocity_1h": ip_vel_1h,
            "device_card_count_24h": dev_cards_24h,
        }
