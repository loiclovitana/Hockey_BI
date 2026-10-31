import os
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

import requests
from fastapi.testclient import TestClient

from hmtracker.common.exceptions import HMAuthenticationError, HMUnavailableError
from hmtracker.parser.hmparser import HMAjaxScrapper
from hmtracker.services.check_user import connect_to_hm


class TestHMLogin(unittest.TestCase):
    def setUp(self):
        self.session = self.enterContext(
            patch("hmtracker.parser.hmparser.requests.session")
        ).return_value
        self.parser = HMAjaxScrapper()
        self.addCleanup(self.parser.close_session)

    def test_invalid_credentials_do_not_load_dashboard(self):
        self.session.post.return_value = Mock(status_code=200, text="0")
        with self.assertRaisesRegex(HMAuthenticationError, "username or password"):
            self.parser.connect_to_hm("user", "wrong-password")
        self.session.get.assert_not_called()

    def test_login_http_and_network_failures_are_service_errors(self):
        for failure in (None, requests.Timeout(), requests.ConnectionError()):
            with self.subTest(failure=failure):
                self.session.post.side_effect = failure
                self.session.post.return_value = Mock(
                    status_code=503, text="private upstream error"
                )
                with self.assertRaises(HMUnavailableError) as raised:
                    self.parser.connect_to_hm("user", "password")
                self.assertNotIn("private upstream error", str(raised.exception))
        self.session.get.assert_not_called()

    def test_successful_login_loads_dashboard(self):
        self.session.post.return_value = Mock(status_code=200, text="1")
        with patch.object(self.parser, "_load_main_dashboard") as dashboard:
            self.parser.connect_to_hm("user", "password")
        dashboard.assert_called_once_with()

    def test_dashboard_http_failures_have_bounded_retries(self):
        self.session.post.return_value = Mock(status_code=200, text="1")
        self.session.get.return_value = Mock(status_code=503, text="unavailable")
        with self.assertRaises(HMUnavailableError):
            self.parser.connect_to_hm("user", "password")
        self.assertEqual(self.session.get.call_count, 5)

    def test_dashboard_timeout_is_a_service_error(self):
        self.session.post.return_value = Mock(status_code=200, text="1")
        self.session.get.side_effect = requests.Timeout()
        with self.assertRaises(HMUnavailableError):
            self.parser.connect_to_hm("user", "password")

    def test_credential_check_closes_session_on_success_and_failure(self):
        for error in (None, HMAuthenticationError(), HMUnavailableError()):
            with (
                self.subTest(error=error),
                patch("hmtracker.services.check_user.HMAjaxScrapper") as parser,
            ):
                parser.return_value.connect_to_hm.side_effect = error
                if error:
                    with self.assertRaises(type(error)):
                        connect_to_hm("user", "password")
                else:
                    connect_to_hm("user", "password")
                parser.return_value.close_session.assert_called_once_with()


