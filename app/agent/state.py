from typing import TypedDict
from langchain_core.messages import BaseMessage

from app.core.types import RetrievalResult


class AgentState(TypedDict):
    query: str
    chat_history: list[BaseMessage]
    repo_id: str
    intent: str
    retrieval_results: list[RetrievalResult]
    answer: str
    confidence: float
    retrieval_attempts: int
    vector_k: int
    expansion_hops: int