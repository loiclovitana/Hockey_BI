import json
import unittest
from pathlib import Path
from unicodedata import normalize, category as uniform_category

from hmtracker.database.models import PlayerInfoType
from pydantic_ai import capture_run_messages
from pydantic_ai.messages import ModelMessagesTypeAdapter

from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerAbsenceInfo,
    PlayerNewsInfo,
    PlayerTransferInfo,
    extract_player_news,
)
from hmtracker.parser.models import ArticleDetails


DATASET = Path(__file__).resolve().parents[1] / "resources" / "shn_player_news.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "output" / "player_news"


def _uniform(name: str | None):
    if name is None:
        return ""
    text = normalize("NFD", name)
    text = "".join(c for c in text if uniform_category(c) != "Mn")
    return text.casefold()


class TestPlayerNewsExtractorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dataset = json.loads(DATASET.read_text(encoding="utf-8"))
        cls.articles = {
            entry["source_url"].rsplit("/", 1)[-1]: entry["article"]
            for entry in dataset["articles"]
        }

    def extract(self, slug):
        article = ArticleDetails.model_validate(self.articles[slug])
        article_dir = OUTPUT_DIR / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        output = None
        with capture_run_messages() as messages:
            try:
                result = extract_player_news(article)
                self.assertIsInstance(result, ArticlePlayerNews)
                output = result.model_dump(mode="json")
            except Exception as error:
                output = {"error": type(error).__name__, "message": str(error)}
                raise
            finally:
                (article_dir / "conversation.json").write_bytes(
                    ModelMessagesTypeAdapter.dump_json(messages, indent=2) + b"\n"
                )
                (article_dir / "output.json").write_text(
                    json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        return result.players

    def find_player(self, players : list[PlayerNewsInfo], name: str) -> PlayerNewsInfo | None:
        matches = [p for p in players if _uniform(name) in _uniform(p.player_name)]
        self.assertEqual(len(matches), 1, f"Expected one update for {name}: {players}")
        return matches[0] if len(matches)>0 else None

    def find_absence(self, players : list[PlayerNewsInfo], name : str) -> PlayerAbsenceInfo | None:
        player = self.find_player(players, name)
        if player:
            self.assertIsInstance(player, PlayerAbsenceInfo)
            self.assertEqual(player.info_type, PlayerInfoType.ABSENCE)
            if player.info_type == PlayerInfoType.ABSENCE:
                return player
        return None

    def find_transfert(self, players : list[PlayerNewsInfo], name : str) -> PlayerTransferInfo | None:
            player = self.find_player(players, name)
            if player:
                self.assertIsInstance(player, PlayerTransferInfo)
                self.assertEqual(player.info_type, PlayerInfoType.TRANSFERT)
                if player.info_type == PlayerInfoType.TRANSFERT:
                    return player
            return None

    def test_logan_brown_transfer(self):
        players = self.extract("hc-ajoie-signs-forward-logan-brown")
        self.assertEqual(len(players), 1)
        brown = self.find_transfert(players, "Logan Brown")
        if brown:
            self.assertIn("ajoie", _uniform(brown.to_team))
            self.assertTrue(brown.confirmed)

    def test_coach_is_not_a_player_update(self):
        players = self.extract("interest-from-switzerland-in-roegles-dan-tangnes")
        self.assertEqual(players, [])

    def test_rathgeb_returns_tonight(self):
        players = self.extract("yannick-rathgeb-will-likely-play-tonight")
        self.assertEqual(len(players), 3)

        rathgeb = self.find_absence(players, "Rathgeb")
        if rathgeb:
            self.assertFalse(rathgeb.confirmed)
            self.assertTrue(rathgeb.is_return)
            self.assertIsNotNone(rathgeb.expected_duration_or_return)
            if rathgeb.expected_duration_or_return:
                self.assertIn("tonight", _uniform(rathgeb.expected_duration_or_return))
            self.assertIn("gotteron", _uniform(rathgeb.team))

        walser = self.find_absence(players, "Samuel Walser")
        if walser:
            self.assertIn("gotteron", _uniform(walser.team))

        taibel = self.find_absence(players, "Jonas Taibel")
        if taibel:
            self.assertIn("gotteron", _uniform(taibel.team))

    def test_lugano_return_and_injuries(self):
        players = self.extract(
            "mirco-mueller-in-jesper-peltonen-and-alessio-bertaggia-out-for-lugano"
        )
        mueller = self.find_absence(players, "Muller")
        if mueller:
            self.assertIn("weekend", _uniform(mueller.expected_duration_or_return))
            self.assertIn("lugano", _uniform(mueller.team))
            self.assertTrue(mueller.confirmed)

        for name in ("Jesper Peltonen", "Alessio Bertaggia"):
            with self.subTest(player=name):
                player = self.find_absence(players, name)
                if player:
                    self.assertTrue(player.confirmed)
                    self.assertIn("month", _uniform(player.expected_duration_or_return))
                    self.assertIn("lugano", _uniform(player.team))

    def test_carr_suspension_and_haas_injury(self):
        players = self.extract("hc-ajoies-daniel-carr-suspended-for-five-games")
        self.assertEqual(len(players), 2)
        carr = self.find_absence(players, "Daniel Carr")
        if carr:
            self.assertTrue(carr.confirmed)
            self.assertEqual(carr.reason,PlayerInfoType.SUSPENSION)
            self.assertIn("games", _uniform(carr.expected_duration_or_return))
            self.assertIn("ajoie", _uniform(carr.team))

        haas = self.find_absence(players, "Gaëtan Haas")
        if haas:
            self.assertTrue(haas.confirmed)
            self.assertEqual(haas.reason,PlayerInfoType.INJURY)
            self.assertIsNotNone(_uniform(haas.expected_duration_or_return))
            self.assertIn("biel", _uniform(haas.team))

    def test_biel_injuries_exclude_incidental_carr_mention(self):
        players = self.extract("ehc-biel-without-gaetan-haas-on-tuesday")
        self.assertEqual(len(players), 2)
        haas = self.find_absence(players, "Gaëtan Haas")
        if haas:
            self.assertTrue(haas.confirmed)
            self.assertIsNotNone(_uniform(haas.expected_duration_or_return))
            self.assertIn("biel", _uniform(haas.team))

        iakovenko = self.find_absence(players, "Aleksandr Iakovenko")
        if iakovenko:
            self.assertTrue(iakovenko.confirmed)
            self.assertIn("week", _uniform(iakovenko.expected_duration_or_return))
            self.assertIn("biel", _uniform(iakovenko.team))


if __name__ == "__main__":
    unittest.main(verbosity=2)
