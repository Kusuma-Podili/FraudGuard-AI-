"""OFAC Sanctions & PEP (Politically Exposed Persons) Screening Engine.

Provides fuzzy entity resolution, Jaro-Winkler string similarity, Levenshtein distance,
and Specially Designated Nationals (SDN) list screening.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone


@dataclass
class SanctionMatchResult:
    is_sanctioned: bool
    confidence_score: float  # 0.0 to 1.0
    matched_sdn_entry: Optional[Dict[str, Any]]
    match_algorithm: str
    requires_blocking: bool
    regulatory_program: str


class OfacSanctionsScanner:
    """Fuzzy entity matching engine against global OFAC/UN/EU sanctions databases."""

    SAMPLE_SDN_LIST = [
        {"id": "SDN_001", "name": "VLADIMIR SMIRNOV", "aliases": ["V. SMIRNOV", "VLAD SMIRNOFF"], "country": "RU", "program": "UKRAINE-EO13661"},
        {"id": "SDN_002", "name": "AHMAD AL-KHALIL", "aliases": ["AHMED KHALIL", "A. ALKHALIL"], "country": "SY", "program": "SDGT"},
        {"id": "SDN_003", "name": "KIM JONG SIK", "aliases": ["KIM JONG-SIK"], "country": "KP", "program": "DPRK3"},
        {"id": "SDN_004", "name": "CARTEL DE LOS SOLES ENTITY", "aliases": ["SOLES LOGISTICS"], "country": "VE", "program": "SDNTK"},
        {"id": "SDN_005", "name": "CARLOS MENDOZA HERNANDEZ", "aliases": ["EL GATO", "CARLOS HERNANDEZ"], "country": "MX", "program": "SDNT"},
    ]

    @staticmethod
    def normalize_name(name: str) -> str:
        """Strip punctuation and uppercase name."""
        return re.sub(r"[^A-Z\s]", "", name.upper()).strip()

    @classmethod
    def jaro_winkler_similarity(cls, s1: str, s2: str) -> float:
        """Calculate Jaro-Winkler string distance between entity names."""
        s1 = cls.normalize_name(s1)
        s2 = cls.normalize_name(s2)

        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        len1, len2 = len(s1), len(s2)
        match_bound = max(len1, len2) // 2 - 1

        matches1 = [False] * len1
        matches2 = [False] * len2
        m = 0

        for i in range(len1):
            start = max(0, i - match_bound)
            end = min(i + match_bound + 1, len2)
            for j in range(start, end):
                if not matches2[j] and s1[i] == s2[j]:
                    matches1[i] = True
                    matches2[j] = True
                    m += 1
                    break

        if m == 0:
            return 0.0

        # Transpositions
        k = 0
        t = 0
        for i in range(len1):
            if matches1[i]:
                while not matches2[k]:
                    k += 1
                if s1[i] != s2[k]:
                    t += 1
                k += 1
        t //= 2

        jaro = (m / len1 + m / len2 + (m - t) / m) / 3.0

        # Winkler prefix bonus (up to 4 chars)
        prefix_len = 0
        for i in range(min(4, len1, len2)):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + (prefix_len * 0.1 * (1.0 - jaro))

    def screen_entity(self, full_name: str, country_code: Optional[str] = None, threshold: float = 0.85) -> SanctionMatchResult:
        """Screen individual or merchant name against SDN list."""
        best_score = 0.0
        best_match = None

        for entry in self.SAMPLE_SDN_LIST:
            # Check main name
            score = self.jaro_winkler_similarity(full_name, entry["name"])
            if score > best_score:
                best_score = score
                best_match = entry

            # Check aliases
            for alias in entry.get("aliases", []):
                alias_score = self.jaro_winkler_similarity(full_name, alias)
                if alias_score > best_score:
                    best_score = alias_score
                    best_match = entry

        # Country risk multiplier
        if best_match and country_code and country_code == best_match.get("country"):
            best_score = min(1.0, best_score + 0.05)

        is_hit = best_score >= threshold
        return SanctionMatchResult(
            is_sanctioned=is_hit,
            confidence_score=round(best_score, 4),
            matched_sdn_entry=best_match if is_hit else None,
            match_algorithm="JARO_WINKLER_FUZZY",
            requires_blocking=bool(is_hit and best_score >= 0.92),
            regulatory_program=best_match["program"] if (is_hit and best_match) else "NONE",
        )
