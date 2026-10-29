import logging
from collections.abc import Callable

from hmtracker.database.models import PlayerNews
from hmtracker.database.repository import RepositorySession
from hmtracker.loader.playernews.extractor import (
    ArticlePlayerNews,
    PlayerNewsInfo,
    PlayerTransferInfo,
    extract_player_news,
)
from hmtracker.database.models import PlayerInfoType
from hmtracker.parser.models import ArticleDetails
from hmtracker.parser.shnparser import SwissHockeyNewsParser


def _to_player_news(
    player: PlayerNewsInfo, article: ArticleDetails, source: str
) -> PlayerNews:
    info_type: PlayerInfoType
    if isinstance(player, PlayerTransferInfo):
        info_type = player.info_type
        current_team = player.from_team
        new_team = player.to_team
        availability_time = player.transfer_time
    else:
        info_type = (
            PlayerInfoType.RETURN
            if player.is_return
            else player.reason or player.info_type
        )
        current_team = player.team
        new_team = None
        availability_time = player.expected_duration_or_return

    return PlayerNews(
        source=source,
        news_date=article.date,
        title=article.title,
        player_name=player.player_name,
        confirmed=player.confirmed,
        info_type=info_type,
        current_team=current_team,
        new_team=new_team,
        availability_time=availability_time,
    )


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
                    _to_player_news(player, article, url)
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
