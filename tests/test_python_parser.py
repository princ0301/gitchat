from app.parsing.languages.python_parser import PythonParser
from app.core.types import SymbolType


def test_extracts_function_and_class_and_method():
    source = """
class Foo:
    def bar(self, x):
        return os.path.join(x)

def baz():
    f = Foo()
    return f.bar(1)
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    symbol_names = {(s.name, s.symbol_type, s.parent_name) for s in result.symbols}
    assert (("Foo", SymbolType.CLASS, None)) in symbol_names
    assert (("bar", SymbolType.METHOD, "Foo")) in symbol_names
    assert (("baz", SymbolType.FUNCTION, None)) in symbol_names


def test_extracts_calls_with_caller_context():
    source = """
def baz():
    f = Foo()
    return f.bar(1)
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    call_pairs = {(c.caller_name, c.callee_name) for c in result.calls}
    assert ("baz", "Foo") in call_pairs
    assert ("baz", "bar") in call_pairs


def test_extracts_imports():
    source = """
import os
from typing import Optional
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    import_pairs = {(i.source_module, i.imported_name) for i in result.imports}
    assert ("os", "os") in import_pairs
    assert ("typing", "Optional") in import_pairs


def test_extracts_docstring():
    source = '''
def greet():
    """Says hello."""
    return "hello"
'''
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    greet_symbol = next(s for s in result.symbols if s.name == "greet")
    assert greet_symbol.docstring == "Says hello."


def test_extracts_signature():
    source = """
def add(a, b):
    return a + b
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    add_symbol = next(s for s in result.symbols if s.name == "add")
    assert add_symbol.signature == "add(a, b)"


def test_nested_function_gets_distinct_scope_path():
    source = """
def test_one():
    def hello():
        return 1
    return hello()

def test_two():
    def hello():
        return 2
    return hello()
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    nested_hellos = [s for s in result.symbols if s.name == "hello"]
    assert len(nested_hellos) == 2
    parent_names = {s.parent_name for s in nested_hellos}
    assert parent_names == {"test_one", "test_two"}


def test_nested_function_is_not_classified_as_method():
    source = """
def outer():
    def inner():
        return 1
    return inner()
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    inner_symbol = next(s for s in result.symbols if s.name == "inner")
    assert inner_symbol.symbol_type == SymbolType.FUNCTION
    assert inner_symbol.parent_name == "outer"


def test_class_nested_inside_function_gets_scope_path():
    source = """
def make_class():
    class Helper:
        def run(self):
            return 1
    return Helper()
"""
    parser = PythonParser()
    result = parser.parse("sample.py", source)

    helper_symbol = next(s for s in result.symbols if s.name == "Helper")
    assert helper_symbol.symbol_type == SymbolType.CLASS
    assert helper_symbol.parent_name == "make_class"

    run_symbol = next(s for s in result.symbols if s.name == "run")
    assert run_symbol.symbol_type == SymbolType.METHOD
    assert run_symbol.parent_name == "make_class.Helper"