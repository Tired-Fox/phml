from __future__ import annotations
from copy import deepcopy
from functools import cached_property
from typing import Iterator
from re import sub, match

from phml.nodes import (
    Root,
    Element,
)  # , Node, DocType, Parent, Literal, Comment, Text, Position, Point, Properties, PropertyName, PropertyValue

from phml.VirtualPython import VirtualPython, get_vp_result, process_vp_blocks
from phml.utils.transform import walk, size
from phml.utils.travel import visit_children
from phml.utils.test import test
from phml.utils.find import find_all
from phml.utils.transform import remove_nodes

__all__ = ["AST"]


class AST:
    """PHML ast.

    Contains utility functions that can manipulate the ast.
    """

    def __init__(self, tree: Root | Element):
        self.tree = tree

    def __iter__(self) -> Iterator:
        return walk(self.tree)

    def __eq__(self, obj) -> bool:
        if isinstance(obj, self.__class__):
            if self.tree == obj.tree:
                return True

        return False

    @cached_property
    def size(self) -> int:
        """Get the number of nodes in the ast tree."""

        size(self.tree)

    def inspect(self) -> str:
        """Return the full tree's inspect data."""
        return self.tree.inspect()

    def source(self) -> str:
        """Get the ast as a phml string."""
        return self.tree.phml()

    def json(self) -> str:
        """Get the ast as a json string."""
        return self.tree.json()

    def render(self, **kwargs) -> str:
        """Get the ast as a rendered html string.
        
        By default it will parse the `<python>` tags and use it's
        data. However, you may also pass in **kwargs for additional
        data in the file. If there is a naming conflict the `<python>`
        tags local variables will override the passed variables.
        """

        html = deepcopy(self.tree)

        # 1. Search for all python elements and get source info.
        #    - Remove when done
        vp = VirtualPython()

        for pb in find_all(html, {"tag": "python"}):
            if len(pb.children) == 1:
                if pb.children[0].type == "text":
                    vp += VirtualPython(pb.children[0].value)

        remove_nodes(html, ["element", {"tag": "python"}])

        # 2. Search each element and find py-if, py-elif, py-else, and py-for
        #    - Execute those statements

        apply_conditions(html, vp, **kwargs)


        # 3. Search for python blocks and process them.

        apply_python(html, vp, **kwargs)

        # 4. Take the final manipulated tree and stringify
        #    - Since phml just returns a string representation of the nodes
        #       recursively it can be used here on the modified tree.
        return html.phml()

def apply_conditions(node: Root | Element, vp: VirtualPython, **kwargs):
    """Applys all `py-if`, `py-elif`, `py-else`, and `py-for` to the node
    recursively.

    Args:
        node (Root | Element): The node to recursively apply `py-` attributes too.
        vp (VirtualPython): All of the data from the python elements.
    """
    process_conditions(node, vp, **kwargs)
    for child in node.children:
        if isinstance(child, (Root, Element)):
            apply_conditions(child, vp, **kwargs)


def apply_python(node: Root | Element, vp: VirtualPython, **kwargs):
    """Recursively travers the node and search for python blocks. When found
    process them and apply the results.

    Args:
        node (Root | Element): The node to traverse
        vp (VirtualPython): The python elements data
    """
    def process_children(n: Root | Element, local_env: dict):
        for child in n.children:
            if test(child, "element"):
                le = {**local_env, **child.locals}
                new_props = {}
                for prop in child.properties:
                    if prop.startswith("py-"):
                        new_props[prop.lstrip("py-")] = get_vp_result(
                            child.properties[prop], **le, **vp.locals
                        )
                    elif match(r".*\{.*\}.*", child.properties[prop]) is not None:
                        new_props[prop] = process_vp_blocks(child.properties[prop], vp, **le)
                    else:
                        new_props[prop] = child.properties[prop]

                child.properties = new_props
                process_children(child, {**le})
            elif test(child, "text") and child.parent.tag not in ["script", "style"]:
                child.value = process_vp_blocks(child.value, vp, **local_env)

    process_children(node, {**kwargs})


def process_conditions(tree: Root | Element, vp: VirtualPython, **kwargs):
    def py_conditions(node) -> bool:
        return [k for k in node.properties.keys() if k in ["py-for", "py-if", "py-elif", "py-else"]]

    conditions = []
    for child in visit_children(tree):
        if test(child, "element"):
            if len(py_conditions(child)) == 1:
                conditions.append((py_conditions(child)[0], child))
            elif len(py_conditions(child)) > 1:
                raise Exception(
                    f"There can only be one of 'py-if', 'py-elif', 'py-else',\
or 'py-for' at a time:\n{child.phml()}"
                )

    tree.children = execute_conditions(conditions, tree.children, vp, **kwargs)


def execute_conditions(cond: list[tuple], children: list, vp: VirtualPython, **kwargs) -> list:


    valid_prev = {
        "py-for": ["py-if", "py-elif", "py-else", "py-for"],
        "py-if": ["py-if", "py-elif", "py-else", "py-for"],
        "py-elif": ["py-if", "py-elif"],
        "py-else": ["py-if", "py-elif"],
    }

    first_cond = False
    previous = "py-for"

    kwargs.update(vp.locals)
    for imp in vp.imports:
        exec(str(imp))

    for condition, child in cond:
        if condition == "py-for":
            # TODO: Split for loop into it's own function
            for_loop = sub(r"for |:", "", child.properties[condition]).strip()
            new_locals = (
                sub(
                    r"\s+",
                    " ",
                    match(r"(for )?(.*)in", for_loop).group(2),
                )
                .strip()
                .split(", ")
            )
            key_value = "\"{key}\": {key}"
            insert = children.index(child)

            for_loop = f'''\
new_children = []
for {for_loop}:
    new_children.append(deepcopy(child))
    new_children[-1].locals = {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}}
children = [*children[:insert], *new_children, *children[insert+1:]]\
'''

            del child.properties[condition]
            child.position = None

            local_env = {
                "children": children,
                "insert": insert,
                "child": child,
                **kwargs,
            }
            exec(
                for_loop,
                {**globals()},
                local_env,
            )
            
            children = local_env["children"]
            previous = ("py-for", False)
            first_cond = False
        elif condition == "py-if":
            result = get_vp_result(sub(r"\{|\}", "", child.properties[condition].strip()), **kwargs)
            if result:
                del child.properties[condition]
                previous = ("py-if", True)
            else:
                children.remove(child)
                previous = ("py-if", False)
            first_cond = True
        elif condition == "py-elif":
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    result = get_vp_result(
                        sub(r"\{|\}", "", child.properties[condition].strip()), **kwargs
                    )
                    if result:
                        del child.properties[condition]
                        previous = ("py-elif", True)
                    else:
                        children.remove(child)
                        previous = ("py-elif", False)
                else:
                    children.remove(child)
            else:
                raise Exception(f"py-elif must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child}")
        elif condition == "py-else":
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    child.properties[condition]
                    previous = ("py-else", True)
                else:
                    children.remove(child)
                first_cond = False
            else:
                raise Exception(f"py-else must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child.parent.type}.{child.tag} at {child.position}")
        else:
            raise Exception(f"Unkown condition property: {condition}")
    
    return children