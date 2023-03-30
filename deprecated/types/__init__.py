from typing import TypeAlias
from pathlib import Path
from phml.core.nodes import AST
from phml.core.nodes.nodes import NODE

__all__ = [
    "PathLike",
    "Component",
    "Components",
]

PathLike: TypeAlias = str | Path
Component = dict[str, list | NODE] | AST | PathLike

ComponentsDict: TypeAlias = dict[str, Component]
ComponentsTuple: TypeAlias = tuple[str, Component]
Components: TypeAlias = (
    ComponentsDict
    | ComponentsTuple
    | list[PathLike]
    | PathLike
)
