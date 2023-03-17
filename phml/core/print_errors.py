import sys
from saimll import SAIML
from phml.core.nodes import NODE, Element

__all__ = ["print_warn"]


def print_warn(file: str = "", node: NODE | None = None, message: str = ""):
    sys.stderr.write(SAIML.parse("\\[[@Fyellow]*WARN[@]\\]"))

    if file is not None and file != "":
        pos = ""
        if node is not None and node.position is not None:
            pos = f"[{node.position.start.line}:{node.position.start.column}]"
        file = file if file is not None and file != "" else "__temp__" 
        sys.stderr.write(f" \x1b[32m{file+pos!r}\x1b[39m")

    if node is not None:
        if isinstance(node, Element):
            sys.stderr.write(SAIML.parse(f" <[@Fmagenta]{node.tag}[@F] />"))

    if message is not None and message != "":
                                sys.stderr.write(": " + message)
    sys.stderr.write("\n\n")
    sys.stderr.flush()
