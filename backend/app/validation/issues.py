"""Validation issue records — the structured error taxonomy.

Identical in shape to the reference validator's report
(``tools/validate_scene.py``) and to the documented taxonomy in
``prompts/SCENE_VALIDATION_RULES.md`` section 2: category, scene id, field
path, source line, plain-language message, suggested correction. Errors
block an import; warnings never do.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    category: str
    message: str
    scene: str | None = None
    path: str | None = None
    line: int | None = None
    suggestion: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "scene": self.scene,
            "path": self.path,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class VerificationOutcome:
    id: str
    kind: str
    description: str
    status: str  # "passed" | "failed" | "unavailable"
    message: str
    expected: float
    actual: float | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "description": self.description,
            "status": self.status,
            "message": self.message,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class ValidationReport:
    filename: str = "scene.md"
    schema_version: str | None = None
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    verification: list[VerificationOutcome] = field(default_factory=list)
    summary: dict[str, Any] | None = None

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, *args: Any, **kwargs: Any) -> None:
        self.errors.append(Issue("error", *args, **kwargs))

    def warn(self, *args: Any, **kwargs: Any) -> None:
        self.warnings.append(Issue("warning", *args, **kwargs))
