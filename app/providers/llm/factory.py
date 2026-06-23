from app.core.interfaces.llm_provider import LLMProvider
from app.providers.llm.ollama_provider import OllamaProvider
from app.providers.llm.groq_provider import GroqProvider
from app.providers.llm.openrouter_provider import OpenRouterProvider
from app.providers.llm.gemini_provider import GeminiProvider
from app.providers.llm.openai_provider import OpenAIProvider
from app.config import settings

_PROVIDERS = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
}


def _default_kwargs_for(provider_name: str) -> dict:
    if provider_name == "ollama":
        return {"model_name": settings.ollama_model, "base_url": settings.ollama_base_url}
    if provider_name == "groq":
        return {"model_name": settings.groq_model, "api_key": settings.groq_api_key}
    if provider_name == "openrouter":
        return {"model_name": settings.openrouter_model, "api_key": settings.openrouter_api_key}
    if provider_name == "gemini":
        return {"model_name": settings.gemini_model, "api_key": settings.gemini_api_key}
    if provider_name == "openai":
        return {"model_name": settings.openai_model, "api_key": settings.openai_api_key}
    return {}


def get_llm_provider(provider_name: str | None = None, **overrides) -> LLMProvider:
    resolved_name = provider_name or settings.llm_provider
    if resolved_name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {resolved_name}. Available: {available}")

    kwargs = _default_kwargs_for(resolved_name)
    kwargs.update(overrides)
    return _PROVIDERS[resolved_name](**kwargs)
