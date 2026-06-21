from app.ingestion.repo_cloner import RepoCloner
from app.ingestion.file_walker import FileWalker
from app.parsing.languages.python_parser import PythonParser
from app.graph.builder import GraphBuilder
from app.graph.networkx_store import NetworkXGraphStore
from app.core.types import EdgeType
from app.core.identity import build_node_id

def test_full_pipeline_on_flask():
    cloner = RepoCloner()
    repo_path = cloner.clone("https://github.com/pallets/flask")
    try:
        walker = FileWalker(repo_path)
        files = walker.walk()
        parser = PythonParser()

        parse_results = []
        for f in files:
            source_code = f.absolute_path.read_text(encoding="utf-8", errors="ignore")
            parse_results.append(parser.parse(f.relative_path, source_code))

        builder = GraphBuilder(NetworkXGraphStore())
        store = builder.build(parse_results)

        print(f"total nodes: {store.node_count()}")
        print(f"total edges: {store.edge_count()}")

        assert store.node_count() > 0
        assert store.edge_count() > 0

        add_url_rule_id = build_node_id("src/flask/app.py", "Flask.add_url_rule")
        if store.has_node(add_url_rule_id):
            callers = store.get_callers(add_url_rule_id)
            print(f"callers of Flask.add_url_rule: {len(callers)}")
            for c in callers[:5]:
                print(" -", c)
    finally:
        cloner.cleanup(repo_path)