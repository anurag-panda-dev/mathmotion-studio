"""MathMotion Studio backend package.

This package deliberately keeps its top-level ``__init__`` free of heavy
imports: the render subprocess imports :mod:`app.rendering.manim_runtime`
directly, and that must not drag the FastAPI stack (or a missing Manim
installation) into unrelated processes.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
