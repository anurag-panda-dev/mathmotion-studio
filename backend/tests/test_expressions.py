"""Restricted math grammar tests: validation, safe evaluation, no code execution."""

from __future__ import annotations

import math

import pytest

from app.validation.expressions import check_expression, evaluate_numeric, evaluate_symbolic


@pytest.mark.parametrize(
    "expr",
    [
        "3**2 + 4**2 - 5**2",
        "x**2",
        "sin(x) + cos(x)",
        "sqrt(2)",
        "ln(e)",
        "log(100)",  # log is the natural logarithm in this grammar
        "log10(100)",
        "abs(-3)",
        "pi * r**2",
        "min(1, 2) + max(3, 4)",
        "floor(1.5) + ceil(1.2) + round(1.4)",
        "(1 + 2) * (3 - 1) / 2",
        "2 ^ 3",  # ^ is an alias for **
    ],
)
def test_grammar_accepts_valid_expressions(expr):
    # Declare every variable the expression actually uses (the grammar's
    # constants pi/e and function names are handled by the checker itself).
    import ast as _ast

    tree = _ast.parse(expr.replace("^", "**"), mode="eval")
    allowed = {n.id for n in _ast.walk(tree) if isinstance(n, _ast.Name)}
    assert check_expression(expr, allowed) is None


@pytest.mark.parametrize(
    "expr,vars",
    [
        ("__import__('os')", set()),
        ("open('x')", set()),
        ("eval('1')", set()),
        ("lambda: 1", set()),
        ("[1,2]", set()),
        ("{'a': 1}", set()),
        ("y + 1", {"x"}),  # unknown identifier
        ("sin(x", {"x"}),  # syntax error
        ("1 if x else 2", {"x"}),  # disallowed syntax
        ("f'{x}'", {"x"}),  # f-string
        ("x.attr", {"x"}),  # attribute access
        ("x[0]", {"x"}),  # subscript
        ("sin(x, kw=1)", {"x"}),  # keyword args
        ("tanh(x)", {"x"}),  # not in allowlist
        ("'string'", set()),  # string literal
        ("True", set()),  # bool literal
    ],
)
def test_grammar_rejects_unsafe_or_unknown(expr, vars):  # noqa: A002
    assert check_expression(expr, vars) is not None


def test_evaluate_numeric_matches_math():
    assert evaluate_numeric("3**2 + 4**2 - 5**2") == 0
    assert evaluate_numeric("sqrt(2)", {}) == pytest.approx(math.sqrt(2))
    assert evaluate_numeric("x**2", {"x": 3}) == 9
    assert evaluate_numeric("log10(100)") == pytest.approx(2.0)
    assert evaluate_numeric("ln(e)") == pytest.approx(1.0)
    assert evaluate_numeric("2 ^ 3") == 8


def test_evaluate_numeric_missing_variable_raises():
    with pytest.raises(ValueError, match="missing value"):
        evaluate_numeric("x + 1", {})


def test_evaluate_numeric_never_executes_code():
    """The evaluator walks a validated AST — hostile input is rejected, not run."""
    for hostile in ("__import__('os')", "open('x')", "(1).__class__"):
        # Rejection type varies by AST path (ValueError/SyntaxError/KeyError);
        # the invariant is that it raises rather than executes.
        with pytest.raises(Exception):  # noqa: B017
            evaluate_numeric(hostile, {"x": 1})


def test_evaluate_symbolic_builds_expression():
    expr = evaluate_symbolic("x**2 + 2*x + 1", ["x"])
    import sympy

    assert sympy.simplify(expr.subs("x", 2) - 9) == 0


def test_symbolic_vs_numeric_agree():
    value = evaluate_symbolic("sin(pi/2)", [])

    assert float(value) == pytest.approx(evaluate_numeric("sin(pi/2)"))
