import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor, Node

from app.core.interfaces.parser import LanguageParser
from app.core.types import ParseResult, Symbol, SymbolType, CallReference, ImportReference

PY_LANGUAGE = Language(tspython.language())

QUERY_TEXT = """
(function_definition
  name: (identifier) @func.name) @func.def

(class_definition
  name: (identifier) @class.name) @class.def

(call
  function: (identifier) @call.name) @call.simple

(call
  function: (attribute
    attribute: (identifier) @call.name)) @call.method

(import_statement
  name: (dotted_name) @import.name)

(import_statement
  name: (aliased_import
    name: (dotted_name) @import.name))

(import_from_statement
  module_name: (dotted_name) @import.module
  name: (dotted_name) @import.name)
"""


class PythonParser(LanguageParser):
    def __init__(self):
        self._parser = Parser(PY_LANGUAGE)
        self._query = Query(PY_LANGUAGE, QUERY_TEXT)

    @property
    def language_name(self) -> str:
        return "python"

    @property
    def file_extensions(self) -> list[str]:
        return [".py"]

    def parse(self, file_path: str, source_code: str) -> ParseResult:
        source_bytes = source_code.encode("utf-8")
        tree = self._parser.parse(source_bytes)
        cursor = QueryCursor(self._query)
        matches = cursor.matches(tree.root_node)

        symbols = self._extract_symbols(matches, file_path)
        calls = self._extract_calls(matches, file_path, tree.root_node)
        imports = self._extract_imports(matches, file_path)

        return ParseResult(
            file_path=file_path,
            language=self.language_name,
            symbols=symbols,
            calls=calls,
            imports=imports,
        )

    def _extract_symbols(self, matches, file_path: str) -> list[Symbol]:
        symbols = []
        for _, captures in matches:
            if "func.def" in captures:
                func_node = captures["func.def"][0]
                name_node = captures["func.name"][0]
                scope_path = self._find_enclosing_scope_path(func_node)
                symbol_type = SymbolType.METHOD if self._immediate_parent_is_class(func_node) else SymbolType.FUNCTION
                symbols.append(
                    Symbol(
                        symbol_type=symbol_type,
                        name=name_node.text.decode("utf-8"),
                        file_path=file_path,
                        start_line=func_node.start_point.row + 1,
                        end_line=func_node.end_point.row + 1,
                        parent_name=scope_path,
                        signature=self._extract_signature(func_node),
                        docstring=self._extract_docstring(func_node),
                    )
                )
            elif "class.def" in captures:
                class_node = captures["class.def"][0]
                name_node = captures["class.name"][0]
                scope_path = self._find_enclosing_scope_path(class_node)
                symbols.append(
                    Symbol(
                        symbol_type=SymbolType.CLASS,
                        name=name_node.text.decode("utf-8"),
                        file_path=file_path,
                        start_line=class_node.start_point.row + 1,
                        end_line=class_node.end_point.row + 1,
                        parent_name=scope_path,
                        signature=None,
                        docstring=self._extract_docstring(class_node),
                    )
                )
        return symbols

    def _extract_calls(self, matches, file_path: str, root_node: Node) -> list[CallReference]:
        calls = []
        for _, captures in matches:
            call_node = None
            if "call.simple" in captures:
                call_node = captures["call.simple"][0]
            elif "call.method" in captures:
                call_node = captures["call.method"][0]
            if call_node is None:
                continue
            callee_name = captures["call.name"][0].text.decode("utf-8")
            caller_name = self._find_enclosing_function(call_node) or "__module__"
            calls.append(
                CallReference(
                    caller_name=caller_name,
                    callee_name=callee_name,
                    file_path=file_path,
                    line=call_node.start_point.row + 1,
                )
            )
        return calls

    def _extract_imports(self, matches, file_path: str) -> list[ImportReference]:
        imports = []
        for _, captures in matches:
            if "import.name" not in captures:
                continue
            imported_name = captures["import.name"][0].text.decode("utf-8")
            source_module = (
                captures["import.module"][0].text.decode("utf-8")
                if "import.module" in captures
                else imported_name
            )
            line = captures["import.name"][0].start_point.row + 1
            imports.append(
                ImportReference(
                    file_path=file_path,
                    imported_name=imported_name,
                    source_module=source_module,
                    line=line,
                )
            )
        return imports

    def _immediate_parent_is_class(self, node: Node) -> bool:
        current = node.parent
        while current is not None:
            if current.type in ("class_definition", "function_definition"):
                return current.type == "class_definition"
            current = current.parent
        return False

    def _find_enclosing_scope_path(self, node: Node) -> str | None:
        scopes = []
        current = node.parent
        while current is not None:
            if current.type in ("class_definition", "function_definition"):
                name_node = current.child_by_field_name("name")
                if name_node is not None:
                    scopes.append(name_node.text.decode("utf-8"))
            current = current.parent
        if not scopes:
            return None
        return ".".join(reversed(scopes))

    def _find_enclosing_function(self, node: Node) -> str | None:
        current = node.parent
        while current is not None:
            if current.type == "function_definition":
                name_node = current.child_by_field_name("name")
                return name_node.text.decode("utf-8") if name_node else None
            current = current.parent
        return None

    def _extract_signature(self, func_node: Node) -> str | None:
        name_node = func_node.child_by_field_name("name")
        params_node = func_node.child_by_field_name("parameters")
        if name_node is None or params_node is None:
            return None
        return f"{name_node.text.decode('utf-8')}{params_node.text.decode('utf-8')}"

    def _extract_docstring(self, definition_node: Node) -> str | None:
        body_node = definition_node.child_by_field_name("body")
        if body_node is None or body_node.child_count == 0:
            return None
        first_statement = body_node.children[0]
        if first_statement.type != "expression_statement":
            return None
        string_node = first_statement.children[0] if first_statement.child_count > 0 else None
        if string_node is None or string_node.type != "string":
            return None
        return string_node.text.decode("utf-8").strip("\"'")