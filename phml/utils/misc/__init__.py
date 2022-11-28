from pathlib import Path
from phml.nodes import Root, Element
from .classes import *
from .heading import *
from .inspect import *

# __all__ = [
#     "depth",
#     "size",
#     "heading_rank",
#     "classnames",
#     "ClassList",
#     "inspect",
#     "normalize_indent",
# ]


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


def depth(el) -> int:
    """Get the depth in the tree for a given node.

    -1 means that you passed in the tree itself and you are at the
    ast's root.
    """

    level = -1
    while el.parent is not None:
        level += 1
        el = el.parent

    return level


def size(node: Root | Element) -> int:
    """Get the number of nodes recursively."""
    from phml.utils import walk

    count = 0

    for _ in walk(node):
        count += 1

    return count
