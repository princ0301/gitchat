from app.providers.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider


def test_provider_name_and_dimension():
    provider = HuggingFaceEmbeddingProvider()
    assert provider.provider_name == "huggingface"
    assert provider.dimension == 384


def test_embeds_single_text():
    provider = HuggingFaceEmbeddingProvider()
    embeddings = provider.get_embeddings()
    vector = embeddings.embed_query("def add(a, b): return a + b")

    assert len(vector) == 384
    assert all(isinstance(x, float) for x in vector)


def test_embeds_multiple_documents():
    provider = HuggingFaceEmbeddingProvider()
    embeddings = provider.get_embeddings()
    vectors = embeddings.embed_documents([
        "def add(a, b): return a + b",
        "class UserRepository: pass",
    ])

    assert len(vectors) == 2
    assert len(vectors[0]) == 384


def test_similar_code_has_higher_similarity_than_unrelated():
    import math

    provider = HuggingFaceEmbeddingProvider()
    embeddings = provider.get_embeddings()

    query_vec = embeddings.embed_query("function that adds two numbers")
    similar_vec = embeddings.embed_query("def add(a, b): return a + b")
    unrelated_vec = embeddings.embed_query("class DatabaseConnectionPool: pass")

    def cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b)

    sim_similar = cosine_sim(query_vec, similar_vec)
    sim_unrelated = cosine_sim(query_vec, unrelated_vec)

    assert sim_similar > sim_unrelated