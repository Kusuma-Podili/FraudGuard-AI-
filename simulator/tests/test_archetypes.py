"""Unit tests for Adversarial Attack Archetypes."""

import unittest
from simulator.archetypes import (
    CardTestingArchetype,
    ImpossibleTravelArchetype,
    AccountTakeoverArchetype,
    CryptoVelocityArchetype,
    CredentialStuffingArchetype,
    NocturnalLuxuryArchetype,
)


class TestAttackArchetypes(unittest.TestCase):

    def test_card_testing_archetype(self):
        wave = CardTestingArchetype.generate_wave("CARD_1001", count=5)
        self.assertEqual(len(wave), 5)
        for tx in wave:
            self.assertLess(tx["amount"], 3.0)
            self.assertEqual(tx["fraud_archetype"], "CARD_TESTING")

    def test_impossible_travel_archetype(self):
        pair = ImpossibleTravelArchetype.generate_pair("CARD_1002")
        self.assertEqual(len(pair), 2)
        self.assertEqual(pair[0]["country_code"], "US")
        self.assertEqual(pair[1]["country_code"], "JP")
        self.assertEqual(pair[1]["fraud_archetype"], "IMPOSSIBLE_TRAVEL")

    def test_account_takeover_archetype(self):
        burst = AccountTakeoverArchetype.generate_burst("CARD_1003", count=2)
        self.assertEqual(len(burst), 2)
        for tx in burst:
            self.assertGreaterEqual(tx["amount"], 800.0)
            self.assertEqual(tx["merchant_category"], "ELECTRONICS")

    def test_crypto_velocity_archetype(self):
        surge = CryptoVelocityArchetype.generate_surge("CARD_1004", count=3)
        self.assertEqual(len(surge), 3)
        for tx in surge:
            self.assertEqual(tx["merchant_category"], "CRYPTO_EXCHANGE")
            self.assertEqual(tx["country_code"], "CY")

    def test_credential_stuffing_archetype(self):
        attacks = CredentialStuffingArchetype.generate_attack("CARD_1005")
        self.assertEqual(len(attacks), 4)
        self.assertEqual(attacks[0]["failed_pin_attempts_24h"], 1)
        self.assertEqual(attacks[-1]["failed_pin_attempts_24h"], 4)

    def test_nocturnal_luxury_archetype(self):
        spree = NocturnalLuxuryArchetype.generate_spree("CARD_1006")
        self.assertEqual(len(spree), 1)
        self.assertGreaterEqual(spree[0]["amount"], 5000.0)
        self.assertEqual(spree[0]["merchant_category"], "LUXURY_JEWELRY")


if __name__ == "__main__":
    unittest.main()
