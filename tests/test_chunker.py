from app.retrieval.chunker import SymbolChunker
from app.core.types import Symbol, SymbolType


def make_source_lines():
    source = """def add(a, b):
    return a + b
"""
    return source.splitlines()


def test_chunks_function_symbol():
    symbol = Symbol(
        symbol_type=SymbolType.FUNCTION,
        name="add",
        file_path="sample.py",
        start_line=1,
        end_line=2,
        signature="add(a, b)",
    )
    chunker = SymbolChunker()
    chunk = chunker.chunk(symbol, make_source_lines())

    assert chunk is not None
    assert chunk.node_id == "sample.py::add"
    assert "add(a, b)" in chunk.text
    assert "return a + b" in chunk.text


def test_skips_non_chunkable_symbol_types():
    symbol = Symbol(
        symbol_type=SymbolType.FILE,
        name="sample.py",
        file_path="sample.py",
        start_line=0,
        end_line=0,
    )
    chunker = SymbolChunker()
    chunk = chunker.chunk(symbol, make_source_lines())

    assert chunk is None


def test_includes_docstring_when_present():
    symbol = Symbol(
        symbol_type=SymbolType.FUNCTION,
        name="add",
        file_path="sample.py",
        start_line=1,
        end_line=2,
        signature="add(a, b)",
        docstring="Adds two numbers.",
    )
    chunker = SymbolChunker()
    chunk = chunker.chunk(symbol, make_source_lines())

    assert "Adds two numbers." in chunk.text


def test_method_uses_qualified_name():
    symbol = Symbol(
        symbol_type=SymbolType.METHOD,
        name="bar",
        file_path="sample.py",
        start_line=1,
        end_line=2,
        parent_name="Foo",
    )
    chunker = SymbolChunker()
    chunk = chunker.chunk(symbol, make_source_lines())

    assert chunk.node_id == "sample.py::Foo.bar"
    assert "Foo.bar" in chunk.text


def test_truncates_long_body():
    symbol = Symbol(
        symbol_type=SymbolType.FUNCTION,
        name="big_func",
        file_path="sample.py",
        start_line=1,
        end_line=1,
    )
    long_line = "x" * 5000
    chunker = SymbolChunker()
    chunk = chunker.chunk(symbol, [long_line])

    assert "truncated" in chunk.text
    assert len(chunk.text) < 5000


def test_chunk_all_filters_and_maps_correctly():
    symbols = [
        Symbol(symbol_type=SymbolType.FILE, name="sample.py", file_path="sample.py", start_line=0, end_line=0),
        Symbol(symbol_type=SymbolType.FUNCTION, name="add", file_path="sample.py", start_line=1, end_line=2),
    ]
    chunker = SymbolChunker()
    chunks = chunker.chunk_all(symbols, {"sample.py": make_source_lines()})

    assert len(chunks) == 1
    assert chunks[0].node_id == "sample.py::add"