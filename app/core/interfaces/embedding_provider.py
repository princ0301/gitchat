from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class EmbeddingProvider(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError