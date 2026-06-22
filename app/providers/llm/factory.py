from app.core.interfaces.llm_provider import LLMProvider
from app.providers.llm.ollama_provider import OllamaProvider
from app.providers.llm.groq_provider import GroqProvider
from app.providers.llm.openrouter_provider import OpenRouterProvider

DEFAULT_PROVIDER_NAME = "ollama"

_PROVIDERS = {
    "ollama": OllamaProvider,
    "groq": GroqProvider,
    "openrouter": OpenRouterProvider,
}


def get_llm_provider(provider_name: str = DEFAULT_PROVIDER_NAME, **kwargs) -> LLMProvider:
    if provider_name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
    return _PROVIDERS[provider_name](**kwargs)