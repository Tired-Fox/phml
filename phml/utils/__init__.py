"""phml.Utils

This is a collection of utility functions that allow for manipulation, traversal,
and discovery inside a phml.ast.AST.
"""

from .locate import *
from .misc import *
from .transform import *
from .travel import *
from .validate import *


# def inspect(node, sep: dict = {"child": "├", "last": "└", "vert_line": "│"}) -> str:
#     """Takes any node in the tree and
#     returns the inspect string form.
#     """
    
#     def inspect_children(node, depth: int = 0, count: int = -1, last: bool = False) -> str:
#         data = []
            
#         label = node.type
#         if hasattr(node, "tag"):
#             label += f"<{node.tag}>"
#         if hasattr(node, "children"):
#             label += f"[{len(node.children)}]"
#         if hasattr(node, "value"):
#             label += f'"{node.value}"'
#         if hasattr(node, "position") and node.position is not None:
#             label += f" ({node.position})"
        
#         data.append(label)
#         additional_info = ["data", "properties"]
#         for ai in additional_info:
#             if hasattr(node, ai):
#                 data.append(f"{count}│ {ai}: {getattr(node, ai)}")
            
#         for i, child in enumerate(travel.visit_children(node)):
#             pass
    
#     if node.type in ["root", "element"]:
#         return inspect_children(node)
#     else:
#         return str(node)
