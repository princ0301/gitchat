from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class LLMProvider(ABC):
    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        raise NotImplementedError
    
    