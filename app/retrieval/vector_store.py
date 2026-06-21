from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.core.interfaces.embedding_provider import EmbeddingProvider
from app.retrieval.chunker import Chunk


class ChunkVectorStore:
    def __init__(self, embedding_provider: EmbeddingProvider, collection_name: str, persist_directory: str | None = None):
        self._store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_provider.get_embeddings(),
            persist_directory=persist_directory,
        )

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        documents = [self._chunk_to_document(chunk) for chunk in chunks]
        ids = [chunk.node_id for chunk in chunks]
        self._store.add_documents(documents=documents, ids=ids)

    def similarity_search(self, query: str, k: int = 5) -> list[dict]:
        results = self._store.similarity_search_with_score(query, k=k)
        return [self._result_to_dict(doc, score) for doc, score in results]

    def count(self) -> int:
        return self._store._collection.count()

    def _chunk_to_document(self, chunk: Chunk) -> Document:
        return Document(
            page_content=chunk.text,
            metadata={
                "node_id": chunk.node_id,
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "symbol_type": chunk.symbol_type,
                "name": chunk.name,
            },
        )

    def _result_to_dict(self, doc: Document, score: float) -> dict:
        return {
            "node_id": doc.metadata["node_id"],
            "file_path": doc.metadata["file_path"],
            "start_line": doc.metadata["start_line"],
            "end_line": doc.metadata["end_line"],
            "symbol_type": doc.metadata["symbol_type"],
            "name": doc.metadata["name"],
            "text": doc.page_content,
            "score": score,
        }