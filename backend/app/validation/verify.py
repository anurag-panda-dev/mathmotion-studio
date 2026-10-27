"""Stage 9 — optional mathematical verification of front-matter assertions.

Reported **separately** from syntax validation, always. A scene that
validates is well-formed; a scene that renders compiled. Only these
assertions speak to mathematical correctness, and only for the
relationships they state (``prompts/SCENE_VALIDATION_RULES.md`` section 4).
"""

from __future__ import annotations

import math
from typing import Any

from app.validation.expressions import check_expression, evaluate_numeric, evaluate_symbolic
from app.validation.issues import VerificationOutcome


def _verify_one(assertion: dict[str, Any]) -> VerificationOutcome:
    kind = str(assertion.get("kind", "numeric"))
    expr = str(assertion.get("expression", ""))
    expected = float(assertion.get("expected", 0.0))
    tolerance = float(assertion.get("tolerance", 1e-9) or 1e-9)
    subs_raw = assertion.get("subs") or {}
    subs = {str(k): float(v) for k, v in subs_raw.items()} if isinstance(subs_raw, dict) else {}

    base = {
        "id": str(assertion.get("id", "?")),
        "kind": kind,
        "description": str(assertion.get("description", "")),
        "expected": expected,
    }

    # Re-check grammar safety here: verification runs without the pipeline sometimes.
    msg = check_expression(expr, set(subs))
    if msg is not None:
        return VerificationOutcome(
            **base, status="failed",
            message=f"Expression is not in the allowed grammar: {msg}", actual=None,
        )

    if kind == "symbolic":
        try:
            import sympy
        except ImportError:  # pragma: no cover - sympy is a core dependency
            return VerificationOutcome(
                **base, status="unavailable",
                message="Symbolic verification is unavailable: SymPy is not installed.",
                actual=None,
            )
        try:
            value = evaluate_symbolic(expr, sorted(subs))
            if subs:
                value = value.subs({k: v for k, v in subs.items()})
            residual = sympy.simplify(value - expected)
            passed = residual == 0
            actual = float(residual) if residual.is_number else None
        except Exception as exc:  # noqa: BLE001 - report, never crash the API
            return VerificationOutcome(
                **base, status="failed",
                message=f"Symbolic check could not be completed: {exc}", actual=None,
            )
        return VerificationOutcome(
            **base,
            status="passed" if passed else "failed",
            message=(
                "The identity simplifies to zero."
                if passed
                else f"The expression simplifies to {residual}, not {expected:g}."
            ),
            actual=actual if not passed else 0.0,
        )

    # numeric
    try:
        actual = evaluate_numeric(expr, subs)
    except ZeroDivisionError:
        return VerificationOutcome(
            **base, status="failed",
            message="The expression divides by zero for the given values.", actual=None,
        )
    except (ValueError, OverflowError) as exc:
        return VerificationOutcome(
            **base, status="failed",
            message=f"The expression could not be evaluated: {exc}", actual=None,
        )
    if not math.isfinite(actual):
        return VerificationOutcome(
            **base, status="failed",
            message="The expression evaluated to a non-finite value (inf or nan).",
            actual=None,
        )
    passed = abs(actual - expected) <= tolerance
    return VerificationOutcome(
        **base,
        status="passed" if passed else "failed",
        message=(
            f"Evaluates to {actual:g}, within tolerance of {expected:g}."
            if passed
            else f"Evaluates to {actual:g}, expected {expected:g}."
        ),
        actual=actual,
    )


def run_verification(front_matter: dict[str, Any] | None) -> list[VerificationOutcome]:
    """Evaluate every ``verification`` assertion in the front matter."""
    if not isinstance(front_matter, dict):
        return []
    assertions = front_matter.get("verification") or []
    outcomes: list[VerificationOutcome] = []
    for assertion in assertions:
        if isinstance(assertion, dict):
            outcomes.append(_verify_one(assertion))
    return outcomes
