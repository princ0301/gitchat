import uuid

from langchain_core.embeddings import Embeddings

from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.vector_store import ChunkVectorStore
from app.retrieval.chunker import Chunk
from app.graph.networkx_store import NetworkXGraphStore
from app.core.types import Symbol, SymbolType, EdgeType


class FakeEmbeddings(Embeddings):
    def __init__(self, vectors: dict[str, list[float]]):
        self._vectors = vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vectors.get(t, [0.0, 0.0, 0.0]) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vectors.get(text, [0.0, 0.0, 0.0])


class FakeEmbeddingProvider:
    def __init__(self, embeddings: Embeddings):
        self._embeddings = embeddings

    def get_embeddings(self) -> Embeddings:
        return self._embeddings


def make_symbol(name: str, file_path: str = "sample.py") -> Symbol:
    return Symbol(
        symbol_type=SymbolType.FUNCTION,
        name=name,
        file_path=file_path,
        start_line=1,
        end_line=5,
    )


def build_graph_store():
    store = NetworkXGraphStore()
    store.add_node("sample.py::login", make_symbol("login"))
    store.add_node("sample.py::authenticate", make_symbol("authenticate"))
    store.add_node("sample.py::hash_password", make_symbol("hash_password"))
    store.add_node("sample.py::unrelated", make_symbol("unrelated"))
    store.add_edge("sample.py::login", "sample.py::authenticate", EdgeType.CALLS)
    store.add_edge("sample.py::authenticate", "sample.py::hash_password", EdgeType.CALLS)
    return store


def build_vector_store(query_text: str):
    chunk_text = "function: login\ncode:\ndef login(): authenticate()"
    fake_vectors = {
        query_text: [1.0, 0.0, 0.0],
        chunk_text: [1.0, 0.0, 0.0],
    }
    embeddings = FakeEmbeddings(fake_vectors)
    provider = FakeEmbeddingProvider(embeddings)
    store = ChunkVectorStore(provider, collection_name=f"test_{uuid.uuid4().hex}")
    chunk = Chunk(
        node_id="sample.py::login",
        text=chunk_text,
        file_path="sample.py",
        start_line=1,
        end_line=5,
        symbol_type="function",
        name="login",
    )
    store.add_chunks([chunk])
    return store


def test_vector_hit_included_in_results():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=0)

    node_ids = {r.node_id for r in results}
    assert "sample.py::login" in node_ids
    login_result = next(r for r in results if r.node_id == "sample.py::login")
    assert login_result.source == "vector"
    assert login_result.vector_score is not None


def test_graph_expansion_includes_neighbors():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=1)

    node_ids = {r.node_id for r in results}
    assert "sample.py::authenticate" in node_ids
    auth_result = next(r for r in results if r.node_id == "sample.py::authenticate")
    assert auth_result.source == "graph"
    assert auth_result.graph_distance == 1


def test_multi_hop_expansion_reaches_further_nodes():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=2)

    node_ids = {r.node_id for r in results}
    assert "sample.py::hash_password" in node_ids
    hash_result = next(r for r in results if r.node_id == "sample.py::hash_password")
    assert hash_result.graph_distance == 2


def test_unrelated_node_not_included():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=2)

    node_ids = {r.node_id for r in results}
    assert "sample.py::unrelated" not in node_ids


def test_results_ranked_by_relevance_descending():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=2)

    scores = [r.relevance_score for r in results]
    assert scores == sorted(scores, reverse=True)


def build_two_strength_vector_store(query_text: str):
    strong_chunk_text = "function: login\ncode:\ndef login(): authenticate()"
    weak_chunk_text = "function: render_page\ncode:\ndef render_page(): format_output()"
    fake_vectors = {
        query_text: [1.0, 0.0, 0.0],
        strong_chunk_text: [0.95, 0.05, 0.0],
        weak_chunk_text: [0.2, 0.8, 0.0],
    }
    embeddings = FakeEmbeddings(fake_vectors)
    provider = FakeEmbeddingProvider(embeddings)
    store = ChunkVectorStore(provider, collection_name=f"test_{uuid.uuid4().hex}")
    chunks = [
        Chunk(
            node_id="sample.py::login",
            text=strong_chunk_text,
            file_path="sample.py",
            start_line=1,
            end_line=5,
            symbol_type="function",
            name="login",
        ),
        Chunk(
            node_id="sample.py::render_page",
            text=weak_chunk_text,
            file_path="sample.py",
            start_line=10,
            end_line=15,
            symbol_type="function",
            name="render_page",
        ),
    ]
    store.add_chunks(chunks)
    return store


def build_two_branch_graph_store():
    store = NetworkXGraphStore()
    store.add_node("sample.py::login", make_symbol("login"))
    store.add_node("sample.py::authenticate", make_symbol("authenticate"))
    store.add_node("sample.py::render_page", make_symbol("render_page"))
    store.add_node("sample.py::format_output", make_symbol("format_output"))
    store.add_edge("sample.py::login", "sample.py::authenticate", EdgeType.CALLS)
    store.add_edge("sample.py::render_page", "sample.py::format_output", EdgeType.CALLS)
    return store


def test_graph_relevance_decays_with_hop_distance():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=2)

    by_id = {r.node_id: r for r in results}
    hop_one_score = by_id["sample.py::authenticate"].relevance_score
    hop_two_score = by_id["sample.py::hash_password"].relevance_score
    assert hop_one_score > hop_two_score


def test_neighbors_of_strong_match_outrank_neighbors_of_weak_match():
    query = "how does login work"
    vector_store = build_two_strength_vector_store(query)
    graph_store = build_two_branch_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=2, expansion_hops=1)

    by_id = {r.node_id: r for r in results}
    strong_neighbor_score = by_id["sample.py::authenticate"].relevance_score
    weak_neighbor_score = by_id["sample.py::format_output"].relevance_score
    assert strong_neighbor_score > weak_neighbor_score


def test_not_all_graph_results_have_identical_relevance():
    query = "how does login work"
    vector_store = build_two_strength_vector_store(query)
    graph_store = build_two_branch_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=2, expansion_hops=1)

    graph_results = [r for r in results if r.source == "graph"]
    scores = {r.relevance_score for r in graph_results}
    assert len(scores) > 1


def test_zero_expansion_hops_returns_only_vector_hits():
    query = "how does login work"
    vector_store = build_vector_store(query)
    graph_store = build_graph_store()

    retriever = HybridRetriever(graph_store, vector_store)
    results = retriever.retrieve(query, vector_k=1, expansion_hops=0)

    assert len(results) == 1
    assert results[0].node_id == "sample.py::login"