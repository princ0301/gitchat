from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.interfaces.llm_provider import LLMProvider

DEFAULT_MODEL_NAME = "qwen3-coder:480b-cloud"
DEFAULT_BASE_URL = "http://localhost:11434"


class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, base_url: str = DEFAULT_BASE_URL, temperature: float = 0.0):
        self._model_name = model_name
        self._chat_model = ChatOllama(model=model_name, base_url=base_url, temperature=temperature)

    def get_chat_model(self) -> BaseChatModel:
        return self._chat_model

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model_name
