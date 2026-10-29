import asyncio
import json
import os
import unittest
from datetime import date
from unittest.mock import patch

from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import (
    ModelResponse,
    RetryPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models import override_allow_model_requests
from pydantic_ai.models.function import FunctionModel

from hmtracker.database.models import PlayerInfoType
from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerTransferInfo,
    _create_agent,
    extract_player_news,
)
from hmtracker.parser.models import ArticleDetails


class TestPlayerNewsExtractor(unittest.TestCase):
    """Run the configured agent with local model replies and no provider requests."""

    def setUp(self):
        self.enterContext(
            patch.dict(os.environ, {"OPENAI_API_KEY": "test"}, clear=True)
        )
        self.enterContext(override_allow_model_requests(False))
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.addCleanup(self.loop.close)
        self.addCleanup(asyncio.set_event_loop, None)
        agent = _create_agent()
        self.enterContext(agent.override(model=FunctionModel(self.respond)))
        self.enterContext(
            patch(
                "hmtracker.loader.playernews.extractor._create_agent",
                return_value=agent,
            )
        )
        self.article = ArticleDetails(
            date=date(2026, 10, 23),
            title="Player update",
            description="Latest news",
            text="Test Player is joining New Team next season.",
        )
        self.replies = ['{"players": []}']
        self.requests = []

    async def respond(self, messages, info):
        self.requests.append(list(messages))
        return ModelResponse(parts=[TextPart(self.replies.pop(0))])

    def test_article_markdown_produces_typed_player_updates(self):
        self.replies = [
            json.dumps(
                {
                    "players": [
                        {
                            "player_name": "  Test Player  ",
                            "confirmed": True,
                            "info_type": "Transfert",
                            "from_team": None,
                            "to_team": "New Team",
                            "transfer_time": "Next season",
                        }
                    ]
                }
            )
        ]

        result = extract_player_news(self.article)

        self.assertIsInstance(result, ArticlePlayerNews)
        self.assertEqual(len(result.players), 1)
        player = result.players[0]
        self.assertIsInstance(player, PlayerTransferInfo)
        self.assertEqual(player.player_name, "Test Player")
        self.assertEqual(player.info_type, PlayerInfoType.TRANSFERT)
        self.assertEqual(player.to_team, "New Team")
        self.assertEqual(player.transfer_time, "Next season")
        self.assertIsNone(player.from_team)
        self.assertTrue(player.confirmed)
        prompts = [
            part.content
            for message in self.requests[0]
            for part in message.parts
            if isinstance(part, UserPromptPart)
        ]
        self.assertEqual(prompts, [self.article.to_markdown()])

    def test_article_without_updates_returns_empty_players(self):
        self.assertEqual(
            extract_player_news(self.article), ArticlePlayerNews(players=[])
        )
        self.assertEqual(len(self.requests), 1)

    def test_invalid_json_is_retried_with_validation_feedback(self):
        self.replies = ["invalid JSON", '{"players": []}']

        self.assertEqual(extract_player_news(self.article).players, [])

        self.assertEqual(len(self.requests), 2)
        self.assertTrue(
            any(
                isinstance(part, RetryPromptPart)
                for message in self.requests[-1]
                for part in message.parts
            )
        )

    def test_missing_structured_output_exhausts_retries(self):
        self.replies = ["{}", "{}"]

        with self.assertRaises(UnexpectedModelBehavior):
            extract_player_news(self.article)

        self.assertEqual(len(self.requests), 2)


if __name__ == "__main__":
    unittest.main()
