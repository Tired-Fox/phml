# pylint: disable=missing-module-docstring
from pathlib import Path

from phml.nodes import AST, Element

__all__ = ["tag_from_file", "filename_from_path", "parse_component"]


def tag_from_file(filename: str | Path) -> str:
    """Generates a tag name some-tag-name from a filename.
    Assumes filenames of:
    * snakecase - some_file_name
    * camel case - someFileName
    * pascal case - SomeFileName
    """
    from re import finditer  # pylint: disable=import-outside-toplevel

    if isinstance(filename, Path):
        if filename.is_file():
            filename = filename.name.replace(filename.suffix, "")
        else:
            raise TypeError("If filename is a path it must also be a valid file.")

    tokens = []
    for token in finditer(r"(\b|[A-Z]|_|-)([a-z]+)|([A-Z]+)(?=[^a-z])", filename):
        first, rest, cap = token.groups()

        if  first is not None and first.isupper():
            rest = first + rest
        elif cap is not None and cap.isupper():
            rest = cap
        tokens.append(rest.lower())

    return "-".join(tokens)


def filename_from_path(file: Path) -> str:
    """Get the filename without the suffix from a pathlib.Path."""

    if file.is_file():
        return file.name.replace(file.suffix, "")

    raise TypeError(f"Expected {type(Path)} not {type(file)}")


def parse_component(ast: AST) -> dict[str, Element]:
    """Helper function to parse the components elements."""
    from phml.utils import test, visit_children  # pylint: disable=import-outside-toplevel

    result = {"python": [], "script": [], "style": [], "component": None}
    for node in visit_children(ast.tree):
        if test(node, ["element", {"tag": "python"}]):
            result["python"].append(node)
        elif test(node, ["element", {"tag": "script"}]):
            result["script"].append(node)
        elif test(node, ["element", {"tag": "style"}]):
            result["style"].append(node)
        elif test(node, "element"):
            if result["component"] is None:
                result["component"] = node
            else:
                raise Exception(
                    """\
Components may only have one wrapping element. All other element in the root must be either a \
script, style, or python tag.\
"""
                )

    if result["component"] is None:
        raise Exception("Must have at least one element in a component.")

    return result
