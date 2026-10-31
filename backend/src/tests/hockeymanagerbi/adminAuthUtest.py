import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import jwt
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from hmtracker.api import admin_login


class AdminAuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.secret = "admin-authentication-test-secret"
        self.enterContext(patch.object(admin_login, "SECRET_KEY", self.secret))
        self.claims = {
            "username": "test-admin",
            "is_admin": True,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        }

    def token(self, claims=None, key=None, algorithm="HS256"):
        return jwt.encode(
            self.claims if claims is None else claims,
            self.secret if key is None else key,
            algorithm=algorithm,
        )

    def assert_unauthorized(self, token):
        with self.assertRaises(HTTPException) as raised:
            admin_login.decode_token(token)
        self.assertEqual(raised.exception.status_code, 401)
        self.assertEqual(raised.exception.headers, {"WWW-Authenticate": "Bearer"})


class TestAdminAuthentication(AdminAuthenticationTestCase):
    def test_issued_token_has_enforced_one_hour_expiry(self):
        before = datetime.now(timezone.utc).timestamp()
        with patch.object(admin_login.admin, "is_admin", return_value=True) as check:
            token = admin_login.create_access_token("test-admin", "test-password")
        check.assert_called_once_with("test-admin", "test-password")
        claims = jwt.decode(token, self.secret, algorithms=["HS256"])
        self.assertGreaterEqual(claims["exp"], before + 3600 - 1)
        self.assertLessEqual(
            claims["exp"], datetime.now(timezone.utc).timestamp() + 3600
        )
        self.assertEqual(admin_login.decode_token(token), "test-admin")
        with patch("jwt.api_jwt.datetime") as clock:
            clock.now.return_value = datetime.fromtimestamp(claims["exp"], timezone.utc)
            self.assert_unauthorized(token)

    def test_incorrect_login_credentials_are_rejected(self):
        with patch.object(admin_login.admin, "is_admin", return_value=False):
            with self.assertRaises(HTTPException) as raised:
                admin_login.create_access_token("test-admin", "wrong-password")
        self.assertEqual(raised.exception.status_code, 401)

    def test_invalid_claims_are_rejected(self):
        invalid_claims = [
            {**self.claims, "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            {**self.claims, "exp": "not-a-timestamp"},
            {**self.claims, "is_admin": False},
            {**self.claims, "is_admin": "false"},
            {**self.claims, "is_admin": 1},
            {**self.claims, "username": ""},
            {**self.claims, "username": " "},
            {**self.claims, "username": 123},
            {
                "username": "test-admin",
                "is_admin": True,
                "expiration": "2000-01-01T00:00+00:00",
            },
        ]
        for claim in ("exp", "username", "is_admin"):
            invalid_claims.append({k: v for k, v in self.claims.items() if k != claim})
        for claims in invalid_claims:
            with self.subTest(claims=claims):
                self.assert_unauthorized(self.token(claims))

    def test_invalid_signatures_and_algorithms_are_rejected(self):
        for token in (
            "definitely-not-a-jwt",
            self.token(key="wrong-secret"),
            self.token(algorithm="HS384"),
            self.token(key="", algorithm="none"),
        ):
            with self.subTest(token=token):
                self.assert_unauthorized(token)

    def test_missing_or_empty_server_key_rejects_tokens(self):
        token = self.token()
        for key in (None, ""):
            with self.subTest(key=key), patch.object(admin_login, "SECRET_KEY", key):
                self.assert_unauthorized(token)


class TestAdminRouteAuthentication(AdminAuthenticationTestCase):
    def setUp(self):
        super().setUp()
        with patch.dict(os.environ, {"HM_DATABASE_URL": "sqlite://"}):
            from hmtracker.api.routers import admin

        self.routes = admin
        self.operations = {
            name: self.enterContext(patch.object(admin.admin, name))
            for name in (
                "start_loading",
                "start_team_alignement",
                "start_loading_playernews",
                "start_matching_playernews",
                "get_current_operation",
            )
        }
        self.import_matches = self.enterContext(patch.object(admin, "import_matches"))
        self.session_access = Mock()

        def session_override():
            self.session_access()
            raise AssertionError("Unauthenticated request accessed the database")

        app = FastAPI()
        app.include_router(admin.router)
        app.dependency_overrides[admin.get_session] = session_override
        self.client = self.enterContext(TestClient(app))

    def test_every_admin_route_rejects_invalid_authentication_before_side_effects(self):
        tokens = [
            None,
            "",
            "definitely-not-a-jwt",
            self.token(key="wrong-secret"),
            self.token({**self.claims, "exp": 1}),
            self.token({k: v for k, v in self.claims.items() if k != "exp"}),
            self.token({**self.claims, "is_admin": False}),
        ]
        for route in self.routes.router.routes:
            for method in route.methods:
                for token in tokens:
                    with self.subTest(path=route.path, method=method, token=token):
                        response = self.client.request(
                            method,
                            route.path,
                            headers={}
                            if token is None
                            else {"Authorization": f"Bearer {token}"},
                            **(
                                {
                                    "files": {
                                        "file": ("matches.csv", b"test", "text/csv")
                                    }
                                }
                                if route.path.endswith("/upload")
                                else {}
                            ),
                        )
                        self.assertEqual(response.status_code, 401)
                        self.assertEqual(response.headers["www-authenticate"], "Bearer")
        self.session_access.assert_not_called()
        self.import_matches.assert_not_called()
        for operation in self.operations.values():
            operation.assert_not_called()

    def test_valid_token_can_access_user_and_start_operation(self):
        headers = {"Authorization": f"Bearer {self.token()}"}
        response = self.client.get("/admin/user", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"username": "test-admin"})
        response = self.client.post("/admin/load/start", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.operations["start_loading"].assert_called_once_with()
