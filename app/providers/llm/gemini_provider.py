from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.interfaces.llm_provider import LLMProvider

DEFAULT_MODEL_NAME = "gemini-2.5-flash"


class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, temperature: float = 0.0, api_key: str | None = None):
        self._model_name = model_name
        self._chat_model = ChatGoogleGenerativeAI(model=model_name, temperature=temperature, api_key=api_key)

    def get_chat_model(self) -> BaseChatModel:
        return self._chat_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name
