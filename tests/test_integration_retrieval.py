from app.ingestion.repo_cloner import RepoCloner
from app.ingestion.file_walker import FileWalker
from app.parsing.languages.python_parser import PythonParser
from app.graph.builder import GraphBuilder
from app.graph.networkx_store import NetworkXGraphStore
from app.retrieval.chunker import SymbolChunker
from app.retrieval.vector_store import ChunkVectorStore
from app.retrieval.hybrid_retriever import HybridRetriever
from app.providers.embeddings.huggingface_provider import HuggingFaceEmbeddingProvider


def test_full_retrieval_pipeline_on_flask():
    cloner = RepoCloner()
    repo_path = cloner.clone("https://github.com/pallets/flask")
    try:
        walker = FileWalker(repo_path)
        files = walker.walk()
        parser = PythonParser()

        parse_results = []
        source_lines_by_file = {}
        for f in files:
            source_code = f.absolute_path.read_text(encoding="utf-8", errors="ignore")
            parse_results.append(parser.parse(f.relative_path, source_code))
            source_lines_by_file[f.relative_path] = source_code.splitlines()

        builder = GraphBuilder(NetworkXGraphStore())
        graph_store = builder.build(parse_results)

        all_symbols = [s for result in parse_results for s in result.symbols]
        chunker = SymbolChunker()
        chunks = chunker.chunk_all(all_symbols, source_lines_by_file, builder.get_node_id_for_symbol)

        provider = HuggingFaceEmbeddingProvider()
        vector_store = ChunkVectorStore(provider, collection_name="flask_test")
        vector_store.add_chunks(chunks)

        print(f"total chunks embedded: {len(chunks)}")

        retriever = HybridRetriever(graph_store, vector_store)
        results = retriever.retrieve("how does flask handle url routing", vector_k=5, expansion_hops=1)

        print(f"total retrieval results: {len(results)}")
        for r in results[:10]:
            print(f"{r.source} | {r.relevance_score:.3f} | {r.node_id}")

        assert len(results) > 0
        vector_sourced = [r for r in results if r.source in ("vector", "both")]
        assert len(vector_sourced) > 0
    finally:
        cloner.cleanup(repo_path)