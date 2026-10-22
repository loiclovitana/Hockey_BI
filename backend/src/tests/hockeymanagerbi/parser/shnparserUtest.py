import unittest
from unittest.mock import patch

import requests

from hmtracker.parser import shnparser


NEWS_HTML = """
<nav><a href="/en/national-league">National League</a></nav>
<div class="national-league no-card">
    <article class="raxo-item-top">
        <img src="/images/hero.jpg">
        <h2 class="raxo-title"><a href="/en/shn/first"> First &amp; latest </a></h2>
        <span class="raxo-date">22.10.2026</span>
    </article>
</div>
<div class="national-league card">
    <article class="raxo-hero-item">
        <h3 class="raxo-title">
            <a href="https://swisshockeynews.ch/en/shn/first">First &amp; latest</a>
        </h3>
        <span class="raxo-date">22.10.2026</span>
    </article>
</div>
<div class="national-league no-card">
    <article class="raxo-item-nor">
        <h4 class="raxo-title"><a href="/en/shn/second">Second story</a></h4>
        <span class="raxo-date">21.10.2026</span>
    </article>
    <article><img src="/images/advertisement.jpg"></article>
</div>
<aside>
    <article>
        <h4 class="raxo-title"><a href="/en/shb/podcast">Unrelated podcast</a></h4>
        <span class="raxo-date">20.10.2026</span>
    </article>
</aside>
"""

ARTICLE_HTML = """
<div class="com-content-article item-page">
    <h1 itemprop="headline"> A player's return &amp; recovery </h1>
    <div class="introtext"><div class="article"><p>A <i>short</i> introduction.</p></div></div>
    <time itemprop="dateModified" datetime="2026-10-23T10:00:00+02:00">Updated</time>
    <time itemprop="datePublished" datetime="2026-10-22T20:11:47+02:00">Published</time>
    <div class="photo-container"><img src="/images/player.jpg">Photo credit</div>
    <div itemprop="articleBody" class="com-content-article__body">
        <div class="article"><p>The <a href="/team">player</a>, now healthy, returns.</p><p>He will play on Friday.</p>
        <script>loadAdvertisement()</script>
        <style>.advertisement { display: block; }</style>
        <iframe src="https://example.com/video">Embedded video</iframe>
        <figure><img src="/images/extra.jpg"><figcaption>Image caption</figcaption></figure>
        <div class="credit">(22 October 2026 | author)</div></div>
    </div>
</div>
<aside>Trending articles</aside>
"""


class TestSwissHockeyNewsParser(unittest.TestCase):
    def test_scrap_news_list(self):
        result = shnparser._scrap_news_list(NEWS_HTML)

        self.assertEqual(
            [
                {
                    "title": "First & latest",
                    "url": "https://swisshockeynews.ch/en/shn/first",
                    "date": "2026-10-22",
                },
                {
                    "title": "Second story",
                    "url": "https://swisshockeynews.ch/en/shn/second",
                    "date": "2026-10-21",
                },
            ],
            result,
        )

    def test_scrap_empty_news_list(self):
        self.assertEqual([], shnparser._scrap_news_list("<div>No news</div>"))

    def test_scrap_article_details(self):
        result = shnparser._scrap_article_details(ARTICLE_HTML)

        self.assertEqual(
            {
                "date": "2026-10-22",
                "title": "A player's return & recovery",
                "description": "A short introduction.",
                "text": "The player, now healthy, returns.\n\nHe will play on Friday.",
            },
            result,
        )

    def test_scrap_invalid_article(self):
        with self.assertRaisesRegex(ValueError, "missing article details"):
            shnparser._scrap_article_details("<div>Article not found</div>")

    def test_methods_only_request_the_requested_html(self):
        parser = shnparser.SwissHockeyNewsParser(timeout=10)
        self.addCleanup(parser.close)
        with patch.object(parser.session, "get") as get:
            response = get.return_value.__enter__.return_value
            response.text = NEWS_HTML

            self.assertEqual(2, len(parser.list_news()))
            get.assert_called_once_with(shnparser.NEWS_URL, timeout=10)
            response.raise_for_status.assert_called_once_with()

            get.reset_mock()
            response.text = ARTICLE_HTML

            self.assertEqual(
                "2026-10-22", parser.article_details("/en/shn/first")["date"]
            )
            get.assert_called_once_with(
                "https://swisshockeynews.ch/en/shn/first", timeout=10
            )

    def test_http_errors_are_propagated(self):
        parser = shnparser.SwissHockeyNewsParser()
        self.addCleanup(parser.close)
        with patch.object(parser.session, "get") as get:
            response = get.return_value.__enter__.return_value
            response.raise_for_status.side_effect = requests.HTTPError("503")
            with self.assertRaises(requests.HTTPError):
                parser.list_news()
            with self.assertRaises(requests.HTTPError):
                parser.article_details("/en/shn/first")


if __name__ == "__main__":
    unittest.main()
