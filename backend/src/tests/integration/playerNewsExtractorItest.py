import json
import unittest
from pathlib import Path
from unicodedata import normalize, category as uniform_category

from hmtracker.database.models import PlayerInfoType
from pydantic_ai import capture_run_messages
from pydantic_ai.messages import ModelMessagesTypeAdapter

from hmtracker.loader.playernews.extractor import ArticlePlayerNews, extract_player_news
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

    def player(self, players, name):
        matches = [p for p in players if _uniform(name) in _uniform(p.player_name)]
        self.assertEqual(len(matches), 1, f"Expected one update for {name}: {players}")
        return matches[0]

    def test_logan_brown_transfer(self):
        players = self.extract("hc-ajoie-signs-forward-logan-brown")
        self.assertEqual(len(players), 1)
        brown = self.player(players, "Logan Brown")
        self.assertEqual(brown.info_type, PlayerInfoType.TRANSFERT)
        if brown.info_type == PlayerInfoType.TRANSFERT:
            self.assertIn("ajoie", _uniform(brown.to_team))
        self.assertFalse(brown.rumor)

    def test_coach_is_not_a_player_update(self):
        players = self.extract("interest-from-switzerland-in-roegles-dan-tangnes")
        self.assertEqual(players, [])

    def test_rathgeb_returns_tonight(self):
        players = self.extract("yannick-rathgeb-will-likely-play-tonight")
        self.assertEqual(len(players), 3)

        rathgeb = self.player(players, "Rathgeb")
        self.assertIn(
            rathgeb.info_type,
            [PlayerInfoType.RETURN, PlayerInfoType.INJURY, PlayerInfoType.ABSENCE],
        )
        if rathgeb.info_type == PlayerInfoType.RETURN:
            self.assertIn("tonight", rathgeb.return_time.casefold())
            self.assertIn("gotteron", _uniform(rathgeb.team))
        elif (
            rathgeb.info_type == PlayerInfoType.INJURY
            or rathgeb.info_type == PlayerInfoType.ABSENCE
        ):
            self.assertIn("tonight", rathgeb.expected_return.casefold())
            self.assertIn("gotteron", _uniform(rathgeb.team))

        walser = self.player(players, "Samuel Walser")
        self.assertIn(walser.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE])
        if (
            walser.info_type == PlayerInfoType.INJURY
            or walser.info_type == PlayerInfoType.ABSENCE
        ):
            self.assertFalse(walser.rumor)
            self.assertIn("unknown", walser.expected_return.casefold())
            self.assertIn("gotteron", _uniform(walser.team))

        taibel = self.player(players, "Jonas Taibel")
        self.assertIn(taibel.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE])
        if (
            taibel.info_type == PlayerInfoType.INJURY
            or taibel.info_type == PlayerInfoType.ABSENCE
        ):
            self.assertFalse(taibel.rumor)
            self.assertIn("unknown", taibel.expected_return.casefold())
            self.assertIn("gotteron", _uniform(taibel.team))

    def test_lugano_return_and_injuries(self):
        players = self.extract(
            "mirco-mueller-in-jesper-peltonen-and-alessio-bertaggia-out-for-lugano"
        )
        mueller = self.player(players, "Müller")
        self.assertIn(
            mueller.info_type,
            [PlayerInfoType.RETURN, PlayerInfoType.INJURY, PlayerInfoType.ABSENCE],
        )
        if mueller.info_type == PlayerInfoType.RETURN:
            self.assertIn("weekend", mueller.return_time.casefold())
            self.assertIn("lugano", _uniform(mueller.team))
        elif (
            mueller.info_type == PlayerInfoType.INJURY
            or mueller.info_type == PlayerInfoType.ABSENCE
        ):
            self.assertIn("weekend", mueller.expected_return.casefold())
            self.assertIn("lugano", _uniform(mueller.team))
        self.assertFalse(mueller.rumor)

        for name in ("Jesper Peltonen", "Alessio Bertaggia"):
            with self.subTest(player=name):
                player = self.player(players, name)
                self.assertIn(
                    player.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE]
                )
                if player.info_type in (PlayerInfoType.INJURY, PlayerInfoType.ABSENCE):
                    self.assertFalse(player.rumor)
                    self.assertIn("month", player.expected_return.casefold())
                    self.assertIn("lugano", _uniform(player.team))

    def test_carr_suspension_and_haas_injury(self):
        players = self.extract("hc-ajoies-daniel-carr-suspended-for-five-games")
        self.assertEqual(len(players), 2)
        carr = self.player(players, "Daniel Carr")
        self.assertEqual(carr.info_type, PlayerInfoType.SUSPENSION)
        if carr.info_type == PlayerInfoType.SUSPENSION:
            self.assertFalse(carr.rumor)
            self.assertIn("games", carr.expected_return.casefold())
            self.assertIn("ajoie", _uniform(carr.team))

        haas = self.player(players, "Gaëtan Haas")
        self.assertIn(haas.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE])
        if haas.info_type in (PlayerInfoType.INJURY, PlayerInfoType.ABSENCE):
            self.assertFalse(haas.rumor)
            self.assertIn("indefinite", haas.expected_return.casefold())
            self.assertIn("biel", _uniform(haas.team))

    def test_biel_injuries_exclude_incidental_carr_mention(self):
        players = self.extract("ehc-biel-without-gaetan-haas-on-tuesday")
        self.assertEqual(len(players), 2)
        haas = self.player(players, "Gaëtan Haas")
        self.assertIn(haas.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE])
        if haas.info_type in (PlayerInfoType.INJURY, PlayerInfoType.ABSENCE):
            self.assertFalse(haas.rumor)
            self.assertIn("further notice", haas.expected_return.casefold())
            self.assertIn("biel", _uniform(haas.team))

        iakovenko = self.player(players, "Aleksandr Iakovenko")
        self.assertIn(
            iakovenko.info_type, [PlayerInfoType.INJURY, PlayerInfoType.ABSENCE]
        )
        if iakovenko.info_type in (PlayerInfoType.INJURY, PlayerInfoType.ABSENCE):
            self.assertFalse(iakovenko.rumor)
            self.assertIn("week", iakovenko.expected_return.casefold())
            self.assertIn("biel", _uniform(iakovenko.team))


if __name__ == "__main__":
    unittest.main(verbosity=2)
