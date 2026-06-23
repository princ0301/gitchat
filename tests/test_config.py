import importlib

from app.config import Settings


def test_default_settings_use_ollama():
    settings = Settings(_env_file=None)
    assert settings.llm_provider == "ollama"
    assert settings.ollama_model == "qwen3-coder:480b-cloud"


def test_default_api_keys_are_none_when_unset():
    settings = Settings(_env_file=None)
    assert settings.groq_api_key is None
    assert settings.gemini_api_key is None
    assert settings.openai_api_key is None


def test_env_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_MODEL", "custom-groq-model")
    monkeypatch.setenv("GROQ_API_KEY", "test-key-123")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "groq"
    assert settings.groq_model == "custom-groq-model"
    assert settings.groq_api_key == "test-key-123"


def test_factory_uses_overridden_settings(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "custom-local-model")

    import app.config
    importlib.reload(app.config)
    import app.providers.llm.factory
    importlib.reload(app.providers.llm.factory)

    provider = app.providers.llm.factory.get_llm_provider("ollama")
    assert provider.model_name == "custom-local-model"

    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    importlib.reload(app.config)
    importlib.reload(app.providers.llm.factory)
