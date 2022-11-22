from __future__ import annotations

from copy import deepcopy
from re import sub, match
from typing import Any, Callable, Optional

from phml.core.file_types import HTML, JSON, PHML, Markdown
from phml.nodes import AST, All_Nodes, Root, Element, Position, DocType
from phml.utils.travel import visit_children
from phml.utils.locate.find import find_all
from phml.utils.transform.transform import remove_nodes
from phml.utils.validate.test import test
from phml.virtual_python import VirtualPython, get_vp_result, process_vp_blocks

__all__ = ["Compiler"]


# ? Change prefix char for `if`, `elif`, `else`, and `fore` here
condition_prefix = ""

# ? Change prefix char for python attributes here
python_attr_prefix = "#"


class Compiler:
    """Used to compile phml into other formats. HTML, PHML,
    JSON, Markdown, etc...
    """

    ast: AST
    """phml ast used by the compiler to generate a new format."""

    def __init__(self, ast: Optional[AST] = None):
        self.ast = ast
        self.file = None

    def compile(
        self,
        ast: Optional[AST] = None,
        to_format: str = HTML,
        indent: Optional[int] = None,
        handler: Optional[Callable] = None,
        **kwargs: Any,
    ) -> str:
        """Execute compilation to a different format."""

        ast = ast or self.ast

        if ast is None:
            raise Exception("Must provide an ast to compile.")

        doctypes = [dt for dt in visit_children(ast.tree) if test(dt, "doctype")]
        if len(doctypes) == 0:
            ast.tree.children.insert(0, DocType(ast.tree))

        if to_format == PHML:
            return self.__phml(ast, indent or 4)
        elif to_format == HTML:
            return self.__html(ast, indent or 4, **kwargs)
        elif to_format == JSON:
            return self.__json(ast, indent or 2)
        elif to_format == Markdown:
            return self.__markdown(ast)
        elif handler is None:
            raise Exception(f"Unkown format < { to_format } >")
        else:
            return handler(ast, indent)

    def __phml(self, ast: AST, indent: int = 0) -> str:
        return self.__to_html(ast, indent)

    def __html(self, ast: AST, indent: int = 0, **kwargs) -> str:
        html = deepcopy(ast)

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

        return self.__to_html(html, indent)

    def __json(self, ast: AST, indent: int = 0) -> str:
        from json import dumps

        def compile_children(node: Root | Element) -> dict:
            data = {"type": node.type}

            if data["type"] == "root":
                if node.parent is not None:
                    raise Exception("Root nodes must only occur as the root of an ast/tree.")

            for attr in vars(node):
                if attr not in ["parent", "children"]:
                    value = getattr(node, attr)
                    if isinstance(value, Position):
                        data[attr] = value.as_dict()
                    else:
                        data[attr] = value

            if hasattr(node, "children"):
                data["children"] = []
                for child in visit_children(node):
                    data["children"].append(compile_children(child))

            return data

        data = compile_children(ast.tree)
        return dumps(data, indent=indent)

    def __markdown(self, ast: AST) -> str:
        raise NotImplementedError("Markdown is not supported.")

    def __to_html(self, ast: AST, offset: int = 0) -> str:
        def compile_children(node: All_Nodes, indent: int = 0) -> list[str]:
            data = []
            if node.type == "element":
                if node.startend:
                    data.append(" " * indent + node.start_tag())
                else:
                    if (
                        len(node.children) == 1
                        and node.children[0].type == "text"
                        and node.children[0].num_lines == 1
                    ):
                        out = []
                        out.append(" " * indent + node.start_tag())
                        out.append(
                            node.children[0].stringify(
                                indent + offset if node.children[0].num_lines > 1 else 0
                            )
                        )
                        out.append(node.end_tag())
                        data.append("".join(out))
                    else:
                        data.append(" " * indent + node.start_tag())
                        for c in visit_children(node):
                            if c.type == "element":
                                data.extend(compile_children(c, indent + offset))
                            else:
                                data.append(c.stringify(indent + offset))
                        data.append(" " * indent + node.end_tag())
            elif node.type == "root":
                for child in visit_children(node):
                    data.extend(compile_children(child))
            else:
                data.append(node.stringify(indent + offset))
            return data

        data = compile_children(ast.tree)
        return "\n".join(data)


def apply_conditions(node: Root | Element | AST, vp: VirtualPython, **kwargs):
    """Applys all `py-if`, `py-elif`, `py-else`, and `py-for` to the node
    recursively.

    Args:
        node (Root | Element): The node to recursively apply `py-` attributes too.
        vp (VirtualPython): All of the data from the python elements.
    """

    if isinstance(node, AST):
        node = node.tree

    process_conditions(node, vp, **kwargs)
    for child in node.children:
        if isinstance(child, (Root, Element)):
            apply_conditions(child, vp, **kwargs)


