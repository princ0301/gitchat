from app.ingestion.repo_cloner import RepoCloner
from app.ingestion.file_walker import FileWalker

def test_clone_and_walk_public_repo():
    cloner = RepoCloner()
    repo_path = cloner.clone("https://github.com/pallets/flask")
    try:
        walker = FileWalker(repo_path)
        files = walker.walk()
        assert len(files) > 0
        assert all(f.language == "python" for f in files)
        relative_paths = {f.relative_path for f in files}
        assert "src/flask/app.py" in relative_paths
    finally:
        cloner.cleanup(repo_path)