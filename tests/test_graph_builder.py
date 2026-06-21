from app.parsing.languages.python_parser import PythonParser
from app.graph.builder import GraphBuilder
from app.graph.networkx_store import NetworkXGraphStore
from app.core.types import EdgeType
from app.core.identity import build_node_id


def test_builds_file_and_symbol_nodes():
    parser = PythonParser()
    source = """
def baz():
    return 1
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    assert store.has_node("sample.py")
    assert store.has_node(build_node_id("sample.py", "baz"))


def test_contains_edge_from_file_to_function():
    parser = PythonParser()
    source = """
def baz():
    return 1
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    func_node_id = build_node_id("sample.py", "baz")
    children = store.get_neighbors("sample.py", EdgeType.CONTAINS, direction="out")
    assert func_node_id in children


def test_contains_edge_from_class_to_method():
    parser = PythonParser()
    source = """
class Foo:
    def bar(self):
        return 1
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    class_node_id = build_node_id("sample.py", "Foo")
    method_node_id = build_node_id("sample.py", "Foo.bar")
    children = store.get_neighbors(class_node_id, EdgeType.CONTAINS, direction="out")
    assert method_node_id in children


def test_resolves_same_file_call():
    parser = PythonParser()
    source = """
def helper():
    return 1

def baz():
    return helper()
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    baz_node_id = build_node_id("sample.py", "baz")
    helper_node_id = build_node_id("sample.py", "helper")
    callees = store.get_neighbors(baz_node_id, EdgeType.CALLS, direction="out")
    assert helper_node_id in callees


def test_resolves_cross_file_call():
    parser = PythonParser()
    file_a_source = """
def helper():
    return 1
"""
    file_b_source = """
def baz():
    return helper()
"""
    result_a = parser.parse("a.py", file_a_source)
    result_b = parser.parse("b.py", file_b_source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result_a, result_b])

    baz_node_id = build_node_id("b.py", "baz")
    helper_node_id = build_node_id("a.py", "helper")
    callees = store.get_neighbors(baz_node_id, EdgeType.CALLS, direction="out")
    assert helper_node_id in callees


def test_get_callers_after_build():
    parser = PythonParser()
    source = """
def helper():
    return 1

def baz():
    return helper()

def qux():
    return helper()
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    helper_node_id = build_node_id("sample.py", "helper")
    callers = set(store.get_callers(helper_node_id))
    assert callers == {
        build_node_id("sample.py", "baz"),
        build_node_id("sample.py", "qux"),
    }


def test_unresolvable_call_is_skipped_not_errored():
    parser = PythonParser()
    source = """
def baz():
    return external_library_function()
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    baz_node_id = build_node_id("sample.py", "baz")
    callees = store.get_neighbors(baz_node_id, EdgeType.CALLS, direction="out")
    assert callees == []


def test_same_scope_name_collision_gets_unique_node_ids():
    parser = PythonParser()
    source = """
def test_something(apps):
    class Module:
        x = 1

    class Module:
        x = 2

    class Module:
        x = 3
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    module_nodes = [n for n in store._graph.nodes if "Module" in n]
    assert len(module_nodes) == 3
    assert len(set(module_nodes)) == 3


def test_first_occurrence_keeps_clean_node_id():
    parser = PythonParser()
    source = """
def test_something(apps):
    class Module:
        x = 1

    class Module:
        x = 2
"""
    result = parser.parse("sample.py", source)

    builder = GraphBuilder(NetworkXGraphStore())
    store = builder.build([result])

    assert store.has_node(build_node_id("sample.py", "test_something.Module"))