def apply_python(node: Root | Element | AST, vp: VirtualPython, **kwargs):
    """Recursively travers the node and search for python blocks. When found
    process them and apply the results.

    Args:
        node (Root | Element): The node to traverse
        vp (VirtualPython): The python elements data
    """

    if isinstance(node, AST):
        node = node.tree

    def process_children(n: Root | Element, local_env: dict):

        for child in n.children:
            if test(child, "element"):
                le = {**local_env, **child.locals}
                new_props = {}
                for prop in child.properties:
                    if prop.startswith((python_attr_prefix, "py-")):
                        new_props[prop.lstrip(python_attr_prefix).lstrip("py-")] = get_vp_result(
                            child.properties[prop], **le, **vp.locals
                        )
                    elif match(r".*\{.*\}.*", str(child.properties[prop])) is not None:
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
        return [
            k
            for k in node.properties.keys()
            if k
            in [
                "py-for",
                "py-if",
                "py-elif",
                "py-else",
                f"{condition_prefix}if",
                f"{condition_prefix}elif",
                f"{condition_prefix}else",
                f"{condition_prefix}for",
            ]
        ]

    conditions = []
    for child in visit_children(tree):
        if test(child, "element"):
            if len(py_conditions(child)) == 1:
                conditions.append((py_conditions(child)[0], child))
            elif len(py_conditions(child)) > 1:
                raise Exception(
                    f"There can only be one python condition statement at a time:\n{repr(child)}"
                )

    tree.children = execute_conditions(conditions, tree.children, vp, **kwargs)


def execute_conditions(cond: list[tuple], children: list, vp: VirtualPython, **kwargs) -> list:

    valid_prev = {
        "py-for": [
            "py-if",
            "py-elif",
            "py-else",
            "py-for",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
            f"{condition_prefix}else",
            f"{condition_prefix}for",
        ],
        "py-if": [
            "py-if",
            "py-elif",
            "py-else",
            "py-for",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
            f"{condition_prefix}else",
            f"{condition_prefix}for",
        ],
        "py-elif": ["py-if", "py-elif", f"{condition_prefix}if", f"{condition_prefix}elif"],
        "py-else": ["py-if", "py-elif", f"{condition_prefix}if", f"{condition_prefix}elif"],
        f"{condition_prefix}for": [
            "py-if",
            "py-elif",
            "py-else",
            "py-for",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
            f"{condition_prefix}else",
            f"{condition_prefix}for",
        ],
        f"{condition_prefix}if": [
            "py-if",
            "py-elif",
            "py-else",
            "py-for",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
            f"{condition_prefix}else",
            f"{condition_prefix}for",
        ],
        f"{condition_prefix}elif": [
            "py-if",
            "py-elif",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
        ],
        f"{condition_prefix}else": [
            "py-if",
            "py-elif",
            f"{condition_prefix}if",
            f"{condition_prefix}elif",
        ],
    }

    first_cond = False
    previous = f"{condition_prefix}for"

    kwargs.update(vp.locals)
    for imp in vp.imports:
        exec(str(imp))

    for condition, child in cond:
        if condition in ["py-for", f"{condition_prefix}for"]:
            # TODO: Split for loop into it's own function
            for_loop = sub(r"for |:", "", child.properties[condition]).strip()
            new_locals = [
                item.strip()
                for item in sub(
                    r"\s+",
                    " ",
                    match(r"(for )?(.*)in", for_loop).group(2),
                ).split(",")
            ]
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
            previous = (f"{condition_prefix}for", False)
            first_cond = False
        elif condition in ["py-if", f"{condition_prefix}if"]:
            result = get_vp_result(sub(r"\{|\}", "", child.properties[condition].strip()), **kwargs)
            if result:
                del child.properties[condition]
                previous = (f"{condition_prefix}if", True)
            else:
                children.remove(child)
                previous = (f"{condition_prefix}if", False)
            first_cond = True
        elif condition in ["py-elif", f"{condition_prefix}elif"]:
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    result = get_vp_result(
                        sub(r"\{|\}", "", child.properties[condition].strip()), **kwargs
                    )
                    if result:
                        del child.properties[condition]
                        previous = (f"{condition_prefix}elif", True)
                    else:
                        children.remove(child)
                        previous = (f"{condition_prefix}elif", False)
                else:
                    children.remove(child)
            else:
                raise Exception(
                    f"py-elif must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child}"
                )
        elif condition in ["py-else", f"{condition_prefix}else"]:
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    child.properties[condition]
                    previous = (f"{condition_prefix}else", True)
                else:
                    children.remove(child)
                first_cond = False
            else:
                raise Exception(
                    f"py-else must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child.parent.type}.{child.tag} at {child.position}"
                )
        else:
            raise Exception(f"Unkown condition property: {condition}")

    return children
