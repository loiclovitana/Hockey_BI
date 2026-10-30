from urllib.parse import urlsplit, urlunsplit


def split_article_url(url: str) -> tuple[str, str]:
    """Split an absolute article URL into its origin and relative reference."""
    parsed = urlsplit(url)
    return (
        f"{parsed.scheme}://{parsed.netloc}",
        urlunsplit(("", "", parsed.path, parsed.query, parsed.fragment)),
    )
