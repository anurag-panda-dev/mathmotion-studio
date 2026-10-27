"""Manim scene generation and the subprocess render worker.

Submodules that import Manim (:mod:`app.rendering.registry`,
:mod:`app.rendering.manim_runtime`) are only loaded by the render
subprocess or by tests that skip when Manim is absent. The compiler and
the worker must stay importable without Manim so the backend starts on a
machine where rendering is not set up yet.
"""
