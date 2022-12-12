"""phml.utilities.transform.sanatize

Logic for sanatizing a phml ast.
"""
from .clean import sanatize
from .schema import Schema

__all__ = ["sanatize", "Schema"]
