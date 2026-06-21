import tempfile
from pathlib import Path
from app.graph.networkx_store import NetworkXGraphStore
from app.core.types import Symbol, SymbolType, EdgeType


def make_function_symbol(name: str, file_path: str = "sample.py") -> Symbol:
    return Symbol(
        symbol_type=SymbolType.FUNCTION,
        name=name,
        file_path=file_path,
        start_line=1,
        end_line=5,
    )


def test_add_and_get_node():
    store = NetworkXGraphStore()
    symbol = make_function_symbol("foo")
    store.add_node("sample.py::foo", symbol)

    retrieved = store.get_node("sample.py::foo")
    assert retrieved is not None
    assert retrieved.name == "foo"
    assert retrieved.symbol_type == SymbolType.FUNCTION


def test_get_node_missing_returns_none():
    store = NetworkXGraphStore()
    assert store.get_node("does.not.exist") is None


def test_add_edge_and_get_neighbors():
    store = NetworkXGraphStore()
    store.add_node("sample.py::foo", make_function_symbol("foo"))
    store.add_node("sample.py::bar", make_function_symbol("bar"))
    store.add_edge("sample.py::foo", "sample.py::bar", EdgeType.CALLS)

    callees = store.get_neighbors("sample.py::foo", EdgeType.CALLS, direction="out")
    assert callees == ["sample.py::bar"]

    callers = store.get_neighbors("sample.py::bar", EdgeType.CALLS, direction="in")
    assert callers == ["sample.py::foo"]


def test_get_callers():
    store = NetworkXGraphStore()
    store.add_node("sample.py::foo", make_function_symbol("foo"))
    store.add_node("sample.py::bar", make_function_symbol("bar"))
    store.add_node("sample.py::baz", make_function_symbol("baz"))
    store.add_edge("sample.py::foo", "sample.py::bar", EdgeType.CALLS)
    store.add_edge("sample.py::baz", "sample.py::bar", EdgeType.CALLS)

    callers = set(store.get_callers("sample.py::bar"))
    assert callers == {"sample.py::foo", "sample.py::baz"}


def test_get_dependents_combines_calls_and_imports():
    store = NetworkXGraphStore()
    store.add_node("a.py::foo", make_function_symbol("foo", "a.py"))
    store.add_node("b.py", make_function_symbol("b", "b.py"))
    store.add_edge("a.py::foo", "b.py", EdgeType.IMPORTS)

    dependents = store.get_dependents("b.py")
    assert dependents == ["a.py::foo"]


def test_node_and_edge_count():
    store = NetworkXGraphStore()
    store.add_node("a.py::foo", make_function_symbol("foo", "a.py"))
    store.add_node("a.py::bar", make_function_symbol("bar", "a.py"))
    store.add_edge("a.py::foo", "a.py::bar", EdgeType.CALLS)

    assert store.node_count() == 2
    assert store.edge_count() == 1


def test_has_node():
    store = NetworkXGraphStore()
    store.add_node("a.py::foo", make_function_symbol("foo", "a.py"))

    assert store.has_node("a.py::foo") is True
    assert store.has_node("a.py::missing") is False


def test_save_and_load_round_trip():
    store = NetworkXGraphStore()
    store.add_node("a.py::foo", make_function_symbol("foo", "a.py"))
    store.add_node("a.py::bar", make_function_symbol("bar", "a.py"))
    store.add_edge("a.py::foo", "a.py::bar", EdgeType.CALLS)

    with tempfile.TemporaryDirectory() as temp_dir:
        save_path = Path(temp_dir) / "graph.json"
        store.save(str(save_path))

        loaded_store = NetworkXGraphStore()
        loaded_store.load(str(save_path))

        assert loaded_store.node_count() == 2
        assert loaded_store.edge_count() == 1
        assert loaded_store.get_node("a.py::foo").name == "foo"
        assert loaded_store.get_callers("a.py::bar") == ["a.py::foo"]