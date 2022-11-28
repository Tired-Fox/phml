from pathlib import Path
from phml.nodes import AST, Element

__all__ = ["tag_from_file", "filename_from_path", "parse_component"]


def tag_from_file(filename: str) -> str:
    """Generates a tag name some-tag-name from a filename.
    Assumes filenames of:
    * snakecase - some_file_name
    * camel case - someFileName
    * pascal case - SomeFileName
    """
    from re import finditer

    tokens = []
    for token in finditer(r"(\b|[A-Z]|_)([a-z]+)", filename):
        first, rest = token.groups()
        if first.isupper():
            rest = first + rest
        tokens.append(rest.lower())

    return "-".join(tokens)


def filename_from_path(file: Path) -> str:
    """Get the filename without the suffix from a pathlib.Path."""

    if file.is_file():
        return file.name.replace(file.suffix, "")
    else:
        raise TypeError(f"Expected {type(Path)} not {type(file)}")


def parse_component(ast: AST) -> dict[str, Element]:
    from phml.utils import visit_children, test

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
Components may only have one wrapping element. All other element in the root must be either a script,\
style, or python tag.\
"""
                )

    if result["component"] is None:
        raise Exception("Must have at least one element in a component.")

    return result
