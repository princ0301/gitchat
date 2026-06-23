from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: str = "ollama"

    ollama_model: str = "qwen3-coder:480b-cloud"
    ollama_base_url: str = "http://localhost:11434"

    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    openrouter_api_key: str | None = None
    openrouter_model: str = "openai/gpt-4o-mini"

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384


settings = Settings()
