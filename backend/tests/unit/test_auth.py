"""Unit tests for Authentication, Hashing, and JWT Tokens."""

import unittest
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestAuthenticationUnit(unittest.TestCase):

    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword@2026!"
        hashed = get_password_hash(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_jwt_token_lifecycle(self):
        token = create_access_token(subject="USR_1001", role="FRAUD_ANALYST")
        payload = decode_token(token)
        self.assertEqual(payload["sub"], "USR_1001")
        self.assertEqual(payload["role"], "FRAUD_ANALYST")
        self.assertEqual(payload["type"], "access")

    def test_invalid_token_rejection(self):
        with self.assertRaises(ValueError):
            decode_token("invalid.token.structure")


if __name__ == "__main__":
    unittest.main()
