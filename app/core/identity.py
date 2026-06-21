from pathlib import Path


def normalize_path(file_path: str, repo_root: str) -> str:
    relative = Path(file_path).relative_to(Path(repo_root))
    return relative.as_posix()


def build_node_id(file_path: str, qualified_name: str) -> str:
    return f"{file_path}::{qualified_name}"


def build_qualified_name(name: str, parent_name: str | None) -> str:
    if parent_name:
        return f"{parent_name}.{name}"
    return name


def parse_node_id(node_id: str) -> tuple[str, str]:
    file_path, qualified_name = node_id.split("::", 1)
    return file_path, qualified_name