class TestMyTeamAuthentication(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"HM_DATABASE_URL": "sqlite://"}):
            from hmtracker.api.server import api
            from hmtracker.api.routers import myteam

        self.routes = myteam
        self.session = Mock()
        self.manager = SimpleNamespace(id=1, last_import=datetime.now())
        self.session.get_manager_by_email.return_value = self.manager
        self.enterContext(
            patch.dict(
                api.dependency_overrides,
                {
                    myteam.get_session: lambda: self.session,
                },
            )
        )
        self.http_session = self.enterContext(
            patch("hmtracker.parser.hmparser.requests.session")
        ).return_value
        self.http_session.post.return_value = Mock(status_code=200, text="0")
        self.client = self.enterContext(TestClient(api))
        self.credentials = {"hm_user": "user", "hm_password": "password"}

    def request(self, path, force=False):
        if path == "/team_value_evolution":
            return self.client.post(
                "/myteam" + path,
                params={"team_code": "team"},
                json={"request": self.credentials},
            )
        body = {**self.credentials}
        if path == "/load":
            body["force_team_reload"] = force
        return self.client.post("/myteam" + path, json=body)

    def test_all_routes_reject_credentials_without_writes(self):
        for manager in (None, self.manager):
            self.session.get_manager_by_email.return_value = manager
            for path in (
                "/load",
                "/autolineup/register",
                "/autolineup/unregister",
                "/team_value_evolution",
            ):
                with self.subTest(path=path, manager_exists=manager is not None):
                    response = self.request(path)
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(
                        response.json(), {"detail": str(HMAuthenticationError())}
                    )
        self.session.session.commit.assert_not_called()
        self.session.get_teams.assert_not_called()

    def test_forced_reload_rejects_invalid_credentials(self):
        response = self.request("/load", force=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": str(HMAuthenticationError())})
        self.session.session.commit.assert_not_called()

    def test_missing_manager_returns_same_error_without_calling_parser(self):
        self.session.get_manager_by_email.return_value = None
        with patch.object(self.routes, "connect_to_hm") as authenticate:
            for path in (
                "/autolineup/register",
                "/autolineup/unregister",
                "/team_value_evolution",
            ):
                with self.subTest(path=path):
                    authenticate.reset_mock()
                    response = self.request(path)
                    authenticate.assert_not_called()
                    self.assertEqual(response.status_code, 401)
                    self.assertEqual(
                        response.json(), {"detail": str(HMAuthenticationError())}
                    )
        self.session.session.commit.assert_not_called()

    def test_manager_lookup_precedes_parser_authentication(self):
        def authenticate(email, password):
            self.session.get_manager_by_email.assert_called_once_with(email)
            raise HMAuthenticationError()

        for path in (
            "/autolineup/register",
            "/autolineup/unregister",
            "/team_value_evolution",
        ):
            with (
                self.subTest(path=path),
                patch.object(
                    self.routes, "connect_to_hm", side_effect=authenticate
                ) as parser,
            ):
                self.session.get_manager_by_email.reset_mock()
                self.assertEqual(self.request(path).status_code, 401)
                parser.assert_called_once_with("user", password="password")

    def test_service_failure_has_distinct_response_on_cached_and_reload_paths(self):
        self.http_session.post.side_effect = requests.Timeout()
        for path, force in (
            ("/load", False),
            ("/load", True),
            ("/autolineup/register", False),
            ("/autolineup/unregister", False),
            ("/team_value_evolution", False),
        ):
            with self.subTest(path=path, force=force):
                response = self.request(path, force=force)
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json(), {"detail": str(HMUnavailableError())})
        self.session.session.commit.assert_not_called()

    def test_valid_credentials_still_allow_cached_load_and_manager_operations(self):
        self.http_session.post.return_value = Mock(status_code=200, text="1")
        self.session.get_teams.return_value = []
        with (
            patch.object(HMAjaxScrapper, "_load_main_dashboard"),
            patch.object(self.routes, "encrypt", return_value="encrypted-password"),
            patch.object(self.routes, "compute_team_value_sql", return_value=[]),
        ):
            for path in (
                "/load",
                "/autolineup/register",
                "/autolineup/unregister",
                "/team_value_evolution",
            ):
                with self.subTest(path=path):
                    response = self.request(path)
                    self.assertEqual(response.status_code, 200, response.text)

    def test_first_load_can_create_a_manager_after_successful_authentication(self):
        self.session.get_manager_by_email.return_value = None
        self.http_session.post.return_value = Mock(status_code=200, text="1")
        self.session.get_teams.return_value = []

        def import_manager(loader, email, session):
            self.assertEqual(loader(), {})
            session.get_manager_by_email.return_value = self.manager

        with (
            patch.object(HMAjaxScrapper, "_load_main_dashboard"),
            patch.object(HMAjaxScrapper, "get_teams", return_value=[]),
            patch.object(
                self.routes,
                "import_teamplayers_from_loader",
                side_effect=import_manager,
            ),
        ):
            response = self.request("/load")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["manager"]["id"], 1)
