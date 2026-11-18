import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app.api.auth import LoginRequest, login
from app.core.auth import (
    AuthenticatedUser,
    allowed_tenants,
    create_access_token,
    decode_access_token,
    hash_password,
)
from app.core.config import settings


class AuthTests(unittest.TestCase):
    def test_password_hash_and_login_issue_access_level_token(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            users_file = Path(temp_dir) / "users.json"
            users_file.write_text(json.dumps([{
                "username": "spy-user",
                "password_hash": hash_password("strong-test-password"),
                "access_level": "spy_car",
            }]), encoding="utf-8")

            with (
                patch("app.core.auth.USERS_FILE", users_file),
                patch.object(settings, "AUTH_SECRET", "test-signing-secret"),
            ):
                result = login(LoginRequest(username="SPY-USER", password="strong-test-password"))
                user = decode_access_token(result["access_token"])

        self.assertEqual(user, AuthenticatedUser("spy-user", "spy_car"))
        self.assertEqual(result["user"]["access_level"], "spy_car")

    def test_invalid_password_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            users_file = Path(temp_dir) / "users.json"
            users_file.write_text(json.dumps([{
                "username": "spy-user",
                "password_hash": hash_password("correct-password"),
                "access_level": "spy_car",
            }]), encoding="utf-8")

            with (
                patch("app.core.auth.USERS_FILE", users_file),
                patch.object(settings, "AUTH_SECRET", "test-signing-secret"),
            ):
                with self.assertRaises(HTTPException) as error:
                    login(LoginRequest(username="spy-user", password="wrong-password"))

        self.assertEqual(error.exception.status_code, 401)

    def test_tampered_token_is_rejected(self):
        with patch.object(settings, "AUTH_SECRET", "test-signing-secret"):
            token = create_access_token("director", "diretoria")
            header, payload, signature = token.split(".")
            replacement = "A" if signature[0] != "A" else "B"
            with self.assertRaises(HTTPException) as error:
                decode_access_token(f"{header}.{payload}.{replacement}{signature[1:]}")

        self.assertEqual(error.exception.status_code, 401)

    def test_directoria_can_access_both_tenants(self):
        self.assertEqual(
            allowed_tenants(AuthenticatedUser("director", "diretoria")),
            ("spy_car", "g_system"),
        )


if __name__ == "__main__":
    unittest.main()
