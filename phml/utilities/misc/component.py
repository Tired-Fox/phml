from pathlib import Path

from phml.core.nodes import AST, All_Nodes, Element

__all__ = [
    "tag_from_file",
    "filename_from_path",
    "parse_component",
    "valid_component_dict",
    "cmpt_name_from_path",
]


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
    for token in finditer(r"(\b|[A-Z]|_|-)([a-z]+)|([0-9]+)|([A-Z]+)(?=[^a-z])", filename):
        first, rest, nums, cap = token.groups()

        if first is not None and first.isupper():
            rest = first + rest
        elif cap is not None and cap.isupper():
            rest = cap
        elif nums is not None and nums.isnumeric():
            rest = str(nums)
        tokens.append(rest.lower())

    return "-".join(tokens)


def cmpt_name_from_path(file: Path, strip_root: bool = True) -> str:
    """Construct a component name given a path. This will include parent directories.
    it will also strip the root directory as this is most commonly not wanted.

    Examples:
        `components/blog/header.phml`

        yields

        `blog-header`
    """
    last = file.name.replace(file.suffix, "")

    file = file.as_posix().lstrip("/")
    if strip_root:
        dirs = [subdir for subdir in file.split("/")[1:-1] if subdir.strip() != ""]
    else:
        dirs = [subdir for subdir in file.split("/")[:-1] if subdir.strip() != ""]

    if len(dirs) > 0:
        return "-".join(dirs) + f"-{last}"
    return last

def filename_from_path(file: Path) -> str:
    """Get the filename without the suffix from a pathlib.Path."""

    return file.name.replace(file.suffix, "")


def valid_component_dict(cmpt: dict) -> bool:
    """Check if a component dict is valid."""
    return bool(
        ("python" in cmpt and isinstance(cmpt["python"], list))
        and ("script" in cmpt and isinstance(cmpt["script"], list))
        and ("style" in cmpt and isinstance(cmpt["script"], list))
        and ("component" in cmpt and isinstance(cmpt["component"], All_Nodes))
    )


def parse_component(ast: AST) -> dict[str, Element]:
    """Helper function to parse the components elements."""
    from phml import (  # pylint: disable=import-outside-toplevel
        check,
        is_css_style,
        is_javascript,
        visit_children,
    )

    result = {"python": [], "script": [], "style": [], "component": None}
    for node in visit_children(ast.tree):
        if check(node, ["element", {"tag": "python"}]):
            result["python"].append(node)
        elif check(node, ["element", {"tag": "script"}]) and is_javascript(node):
            result["script"].append(node)
        elif check(node, ["element", {"tag": "style"}]) and is_css_style(node):
            result["style"].append(node)
        elif check(node, "element"):
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
