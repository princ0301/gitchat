from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings

from app.core.interfaces.embedding_provider import EmbeddingProvider

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_DIMENSION = 384


class HuggingFaceEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, dimension: int = DEFAULT_DIMENSION):
        self._model_name = model_name
        self._dimension = dimension
        self._embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def get_embeddings(self) -> Embeddings:
        return self._embeddings

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def dimension(self) -> int:
        return self._dimension