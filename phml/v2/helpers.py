from pathlib import Path
from typing import Iterator, Any
from traceback import print_tb

from phml.v2.nodes import Parent, Node, AST, Element

def build_recursive_context(node: Node, context: dict[str, Any]) -> dict[str, Any]:
    """Build recursive context for the current node."""
    parent = node.parent
    parents = []
    result = {**context}

    while parent is not None and not isinstance(parent, AST):
        parents.append(parent)
        parent = parent.parent
    
    for parent in parents:
        result.update(parent.context)

    if isinstance(node, Element):
        result.update(node.context)
    return result


def iterate_nodes(node: Parent) -> Iterator[Node]:
    """Recursively iterate over nodes and their children."""
    yield from node
    for child in node:
        if isinstance(child, Parent):
            yield from iterate_nodes(child)
            
def calc_offset(content: str) -> int:
    """Get the leading offset of the first line of the string."""
    return len(content) - len(content.lstrip())

def strip_blank_lines(data: str) -> str:
    """Strip the blank lines at the start and end of a list."""
    data = data.rstrip().replace("\r\n", "\n")
    data_lines = data.split("\n")

    # remove leading blank lines
    for idx in range(0, len(data_lines)):  # pylint: disable=consider-using-enumerate
        if data_lines[idx].strip() != "":
            return "\n".join(data_lines[idx:])

    return ""


def normalize_indent(content: str, indent: int = 0) -> str:
    """Normalize the indent between all lines.

    Args:
        content (str): The content to normalize the indent for
        indent (bool): The amount of offset to add to each line after normalization.

    Returns:
        str: The normalized string
    """

    lines = strip_blank_lines(content).split("\n")
    offset = calc_offset(lines[0])

    result = []
    for line in lines:
        if len(line) > 0:
            result.append(
                " " * indent
                + line[min(calc_offset(line), offset):]
            )
        else:
            result.append(line)
    return "\n".join(result)

class PHMLTryCatch:
    """Context manager around core PHML actions. When an exception is raised
    it is caught here and the current file that is being handled is prepended
    to the exception message.
    """
    def __init__(self, path: str|Path|None = None):
        self._path = str(path or "")

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None and not isinstance(exc_val, SystemExit):
            print_tb(exc_tb)
            if self._path != "":
                print(f'[{self._path}]:', exc_val)
            else:
                print(exc_val)
            exit()

