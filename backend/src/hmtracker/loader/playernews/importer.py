import logging
from collections.abc import Callable

from hmtracker.database.models import PlayerNews
from hmtracker.database.repository import RepositorySession
from hmtracker.loader.playernews.extractor import ArticlePlayerNews, extract_player_news
from hmtracker.parser.models import ArticleDetails
from hmtracker.parser.shnparser import SwissHockeyNewsParser


def import_player_news(
    repository_session: RepositorySession,
    extractor: Callable[[ArticleDetails], ArticlePlayerNews] = extract_player_news,
) -> int:
    """Commit each successful article independently and log failed articles."""
    parser = SwissHockeyNewsParser()
    try:
        urls = list(dict.fromkeys(article.url for article in parser.list_news()))
        new_urls = repository_session.filter_new_player_news_urls(urls)
        count = 0
        failed_count = 0
        for url in new_urls:
            try:
                article = parser.article_details(url)
                extracted = extractor(article)
                records = [
                    PlayerNews(
                        source=url,
                        news_date=article.date,
                        title=article.title,
                        **player.model_dump(),
                    )
                    for player in extracted.players
                ]
                repository_session.session.add_all(records)
                repository_session.session.commit()
            except Exception:
                repository_session.session.rollback()
                failed_count += 1
                logging.exception("Failed to import player news from %s; skipping", url)
                continue
            count += len(records)
        logging.info(
            "Loaded %s player news records from %s new articles; %s articles failed",
            count,
            len(new_urls) - failed_count,
            failed_count,
        )
        return count
    finally:
        parser.close()
