from pathlib import Path
from re import finditer, sub

from phml.core.nodes import AST, NODE, Element

__all__ = [
    "tokanize_name",
    "tag_from_file",
    "filename_from_path",
    "parse_component",
    "valid_component_dict",
    "cmpt_name_from_path",
]


def tokanize_name(name: str, normalize: bool = True) -> list[str]:
    """Generates name tokens `some name tokanized` from a filename.
    Assumes filenames is one of:
    * snakecase - some_file_name
    * camel case - someFileName
    * pascal case - SomeFileName

    Args:
        name (str): File name without extension
        normalize (bool): Make all tokens fully lowercase. Defaults to True

    Returns:
        list[str]: List of word tokens.
    """
    tokens = []
    for token in finditer(r"(\b|[A-Z]|_|-|\.)([a-z]+)|([0-9]+)|([A-Z]+)(?=[^a-z])", name):
        first, rest, nums, cap = token.groups()

        if first is not None and first.isupper():
            rest = first + rest
        elif cap is not None and cap.isupper():
            rest = cap
        elif nums is not None and nums.isnumeric():
            rest = str(nums)
        tokens.append(rest.lower() if normalize else rest)
    return tokens


def tag_from_file(filename: str | Path) -> str:
    """Generates a tag name some-tag-name from a filename.
    Assumes filenames of:
    * snakecase - some_file_name
    * camel case - someFileName
    * pascal case - SomeFileName
    """

    if isinstance(filename, Path):
        if filename.is_file():
            filename = filename.name.replace(filename.suffix, "")
        else:
            raise TypeError("If filename is a path it must also be a valid file.")

    tokens = tokanize_name(filename)

    return "-".join(tokens)


def cmpt_name_from_path(file: Path | str, strip: str = "") -> str:
    """Construct a component name given a path. This will include parent directories.
    it will also strip the root directory as this is most commonly not wanted.

    Examples:
        `components/blog/header.phml`

        yields

        `blog-header`
    """
    file = Path(file)
    file = file.with_name(file.name.replace(file.suffix, ""))
    file = sub(strip.strip("/"), "", file.as_posix().lstrip("/")).strip("/")
    dirs = [
        "".join([
            n[0].upper() + n[1:]
            for n in tokanize_name(name, False)
        ])
        for name in file.split("/")
    ]
    return ".".join(dirs)


def filename_from_path(file: Path) -> str:
    """Get the filename without the suffix from a pathlib.Path."""

    return file.name.replace(file.suffix, "")


def valid_component_dict(cmpt: dict) -> bool:
    """Check if a component dict is valid."""
    return bool(
        ("python" in cmpt and isinstance(cmpt["python"], list))
        and ("script" in cmpt and isinstance(cmpt["script"], list))
        and ("style" in cmpt and isinstance(cmpt["script"], list))
        and ("component" in cmpt and isinstance(cmpt["component"], NODE))
    )


def parse_component(ast: AST) -> dict[str, Element]:
    """Helper function to parse the components elements."""
    from phml.utilities import (  # pylint: disable=import-outside-toplevel
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
script, style, or python tag. The root wrapping element must be '<PHML>`\
"""
                )

    if result["component"] is None:
        result["component"] = Element("")

    return result
