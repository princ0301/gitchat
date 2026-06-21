import shutil
import tempfile
from pathlib import Path
from git import Repo

class RepoCloner:

    def clone(self, repo_url: str) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="ucia_"))
        Repo.clone_from(repo_url, temp_dir, depth=1)
        return temp_dir
    
    def cleanup(self, repo_path: Path) -> None:
        shutil.rmtree(repo_path, ignore_errors=True)

