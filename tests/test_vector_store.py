import uuid

from app.retrieval.vector_store import ChunkVectorStore
from app.retrieval.chunker import Chunk
from app.providers.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider


def make_chunk(node_id: str, name: str, text: str) -> Chunk:
    return Chunk(
        node_id=node_id,
        text=text,
        file_path="sample.py",
        start_line=1,
        end_line=5,
        symbol_type="function",
        name=name,
    )


def test_add_and_search_chunks():
    provider = HuggingFaceEmbeddingProvider()
    store = ChunkVectorStore(provider, collection_name=f"test_{uuid.uuid4().hex}")

    chunks = [
        make_chunk("sample.py::add", "add", "function: add\nsignature: add(a, b)\ncode:\ndef add(a, b):\n    return a + b"),
        make_chunk("sample.py::UserRepository", "UserRepository", "class: UserRepository\ncode:\nclass UserRepository:\n    def get(self, id): pass"),
    ]
    store.add_chunks(chunks)

    assert store.count() == 2

    results = store.similarity_search("function that adds two numbers", k=1)
    assert len(results) == 1
    assert results[0]["node_id"] == "sample.py::add"


def test_search_returns_metadata_fields():
    provider = HuggingFaceEmbeddingProvider()
    store = ChunkVectorStore(provider, collection_name=f"test_{uuid.uuid4().hex}")

    chunks = [make_chunk("sample.py::add", "add", "function: add\ncode:\ndef add(a, b):\n    return a + b")]
    store.add_chunks(chunks)

    results = store.similarity_search("add function", k=1)
    result = results[0]
    assert result["file_path"] == "sample.py"
    assert result["start_line"] == 1
    assert result["end_line"] == 5
    assert result["symbol_type"] == "function"
    assert result["name"] == "add"
    assert "score" in result


def test_empty_chunks_does_not_error():
    provider = HuggingFaceEmbeddingProvider()
    store = ChunkVectorStore(provider, collection_name=f"test_{uuid.uuid4().hex}")

    store.add_chunks([])
    assert store.count() == 0