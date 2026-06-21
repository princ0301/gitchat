from dataclasses import dataclass
from enum import Enum


class SymbolType(str, Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"


class EdgeType(str, Enum):
    CONTAINS = "contains"
    CALLS = "calls"
    IMPORTS = "imports"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    INSTANTIATES = "instantiates"
    REFERENCES = "references"


@dataclass(frozen=True)
class Symbol:
    symbol_type: SymbolType
    name: str
    file_path: str
    start_line: int
    end_line: int
    parent_name: str | None = None
    signature: str | None = None
    docstring: str | None = None


@dataclass(frozen=True)
class CallReference:
    caller_name: str
    callee_name: str
    file_path: str
    line: int


@dataclass(frozen=True)
class ImportReference:
    file_path: str
    imported_name: str
    source_module: str
    line: int


@dataclass(frozen=True)
class ParseResult:
    file_path: str
    language: str
    symbols: list[Symbol]
    calls: list[CallReference]
    imports: list[ImportReference]


@dataclass(frozen=True)
class RetrievalResult:
    node_id: str
    name: str
    symbol_type: str
    file_path: str
    start_line: int
    end_line: int
    text: str
    vector_score: float | None
    graph_distance: int | None
    relevance_score: float
    source: str