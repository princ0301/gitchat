from app.ingestion.repo_cloner import RepoCloner
from app.ingestion.file_walker import FileWalker
from app.parsing.languages.python_parser import PythonParser


def test_parse_real_flask_file():
    cloner = RepoCloner()
    repo_path = cloner.clone("https://github.com/pallets/flask")
    try:
        walker = FileWalker(repo_path)
        files = walker.walk()
        target = next(f for f in files if f.relative_path == "src/flask/app.py")
        source_code = target.absolute_path.read_text(encoding="utf-8")

        parser = PythonParser()
        result = parser.parse(target.relative_path, source_code)

        assert len(result.symbols) > 0
        assert len(result.calls) > 0
        assert any(s.name == "Flask" for s in result.symbols)

        print(f"symbols: {len(result.symbols)}")
        print(f"calls: {len(result.calls)}")
        print(f"imports: {len(result.imports)}")
    finally:
        cloner.cleanup(repo_path)