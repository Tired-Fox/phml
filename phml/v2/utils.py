from pathlib import Path
from typing import Iterator
from traceback import print_tb

from .nodes import Parent, Node


def iterate_nodes(node: Parent) -> Iterator[Node]:
    """Recursively iterate over nodes and their children."""
    yield from node
    for child in node:
        if isinstance(child, Parent):
            yield from iterate_nodes(child)
            
def calc_offset(content: str | list[str]) -> int:
    """Get the leading offset of the first line of the string."""
    content = content.split("\n") if isinstance(content, str) else content
    return len(content[0]) - len(content[0].lstrip())

def strip_blank_lines(data_lines: list[str]) -> list[str]:
    """Strip the blank lines at the start and end of a list."""
    data_lines = [line.replace("\r\n", "\n") for line in data_lines]
    # remove leading blank lines
    for idx in range(0, len(data_lines)):  # pylint: disable=consider-using-enumerate
        if data_lines[idx].strip() != "":
            data_lines = data_lines[idx:]
            break
        if idx == len(data_lines) - 1:
            data_lines = []
            break

    # Remove trailing blank lines
    if len(data_lines) > 0:
        for idx in range(len(data_lines) - 1, -1, -1):
            if data_lines[idx].replace("\n", " ").strip() != "":
                data_lines = data_lines[: idx + 1]
                break

    return data_lines


def normalize_indent(content: str, indent: int = 0) -> str:
    """Normalize the indent between all lines.

    Args:
        content (str): The content to normalize the indent for
        indent (bool): The amount of offset to add to each line after normalization.

    Returns:
        str: The normalized string
    """

    content = str(content).split("\n")
    offset = len(content[0]) - len(content[0].lstrip())
    lines = []
    for line in content:
        if len(line) > 0 and calc_offset(line) >= offset:
            lines.append(" " * indent + line[offset:])
        else:
            lines.append(line)
    return "\n".join(strip_blank_lines(lines))

class PHMLTryCatch:
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
