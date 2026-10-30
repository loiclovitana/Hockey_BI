"""Typed article data returned by news parsers."""

from datetime import date as Date

from pydantic import BaseModel, ConfigDict


class ArticleSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: str
    date: Date


class ArticleDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Date
    title: str
    description: str
    text: str

    def to_markdown(self) -> str:
        """Render the article content without publication metadata."""
        return f"""# {self.title}
        
## Introduction

{self.description}

## Article

{self.text}
"""
