from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Optional
from .parent import Parent

if TYPE_CHECKING:
    from .position import Position
    from .element import Element
    from .doctype import DocType
    from .comment import Comment
    from .text import Text


class Root(Parent):
    """Root (Parent) represents a document.

    Root can be used as the root of a tree, or as a value
    of the content field on a 'template' Element, never as a child.
    """

    def __init__(
        self,
        position: Optional[Position] = None,
        children: Optional[list] = None,
    ):  # pylint: disable=useless-parent-delegation
        super().__init__(position, children)
        self.parent = None

    def __eq__(self, obj) -> bool:
        if hasattr(obj, "type") and self.type == obj.type:
            if self.position != obj.position:
                # print(f"{self.position} != {obj.position}: Position values are not equal")
                return False
            for c, oc in zip(self.children, obj.children):
                if c != oc:
                    # print(f"{c} != {oc}: Children values are not equal")
                    return False
            return True
        else:
            # print(f"{self.type} != {obj.type}: {type(self).__name__} can not be equated to {type(obj).__name__}")
            return False

    def as_dict(self) -> dict:
        """Convert root node to a dict."""

        return {"type": self.type, "children": [child.as_dict() for child in self.children]}

    def tree(self) -> Iterator[str]:
        """Yields the tree representation of the node."""
        yield f"ROOT [{len(self.children)}]"
        for i, child in enumerate(self.children):
            if len(self.children) > 1:
                if i == len(self.children) - 1:
                    sep = "└"
                else:
                    sep = "├"
            else:
                sep = "└"
            yield from child.tree(0, sep)

    def inspect(self) -> str:
        """Return an inspected tree view of the node."""
        return "\n".join(self.tree())

    def json(self, indent: int = 2) -> str:
        """Convert root node and all children to a json string."""
        from json import dumps  # pylint: disable=import-outside-toplevel

        return dumps(self.as_dict(), indent=indent)

    def phml(self, indent: int = 0) -> str:
        """Build indented html string of documents elements and their children.

        Returns:
            str: Built html of document
        """
        out = []
        out.extend([child.phml() for child in self.children])
        return "\n".join(out)

    def __str__(self) -> str:
        return f"root [{len(self.children)}]"
