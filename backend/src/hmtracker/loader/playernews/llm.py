"""Shared model configuration for player news extraction and matching."""

from os import getenv
from pydantic import BaseModel
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import (
    OpenAIChatModel,
    OpenAIResponsesModel,
    OpenAIResponsesModelSettings,
)
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider


def create_news_agent[OutputT: BaseModel](
    output_type: type[OutputT], instructions: str
) -> Agent[None, OutputT]:
    provider_name = (getenv("HM_PLAYER_NEWS_PROVIDER") or "openai").strip().lower()
    model_name = (getenv("HM_PLAYER_NEWS_MODEL") or "").strip()
    model: OpenAIChatModel | OpenAIResponsesModel

    if provider_name == "openai":
        api_key = getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required to process player news")
        model = OpenAIResponsesModel(
            model_name or "gpt-6-luna",
            provider=OpenAIProvider(
                api_key=api_key,
                base_url=getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1",
            ),
            settings=OpenAIResponsesModelSettings(openai_store=False),
        )
    elif provider_name == "ollama":
        if not model_name:
            raise ValueError("HM_PLAYER_NEWS_MODEL is required for Ollama")
        provider = OllamaProvider(
            base_url=getenv("OLLAMA_BASE_URL") or "http://localhost:11434/v1",
        )
        profile = OpenAIModelProfile.from_profile(provider.model_profile(model_name))
        # Pydantic AI 1.60 does not advertise Ollama's JSON schema support.
        profile.supports_json_schema_output = True
        model = OpenAIChatModel(
            model_name,
            provider=provider,
            profile=profile,
        )
    else:
        raise ValueError("HM_PLAYER_NEWS_PROVIDER must be 'openai' or 'ollama'")

    return Agent(
        model,
        output_type=NativeOutput(output_type),
        model_settings={"timeout": 120},
        instructions=instructions,
    )
