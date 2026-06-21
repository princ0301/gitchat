from dataclasses import dataclass

from app.core.types import Symbol, SymbolType
from app.core.identity import build_node_id, build_qualified_name

CHUNKABLE_TYPES = {SymbolType.FUNCTION, SymbolType.METHOD, SymbolType.CLASS}
MAX_BODY_CHARS = 2000


@dataclass(frozen=True)
class Chunk:
    node_id: str
    text: str
    file_path: str
    start_line: int
    end_line: int
    symbol_type: str
    name: str


class SymbolChunker:
    def chunk(self, symbol: Symbol, source_lines: list[str]) -> Chunk | None:
        if symbol.symbol_type not in CHUNKABLE_TYPES:
            return None

        qualified_name = build_qualified_name(symbol.name, symbol.parent_name)
        node_id = build_node_id(symbol.file_path, qualified_name)
        body = self._extract_body(symbol, source_lines)
        text = self._build_chunk_text(symbol, qualified_name, body)

        return Chunk(
            node_id=node_id,
            text=text,
            file_path=symbol.file_path,
            start_line=symbol.start_line,
            end_line=symbol.end_line,
            symbol_type=symbol.symbol_type.value,
            name=symbol.name,
        )

    def chunk_all(self, symbols: list[Symbol], source_lines_by_file: dict[str, list[str]]) -> list[Chunk]:
        chunks = []
        for symbol in symbols:
            source_lines = source_lines_by_file.get(symbol.file_path, [])
            chunk = self.chunk(symbol, source_lines)
            if chunk is not None:
                chunks.append(chunk)
        return chunks

    def _extract_body(self, symbol: Symbol, source_lines: list[str]) -> str:
        if not source_lines:
            return ""
        start = max(symbol.start_line - 1, 0)
        end = min(symbol.end_line, len(source_lines))
        body = "\n".join(source_lines[start:end])
        if len(body) > MAX_BODY_CHARS:
            body = body[:MAX_BODY_CHARS] + "\n... (truncated)"
        return body

    def _build_chunk_text(self, symbol: Symbol, qualified_name: str, body: str) -> str:
        parts = [f"{symbol.symbol_type.value}: {qualified_name}", f"file: {symbol.file_path}"]
        if symbol.signature:
            parts.append(f"signature: {symbol.signature}")
        if symbol.docstring:
            parts.append(f"docstring: {symbol.docstring}")
        parts.append(f"code:\n{body}")
        return "\n".join(parts)