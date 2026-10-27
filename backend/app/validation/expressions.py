"""Restricted math-expression grammar: validation and *safe* evaluation.

The grammar is defined in ``prompts/SCENE_FORMAT_SPEC.md`` section 7.4:
decimal numbers, variables, ``+ - * / **`` (``^`` alias), parentheses, the
constants ``pi`` and ``e``, and the function allowlist only.

Validation parses with Python's ``ast`` module and walks against an
allowlist — **never** ``eval`` on untrusted text. Evaluation afterwards
walks the *same* validated AST and builds a pure callable over
``math``/``sympy`` primitives; there is no code generation, no ``exec``
and no ``eval`` anywhere in this module (docs/SECURITY.md section 3).
"""

from __future__ import annotations

import ast
import math
from collections.abc import Callable
from typing import Any

import sympy

ALLOWED_FUNCS = frozenset(
    {
        "sin", "cos", "tan", "asin", "acos", "atan", "sqrt", "abs",
        "ln", "log", "log10", "exp", "floor", "ceil", "round", "min", "max",
    }
)
ALLOWED_CONSTS = frozenset({"pi", "e"})

# ln and log are the natural logarithm (matching SymPy's log), log10 is base 10.
_MATH_FUNCS: dict[str, Any] = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sqrt": math.sqrt, "abs": abs,
    "ln": math.log, "log": math.log, "log10": math.log10,
    "exp": math.exp, "floor": math.floor, "ceil": math.ceil,
    "round": round, "min": min, "max": max,
}

_SYMPY_FUNCS: dict[str, Any] = {
    "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
    "asin": sympy.asin, "acos": sympy.acos, "atan": sympy.atan,
    "sqrt": sympy.sqrt, "abs": sympy.Abs,
    "ln": sympy.log, "log": sympy.log,
    "log10": lambda x: sympy.log(x, 10),
    "exp": sympy.exp, "floor": sympy.floor, "ceil": sympy.ceiling,
    "min": sympy.Min, "max": sympy.Max,
}
_SYMPY_CONSTS = {"pi": sympy.pi, "e": sympy.E}


def check_expression(expr: str, allowed_vars: set[str]) -> str | None:
    """Validate an expression against the restricted grammar.

    Returns a plain-language error message, or ``None`` when acceptable.
    """
    try:
        tree = ast.parse(expr.replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        return f"not parseable as a math expression (syntax error at column {exc.offset})"

    called = {
        n.func.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Expression):
            continue
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                return f"disallowed literal {node.value!r}"
            continue
        if isinstance(node, ast.Name):
            if node.id in allowed_vars or node.id in ALLOWED_CONSTS or node.id in called:
                continue
            allowed = ", ".join(sorted(allowed_vars | ALLOWED_CONSTS))
            return f"unknown identifier '{node.id}' (allowed: {allowed})"
        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
        ):
            continue
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            continue
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
                name = node.func.id if isinstance(node.func, ast.Name) else "complex expression"
                return (
                    f"function '{name}' is not in the allowlist "
                    f"({', '.join(sorted(ALLOWED_FUNCS))})"
                )
            if node.keywords:
                return "keyword arguments are not allowed"
            continue
        if isinstance(node, (ast.Load, ast.Param)):
            continue
        if isinstance(node, (ast.operator, ast.unaryop)):
            continue
        return f"disallowed syntax: {type(node).__name__}"
    return None


def _compile_numeric(node: ast.AST) -> Callable[[dict[str, float]], float]:
    """Build a numeric evaluator closure for an already-validated AST node."""
    if isinstance(node, ast.Expression):
        return _compile_numeric(node.body)
    if isinstance(node, ast.Constant):
        value = float(node.value)
        return lambda env: value
    if isinstance(node, ast.Name):
        name = node.id
        if name in ALLOWED_CONSTS:
            const = math.pi if name == "pi" else math.e
            return lambda env: const
        return lambda env: env[name]
    if isinstance(node, ast.UnaryOp):
        operand = _compile_numeric(node.operand)
        if isinstance(node.op, ast.USub):
            return lambda env: -operand(env)
        return lambda env: +operand(env)
    if isinstance(node, ast.BinOp):
        left, right = _compile_numeric(node.left), _compile_numeric(node.right)
        if isinstance(node.op, ast.Add):
            return lambda env: left(env) + right(env)
        if isinstance(node.op, ast.Sub):
            return lambda env: left(env) - right(env)
        if isinstance(node.op, ast.Mult):
            return lambda env: left(env) * right(env)
        if isinstance(node.op, ast.Div):
            return lambda env: left(env) / right(env)
        if isinstance(node.op, ast.Pow):
            return lambda env: left(env) ** right(env)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = _MATH_FUNCS[node.func.id]
        args = [_compile_numeric(a) for a in node.args]
        return lambda env: float(fn(*[a(env) for a in args]))
    raise ValueError(f"unsupported node after validation: {type(node).__name__}")


def evaluate_numeric(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate a validated expression to a float (raises ValueError on bad input)."""
    env = dict(variables or {})
    tree = ast.parse(expr.replace("^", "**"), mode="eval")
    # Function names appear as ast.Name children of their Call node; exclude
    # them so ``sqrt(2)`` doesn't demand a variable named "sqrt".
    called = {
        n.func.id
        for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    required = {
        n.id for n in ast.walk(tree) if isinstance(n, ast.Name)
    } - ALLOWED_CONSTS - called
    missing = sorted(required - env.keys())
    if missing:
        raise ValueError(f"missing value(s) for {', '.join(missing)}")
    fn = _compile_numeric(tree)
    return float(fn(env))


def _compile_sympy(node: ast.AST, symbols: dict[str, sympy.Symbol]) -> Any:
    if isinstance(node, ast.Expression):
        return _compile_sympy(node.body, symbols)
    if isinstance(node, ast.Constant):
        return sympy.Rational(str(node.value)) if isinstance(node.value, float) else sympy.Integer(node.value)
    if isinstance(node, ast.Name):
        if node.id in symbols:
            return symbols[node.id]
        if node.id == "pi":
            return sympy.pi
        if node.id == "e":
            return sympy.E
        raise ValueError(f"unknown name {node.id}")
    if isinstance(node, ast.UnaryOp):
        operand = _compile_sympy(node.operand, symbols)
        return -operand if isinstance(node.op, ast.USub) else +operand
    if isinstance(node, ast.BinOp):
        left = _compile_sympy(node.left, symbols)
        right = _compile_sympy(node.right, symbols)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id not in _SYMPY_FUNCS:
            raise ValueError(f"function {node.func.id} has no symbolic form")
        fn = _SYMPY_FUNCS[node.func.id]
        args = [_compile_sympy(a, symbols) for a in node.args]
        return fn(*args)
    raise ValueError(f"unsupported node: {type(node).__name__}")


def evaluate_symbolic(
    expr: str, variables: list[str] | None = None
) -> Any:
    """Build a SymPy expression from a validated expression string."""
    names = set(variables or [])
    tree = ast.parse(expr.replace("^", "**"), mode="eval")
    symbols = {name: sympy.Symbol(name) for name in names}
    return _compile_sympy(tree, symbols)
