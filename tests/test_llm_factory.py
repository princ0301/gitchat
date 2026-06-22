import pytest

from app.providers.llm.factory import get_llm_provider
from app.providers.llm.ollama_provider import OllamaProvider
from app.providers.llm.groq_provider import GroqProvider
from app.providers.llm.openrouter_provider import OpenRouterProvider
from app.providers.llm.gemini_provider import GeminiProvider
from app.providers.llm.openai_provider import OpenAIProvider


def test_default_provider_is_ollama():
    provider = get_llm_provider()
    assert isinstance(provider, OllamaProvider)
    assert provider.provider_name == "ollama"


def test_explicit_ollama_provider():
    provider = get_llm_provider("ollama")
    assert isinstance(provider, OllamaProvider)


def test_groq_provider_requires_no_network_to_construct():
    provider = get_llm_provider("groq", api_key="fake-key-for-construction-only")
    assert isinstance(provider, GroqProvider)
    assert provider.provider_name == "groq"


def test_openrouter_provider_requires_no_network_to_construct():
    provider = get_llm_provider("openrouter", api_key="fake-key-for-construction-only")
    assert isinstance(provider, OpenRouterProvider)
    assert provider.provider_name == "openrouter"


def test_gemini_provider_requires_no_network_to_construct():
    provider = get_llm_provider("gemini", api_key="fake-key-for-construction-only")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "gemini"


def test_openai_provider_requires_no_network_to_construct():
    provider = get_llm_provider("openai", api_key="fake-key-for-construction-only")
    assert isinstance(provider, OpenAIProvider)
    assert provider.provider_name == "openai"


def test_unknown_provider_raises_value_error():
    with pytest.raises(ValueError, match="Unknown provider"):
        get_llm_provider("not_a_real_provider")


def test_provider_returns_chat_model_implementing_base_chat_model():
    from langchain_core.language_models.chat_models import BaseChatModel

    provider = get_llm_provider("ollama")
    chat_model = provider.get_chat_model()
    assert isinstance(chat_model, BaseChatModel)


def test_custom_model_name_passed_through():
    provider = get_llm_provider("ollama", model_name="custom-model")
    assert provider.model_name == "custom-model"
