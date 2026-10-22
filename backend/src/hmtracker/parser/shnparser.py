"""Parse Swiss Hockey News using HTML requests only, without loading page assets."""

from datetime import date, datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag

from hmtracker.parser.models import ArticleDetails, ArticleSummary

SHN_URL = "https://swisshockeynews.ch"
NEWS_URL = SHN_URL + "/en/national-league"


class SwissHockeyNewsParser:
    def __init__(self, timeout: float = 15) -> None:
        self.session = requests.Session()
        self.timeout = timeout

    def list_news(self) -> list[ArticleSummary]:
        """Return unique front-page articles with title, URL and publication date.

        Only the National League page is fetched; article pages are not visited.
        """
        return _scrap_news_list(self._get_html(NEWS_URL))

    def article_details(self, url: str) -> ArticleDetails:
        """Return publication date, title, introduction and plain article text."""
        return _scrap_article_details(self._get_html(urljoin(SHN_URL, url)))

    def close(self) -> None:
        self.session.close()

    def _get_html(self, url: str) -> str:
        with self.session.get(url, timeout=self.timeout) as response:
            response.raise_for_status()
            return response.text


def _text(element: Tag | None) -> str:
    return " ".join(element.get_text().split()) if element else ""


def _scrap_news_list(html: str) -> list[ArticleSummary]:
    # Avoid building trees for navigation, advertising and unrelated sidebars.
    soup = BeautifulSoup(
        html,
        "html.parser",
        parse_only=SoupStrainer(
            "div", class_=lambda value: value and "national-league" in value.split()
        ),
    )
    articles = []
    seen = set()
    for article in soup.select("article"):
        link = article.select_one(".raxo-title a[href]")
        published = article.select_one(".raxo-date")
        if link is None or published is None:
            continue
        url = str(link["href"]).strip()
        if url in seen:
            continue
        seen.add(url)
        articles.append(
            ArticleSummary(
                title=_text(link),
                url=url,
                date=datetime.strptime(_text(published), "%d.%m.%Y").date(),
            )
        )
    return articles


def _scrap_article_details(html: str) -> ArticleDetails:
    soup = BeautifulSoup(
        html,
        "html.parser",
        parse_only=SoupStrainer(
            "div", class_=lambda value: value and "com-content-article" in value.split()
        ),
    )
    title = soup.select_one("h1")
    published = soup.select_one('time[itemprop="datePublished"][datetime]')
    body = soup.select_one('[itemprop="articleBody"]')
    if title is None or published is None or body is None:
        raise ValueError("Swiss Hockey News page is missing article details")

    for element in body.select("script, style, iframe, figure, .credit"):
        element.decompose()
    # Preserve paragraph boundaries and inline punctuation without retaining HTML.
    for element in body.select("p, li, h2, h3, h4, blockquote, br"):
        element.insert_after("\n")
    text = "\n\n".join(
        " ".join(line.split()) for line in body.get_text().splitlines() if line.strip()
    )
    return ArticleDetails(
        date=date.fromisoformat(str(published["datetime"]).split("T")[0]),
        title=_text(title),
        description=_text(soup.select_one(".introtext")),
        text=text,
    )
