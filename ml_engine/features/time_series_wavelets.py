"""Time-Series Wavelet & Spectral Decomposition for High-Frequency Burst Detection.

Performs:
- Discrete Wavelet Transform (Haar DWT) multiresolution decomposition
- Fast Fourier Transform (FFT) power spectral density estimation
- Micro-burst periodicity and entropy quantification for card testing probes
"""

from __future__ import annotations
import math
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class SpectralBurstFeatures:
    spectral_energy_low_freq: float
    spectral_energy_high_freq: float
    spectral_entropy: float
    wavelet_detail_energy: float
    is_periodic_burst: bool


class WaveletSpectralAnalyzer:
    """Decomposes transaction interval and amount sequences into spectral wavelets."""

    @staticmethod
    def haar_dwt_level1(signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute 1-level Discrete Haar Wavelet Transform (Approximation and Detail coefficients)."""
        n = len(signal)
        if n % 2 != 0:
            signal = np.append(signal, signal[-1])
            n += 1

        approx = (signal[0::2] + signal[1::2]) / math.sqrt(2.0)
        detail = (signal[0::2] - signal[1::2]) / math.sqrt(2.0)
        return approx, detail

    @classmethod
    def analyze_spending_bursts(cls, amount_sequence: List[float]) -> SpectralBurstFeatures:
        """Calculate frequency domain energy and Haar wavelet detail coefficients."""
        if len(amount_sequence) < 4:
            return SpectralBurstFeatures(
                spectral_energy_low_freq=0.0,
                spectral_energy_high_freq=0.0,
                spectral_entropy=0.0,
                wavelet_detail_energy=0.0,
                is_periodic_burst=False,
            )

        arr = np.array(amount_sequence, dtype=np.float32)
        arr = arr - np.mean(arr)  # Zero-center

        # FFT
        fft_vals = np.fft.rfft(arr)
        power_spectrum = np.abs(fft_vals) ** 2
        total_power = float(np.sum(power_spectrum)) + 1e-12

        # Energy split
        mid = len(power_spectrum) // 2
        low_energy = float(np.sum(power_spectrum[:mid])) / total_power
        high_energy = float(np.sum(power_spectrum[mid:])) / total_power

        # Spectral Entropy
        prob_dist = power_spectrum / total_power
        entropy = -float(np.sum(prob_dist * np.log2(np.maximum(prob_dist, 1e-12))))

        # Wavelet decomposition
        _, detail = cls.haar_dwt_level1(arr)
        detail_energy = float(np.sum(detail ** 2))

        # Periodic micro-burst indicator (card testing spikes have high frequency and low entropy)
        is_burst = bool(high_energy > 0.65 and entropy < 1.8)

        return SpectralBurstFeatures(
            spectral_energy_low_freq=round(low_energy, 4),
            spectral_energy_high_freq=round(high_energy, 4),
            spectral_entropy=round(entropy, 4),
            wavelet_detail_energy=round(detail_energy, 4),
            is_periodic_burst=is_burst,
        )
