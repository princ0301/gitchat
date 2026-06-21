from dataclasses import dataclass
from pathlib import Path
import pathspec

DEFAULT_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    "target",
}

LANGUAGE_EXTENSIONS = {
    ".py": "python",
}

@dataclass(frozen=True)
class WalkedFile:
    absolute_path: Path
    relative_path: str
    language: str

class FileWalker:

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.gitignore_spec = self._load_gitignore()

    def _load_gitignore(self) -> pathspec.PathSpec | None:
        gitignore_path = self.repo_root / "./gitignore"
        if not gitignore_path.exists():
            return None
        
        lines = gitignore_path.read_text(encoding="utf-8", errors='ignore').splitlines()
        return pathspec.PathSpec.from_lines("gitignore", lines)
    
    def _is_ignored(self, relative_path: str) -> bool:
        if self.gitignore_spec and self.gitignore_spec.match_file(relative_path):
            return True
        
        parts = Path(relative_path).parts
        return any(part in DEFAULT_IGNORED_DIRS for part in parts)
    
    def walk(self) -> list[WalkedFile]:
        results = []
        for absolute_path in self.repo_root.rglob("*"):
            if not absolute_path.is_file():
                continue

            relative_path = absolute_path.relative_to(self.repo_root).as_posix()
            if self._is_ignored(relative_path):
                continue

            language = LANGUAGE_EXTENSIONS.get(absolute_path.suffix)
            if language is None:
                continue

            results.append(WalkedFile(absolute_path, relative_path, language))

        return results