from app.core.types import ParseResult, Symbol, SymbolType, EdgeType
from app.core.interfaces.graph_store import GraphStore
from app.core.identity import build_node_id, build_qualified_name


class GraphBuilder:
    def __init__(self, graph_store: GraphStore):
        self._graph_store = graph_store
        self._name_index: dict[str, list[str]] = {}
        self._file_nodes: set[str] = set()
        self._assigned_node_ids: set[str] = set()
        self._node_id_by_symbol: dict[int, str] = {}

    def build(self, parse_results: list[ParseResult]) -> GraphStore:
        for result in parse_results:
            self._add_file_node(result.file_path)

        for result in parse_results:
            self._add_symbol_nodes(result)

        for result in parse_results:
            self._resolve_calls(result)
            self._resolve_imports(result)

        return self._graph_store

    def get_node_id_for_symbol(self, symbol: Symbol) -> str:
        return self._node_id_by_symbol[id(symbol)]

    def _add_file_node(self, file_path: str) -> None:
        file_node_id = file_path
        if file_node_id in self._file_nodes:
            return
        file_symbol = Symbol(
            symbol_type=SymbolType.FILE,
            name=file_path,
            file_path=file_path,
            start_line=0,
            end_line=0,
        )
        self._graph_store.add_node(file_node_id, file_symbol)
        self._file_nodes.add(file_node_id)

    def _add_symbol_nodes(self, result: ParseResult) -> None:
        for symbol in result.symbols:
            qualified_name = build_qualified_name(symbol.name, symbol.parent_name)
            node_id = self._make_unique_node_id(symbol.file_path, qualified_name, symbol.start_line)
            self._node_id_by_symbol[id(symbol)] = node_id
            self._graph_store.add_node(node_id, symbol)
            self._graph_store.add_edge(symbol.file_path, node_id, EdgeType.CONTAINS)
            self._index_name(symbol.name, node_id)

            if symbol.symbol_type == SymbolType.METHOD and symbol.parent_name:
                class_node_id = build_node_id(symbol.file_path, symbol.parent_name)
                if self._graph_store.has_node(class_node_id):
                    self._graph_store.add_edge(class_node_id, node_id, EdgeType.CONTAINS)

    def _make_unique_node_id(self, file_path: str, qualified_name: str, start_line: int) -> str:
        node_id = build_node_id(file_path, qualified_name)
        if node_id not in self._assigned_node_ids:
            self._assigned_node_ids.add(node_id)
            return node_id
        disambiguated_id = build_node_id(file_path, f"{qualified_name}@{start_line}")
        self._assigned_node_ids.add(disambiguated_id)
        return disambiguated_id

    def _index_name(self, name: str, node_id: str) -> None:
        self._name_index.setdefault(name, []).append(node_id)

    def _resolve_calls(self, result: ParseResult) -> None:
        for call in result.calls:
            caller_node_id = self._resolve_caller_node_id(call.caller_name, call.file_path)
            if caller_node_id is None:
                continue
            callee_node_id = self._resolve_callee(call.callee_name, call.file_path)
            if callee_node_id is None:
                continue
            self._graph_store.add_edge(caller_node_id, callee_node_id, EdgeType.CALLS)

    def _resolve_caller_node_id(self, caller_name: str, file_path: str) -> str | None:
        if caller_name == "__module__":
            return file_path
        candidates = self._name_index.get(caller_name, [])
        same_file = [c for c in candidates if c.startswith(f"{file_path}::")]
        if same_file:
            return same_file[0]
        return candidates[0] if candidates else None

    def _resolve_callee(self, callee_name: str, file_path: str) -> str | None:
        candidates = self._name_index.get(callee_name, [])
        if not candidates:
            return None
        same_file = [c for c in candidates if c.startswith(f"{file_path}::")]
        if same_file:
            return same_file[0]
        return candidates[0]

    def _resolve_imports(self, result: ParseResult) -> None:
        for import_ref in result.imports:
            target_file = self._resolve_module_to_file(import_ref.source_module)
            if target_file is None:
                continue
            self._graph_store.add_edge(import_ref.file_path, target_file, EdgeType.IMPORTS)

    def _resolve_module_to_file(self, module_name: str) -> str | None:
        candidate_suffixes = (
            f"/{module_name}.py",
            f"\\{module_name}.py",
        )
        for file_node_id in self._file_nodes:
            if file_node_id == f"{module_name}.py":
                return file_node_id
            if file_node_id.endswith(candidate_suffixes):
                return file_node_id
        return None