from pathlib import Path
from nodes import *


def parse(path: str | Path):
    """Parse a given pehl file to AST following hast and unist."""

    if Path(path).suffix == ".pehl":
        with open(Path(path), "r", encoding="utf-8") as source:
            src = source.read()

        print(src)
    else:
        raise Exception(
            f"File has invalid extension. Was '{Path(path).suffix}' expected '.pehl'"
        )
