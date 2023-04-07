"""phml.utilities.transform.sanatize

Logic for sanatizing a phml ast.
"""
from .clean import (
    sanatize,
    recurse_strip,
    recurse_check_tag,
    recurse_check_ancestor,
    recurse_check_required,
    recurse_check_attributes,
)
from .schema import Schema

__all__ = [
    "sanatize",
    "Schema",
    "recurse_check_attributes",
    "recurse_check_required",
    "recurse_strip",
    "recurse_check_tag",
    "recurse_check_ancestor"
]
