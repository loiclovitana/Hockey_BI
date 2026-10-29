import asyncio
import json
import os
import unittest
from datetime import date
from unittest.mock import patch

import httpx
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior

from hmtracker.database.models import PlayerInfoType
from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerAbsenceInfo,
    PlayerTransferInfo,
    extract_player_news,
)
from hmtracker.parser.models import ArticleDetails


class TestPydanticPlayerNewsExtractor(unittest.TestCase):
    """Exercise the real agent and providers with HTTP responses supplied locally."""

    def setUp(self):
        env = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True)
        env.start()
        self.addCleanup(env.stop)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
        self.addCleanup(asyncio.set_event_loop, None)
        self.client = httpx.AsyncClient(transport=httpx.MockTransport(self.respond))
        self.addCleanup(lambda: self.loop.run_until_complete(self.client.aclose()))
        for provider in ("openai", "ollama"):
            factory = patch(
                f"pydantic_ai.providers.{provider}.cached_async_http_client",
                return_value=self.client,
            )
            factory.start()
            self.addCleanup(factory.stop)
        self.requests = []
        self.payload = {"players": []}
        self.payloads = []
        self.status_code = 200
        self.article = ArticleDetails(
            date=date(2026, 10, 23),
            title="Player update",
            description="Latest news",
            text="No player updates today.",
        )

    def respond(self, request):
        self.requests.append(request)
        if self.status_code != 200:
            return httpx.Response(
                self.status_code, json={"error": {"message": "Model unavailable"}}
            )
        payload = self.payloads.pop(0) if self.payloads else self.payload
        content = json.dumps(payload)
        if request.url.path.endswith("/responses"):
            response = {
                "id": "resp_test",
                "object": "response",
                "created_at": 0,
                "model": "gpt-6-luna",
                "status": "completed",
                "output": [
                    {
                        "id": "msg_test",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {"type": "output_text", "text": content, "annotations": []}
                        ],
                    }
                ],
            }
        else:
            response = {
                "id": "chatcmpl_test",
                "object": "chat.completion",
                "created": 0,
                "model": "llama3.2",
                "choices": [
                    {
                        "index": 0,
                        "finish_reason": "stop",
                        "message": {"role": "assistant", "content": content},
                    }
                ],
            }
        return httpx.Response(200, json=response)

    def use_ollama(self):
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.update(
            HM_PLAYER_NEWS_PROVIDER="ollama", HM_PLAYER_NEWS_MODEL="llama3.2"
        )

    def test_openai_default_preserves_responses_schema_and_storage_setting(self):
        result = extract_player_news(self.article)
        self.assertEqual(result, ArticlePlayerNews(players=[]))
        request = self.requests[0]
        body = json.loads(request.content)
        self.assertEqual(str(request.url), "https://api.openai.com/v1/responses")
        self.assertEqual(request.headers["authorization"], "Bearer test-key")
        self.assertEqual(body["model"], "gpt-6-luna")
        self.assertFalse(body["store"])
        self.assertEqual(body["text"]["format"]["type"], "json_schema")
        self.assertIn("players", body["text"]["format"]["schema"]["properties"])
        self.assertEqual(body["input"][-1]["content"], self.article.to_markdown())
        self.assertEqual(request.extensions["timeout"]["read"], 120)

    def test_openai_custom_model_and_endpoint(self):
        os.environ.update(
            HM_PLAYER_NEWS_MODEL="custom-model",
            OPENAI_BASE_URL="https://openai.example/v1",
        )
        extract_player_news(self.article)
        self.assertEqual(self.requests[0].url.host, "openai.example")
        self.assertEqual(json.loads(self.requests[0].content)["model"], "custom-model")

    def test_ollama_without_openai_credentials_uses_native_schema(self):
        self.use_ollama()
        result = extract_player_news(self.article)
        self.assertEqual(result, ArticlePlayerNews(players=[]))
        request = self.requests[0]
        body = json.loads(request.content)
        self.assertEqual(str(request.url), "http://localhost:11434/v1/chat/completions")
        self.assertEqual(body["model"], "llama3.2")
        self.assertEqual(body["response_format"]["type"], "json_schema")
        self.assertIn(
            "players", body["response_format"]["json_schema"]["schema"]["properties"]
        )
        self.assertEqual(body["messages"][-1]["content"], self.article.to_markdown())
        self.assertNotIn("tools", body)
        self.assertEqual(request.extensions["timeout"]["read"], 120)

    def test_ollama_custom_endpoint_and_credentials(self):
        self.use_ollama()
        os.environ.update(
            OLLAMA_BASE_URL="https://ollama.example/v1", OLLAMA_API_KEY="local-key"
        )
        extract_player_news(self.article)
        self.assertEqual(self.requests[0].url.host, "ollama.example")
        self.assertEqual(self.requests[0].headers["authorization"], "Bearer local-key")

    def test_empty_optional_settings_use_defaults(self):
        os.environ.update(
            HM_PLAYER_NEWS_PROVIDER="", HM_PLAYER_NEWS_MODEL="", OPENAI_BASE_URL=""
        )
        extract_player_news(self.article)
        self.assertEqual(json.loads(self.requests[0].content)["model"], "gpt-6-luna")
        self.use_ollama()
        os.environ["OLLAMA_BASE_URL"] = ""
        extract_player_news(self.article)
        self.assertEqual(self.requests[-1].url.host, "localhost")

    def test_invalid_configuration_fails_without_requests(self):
        for env, error in [
            ({}, "OPENAI_API_KEY"),
            ({"HM_PLAYER_NEWS_PROVIDER": "other"}, "HM_PLAYER_NEWS_PROVIDER"),
            ({"HM_PLAYER_NEWS_PROVIDER": "ollama"}, "HM_PLAYER_NEWS_MODEL"),
            (
                {"HM_PLAYER_NEWS_PROVIDER": "ollama", "HM_PLAYER_NEWS_MODEL": " "},
                "HM_PLAYER_NEWS_MODEL",
            ),
        ]:
            with self.subTest(env=env), patch.dict(os.environ, env, clear=True):
                with self.assertRaisesRegex(ValueError, error):
                    extract_player_news(self.article)
        self.assertEqual(self.requests, [])

    def test_players_are_validated_with_both_backends(self):
        self.payload = {
            "players": [
                {
                    "player_name": "  Test Player  ",
                    "confirmed": True,
                    "info_type": "Transfert",
                    "from_team": None,
                    "to_team": "New Team",
                    "transfer_time": None,
                },
                {
                    "player_name": "Returning Player",
                    "confirmed": False,
                    "info_type": "Absence",
                    "reason": "Injury",
                    "team": "Team A",
                    "is_return": True,
                    "expected_duration_or_return": "Tonight",
                },
            ]
        }
        for provider in ("openai", "ollama"):
            with self.subTest(provider=provider):
                if provider == "ollama":
                    self.use_ollama()
                players = extract_player_news(self.article).players
                self.assertEqual(len(players), 2)
                player = players[0]
                self.assertIsInstance(player, PlayerTransferInfo)
                self.assertEqual(player.player_name, "Test Player")
                self.assertEqual(player.info_type, PlayerInfoType.TRANSFERT)
                self.assertEqual(player.to_team, "New Team")
                self.assertTrue(player.confirmed)
                self.assertIsNone(player.transfer_time)
                returning_player = players[1]
                self.assertIsInstance(returning_player, PlayerAbsenceInfo)
                self.assertEqual(returning_player.info_type, PlayerInfoType.ABSENCE)
                self.assertEqual(returning_player.reason, PlayerInfoType.INJURY)
                self.assertFalse(returning_player.confirmed)
                self.assertTrue(returning_player.is_return)
                self.assertEqual(
                    returning_player.expected_duration_or_return, "Tonight"
                )

    def test_invalid_player_update_is_retried(self):
        self.use_ollama()
        self.payloads = [
            {
                "players": [
                    {
                        "player_name": "Test Player",
                        "confirmed": True,
                        "info_type": "Absence",
                        "reason": "Injury",
                        "team": None,
                        "is_return": False,
                        "to_team": "Invalid destination",
                        "expected_duration_or_return": "Unknown",
                    }
                ]
            },
            {"players": []},
        ]
        self.assertEqual(extract_player_news(self.article).players, [])
        self.assertEqual(len(self.requests), 2)
        self.assertIn("extra_forbidden", self.requests[-1].content.decode())

    def test_repeated_invalid_output_raises(self):
        self.use_ollama()
        self.payload = {"players": [{"player_name": "Incomplete Player"}]}
        with self.assertRaises(UnexpectedModelBehavior):
            extract_player_news(self.article)

    def test_backend_errors_propagate(self):
        self.use_ollama()
        self.status_code = 400
        with self.assertRaises(ModelHTTPError):
            extract_player_news(self.article)


if __name__ == "__main__":
    unittest.main()
