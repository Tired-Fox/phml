"""Helper methods for processing dynamic python attributes and blocks."""

from __future__ import annotations

from copy import deepcopy
from re import match, search, sub
from traceback import print_exc
from typing import Optional

from teddecor import TED

from phml.core.nodes import AST, NODE, DocType, Element, Root
from phml.core.virtual_python import VirtualPython, get_python_result, process_python_blocks
from phml.utilities import (
    check,
    find_all,
    replace_node,
    visit_children,
    path_names
)

# ? Change prefix char for `if`, `elif`, and `else` here
CONDITION_PREFIX = "@"

# ? Change prefix char for python attributes here
ATTR_PREFIX = ":"

valid_prev = {
    f"{CONDITION_PREFIX}if": [
        "py-if",
        "py-elif",
        "py-else",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}else",
    ],
    f"{CONDITION_PREFIX}elif": [
        "py-if",
        "py-elif",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
    ],
    f"{CONDITION_PREFIX}else": [
        "py-if",
        "py-elif",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
    ],
}

def __process_props(child: Element, virtual_python: VirtualPython, local_vars: dict) -> dict:
    new_props = {}

    for prop in child.properties:
        if prop.startswith(ATTR_PREFIX):
            local_env = {**virtual_python.context}
            local_env.update(local_vars)
            new_props[prop.lstrip(ATTR_PREFIX)] = get_python_result(
                child[prop], **local_env
            )
        elif match(r".*\{.*\}.*", str(child[prop])) is not None:
            new_props[prop] = process_python_blocks(child[prop], virtual_python, **local_vars)
        else:
            new_props[prop] = child[prop]

    return new_props

def apply_conditions(
    node: Root | Element | AST, 
    virtual_python: VirtualPython, 
    components: dict, 
    **kwargs
):
    """Applys all `py-if`, `py-elif`, and `py-else` to the node
    recursively.

    Args:
        node (Root | Element): The node to recursively apply `py-` attributes too.
        virtual_python (VirtualPython): All of the data from the python elements.
    """
    from .component import replace_components

    if isinstance(node, AST):
        node = node.tree

    replace_components(node, components, virtual_python, **kwargs)
    process_conditions(node, virtual_python, **kwargs)
    process_loops(node, virtual_python, **kwargs)

    for child in node.children:
        if isinstance(child, (Root, Element)):
            apply_conditions(child, virtual_python, components, **kwargs)

def process_loops(node: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Expands all `<For />` tags giving their children context for each iteration."""

    for_loops = [
        loop 
        for loop in visit_children(node) 
        if check(loop, {"tag": "For", ":each": True})
    ]

    kwargs.update(virtual_python.context)

    for loop in for_loops:
        children = run_phml_for(loop, **kwargs)
        replace_node(node, loop, children)

    if len(for_loops) > 0:
        process_conditions(node, virtual_python, **kwargs)

def apply_python(
    current: Root | Element | AST,
    virtual_python: VirtualPython,
    **kwargs,
):
    """Recursively travers the node and search for python blocks. When found
    process them and apply the results.

    Args:
        current (Root | Element): The node to traverse
        virtual_python (VirtualPython): The python elements data
    """

    if isinstance(current, AST):
        current = current.tree

    def process_children(node: Root | Element, local_env: dict):

        for child in node.children:
            if check(child, "element"):
                if "children" in child.context.keys() and len(child.context["children"]) > 0:
                    replace_node(
                        child,
                        ["element", {"tag": "slot"}],
                        child.context["children"],
                    )

                local_vars = {**local_env}
                local_vars.update(child.context)

                child.properties = __process_props(child, virtual_python, local_vars)
                process_children(child, {**local_vars})
            elif (
                check(child, "text")
                and search(r".*\{.*\}.*", str(child.value))
                and child.parent.tag not in ["script", "style"]
                and "code" not in path_names(child)
            ):
                child.value = process_python_blocks(child.value, virtual_python, **local_env)

    process_children(current, {**kwargs})


def py_condition(node: Element) -> bool:
    """Return all python condition attributes on an element."""
    conditions = [
        k
        for k in node.properties.keys()
        if k
        in [
            f"{CONDITION_PREFIX}if",
            f"{CONDITION_PREFIX}elif",
            f"{CONDITION_PREFIX}else",
            # f"{CONDITION_PREFIX}for",
        ]
    ]
    if len(conditions) > 1:
        raise Exception(
            f"There can only be one python condition statement at a time:\n{repr(node)}"
        )
    return conditions[0] if len(conditions) == 1 else None


def __validate_previous_condition(child: Element) -> Optional[Element]:
    idx = child.parent.children.index(child)
    
    def get_previous_condition(idx: int):
        """Get the last conditional element allowing for comments and text"""
        previous = None
        parent = child.parent
        for i in range(idx - 1, -1, -1):
            if isinstance(parent.children[i], Element):
                if py_condition(parent.children[i]) is not None:
                    previous = parent.children[i]
                break
        return previous
    
    previous = get_previous_condition(idx)
    prev_cond = (
        py_condition(previous) if previous is not None and isinstance(previous, Element) else None
    )

    if prev_cond is None or prev_cond not in [
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}if",
    ]:
        raise Exception(
            f"Condition statements that are not @if must have @if or\
 @elif as a previous sibling.\n{child.start_tag()}\
{f' at {child.position}' if child.position is not None else ''}"
        )
    return previous, prev_cond


def process_conditions(tree: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Process all python condition attributes in the phml tree.

    Args:
        tree (Root | Element): The tree to process conditions on.
        virtual_python (VirtualPython): The collection of information from the python blocks.
    """
    conditional_elements = []
    for child in visit_children(tree):
        if check(child, "element"):
            condition = py_condition(child)
            if condition in [
                f"{CONDITION_PREFIX}elif",
                f"{CONDITION_PREFIX}else",
            ]:
                __validate_previous_condition(child)

            if condition is not None:
                conditional_elements.append((condition, child))

    tree.children = execute_conditions(
        conditional_elements,
        tree.children,
        virtual_python,
        **kwargs,
    )


def execute_conditions(
    cond: list[tuple],
    children: list,
    virtual_python: VirtualPython,
    **kwargs,
) -> list:
    """Execute all the conditions. If the condition is a `for` then generate more nodes.
    All other conditions determine if the node stays or is removed.

    Args:
        cond (list[tuple]): The list of conditions to apply. Holds tuples of (condition, node).
        children (list): List of current nodes children.
        virtual_python (VirtualPython): The collection of information from the python blocks.

    Raises:
        Exception: An unkown conditional attribute is being parsed.
        Exception: Condition requirements are not met.

    Returns:
        list: The newly generated/modified list of children.
    """

    # Whether the current conditional branch began with an `if` condition.
    first_cond = False

    # Previous condition that was run and whether it was successful.
    previous = (f"{CONDITION_PREFIX}else", True)

    # Add the python blocks locals to kwargs dict
    kwargs.update(virtual_python.context)

    # Bring python blocks imports into scope
    for imp in virtual_python.imports:
        exec(str(imp))  # pylint: disable=exec-used

    # For each element with a python condition
    for condition, child in cond:
        if condition == f"{CONDITION_PREFIX}if":
            previous = run_phml_if(child, condition, children, **kwargs)

            # Start of condition branch
            first_cond = True

        elif condition == f"{CONDITION_PREFIX}elif":
            # Can only exist if previous condition in branch failed
            previous = run_phml_elif(
                child,
                children,
                condition,
                {
                    "previous": previous,
                    "valid_prev": valid_prev,
                    "first_cond": first_cond,
                },
                **kwargs,
            )
        elif condition == f"{CONDITION_PREFIX}else":

            # Can only exist if previous condition in branch failed
            previous = run_phml_else(
                child,
                children,
                condition,
                {
                    "previous": previous,
                    "valid_prev": valid_prev,
                    "first_cond": first_cond,
                },
            )

            # End any condition branch
            first_cond = False

    return children


def build_locals(child, **kwargs) -> dict:
    """Build a dictionary of local variables from a nodes inherited locals and
    the passed kwargs.
    """
    from phml.utilities import path  # pylint: disable=import-outside-toplevel

    clocals = {**kwargs}

    # Inherit locals from top down
    for parent in path(child):
        if parent.type == "element":
            clocals.update(parent.context)

    clocals.update(child.context)
    return clocals


def run_phml_if(child: Element, condition: str, children: list, **kwargs):
    """Run the logic for manipulating the children on a `if` condition."""

    clocals = build_locals(child, **kwargs)
    result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)

    if result:
        del child[condition]
        return (f"{CONDITION_PREFIX}if", True)

    # Condition failed, so remove the node
    children.remove(child)
    return (f"{CONDITION_PREFIX}if", False)


def run_phml_elif(
    child: Element,
    children: list,
    condition: str,
    variables: dict,
    **kwargs,
):
    """Run the logic for manipulating the children on a `elif` condition."""

    clocals = build_locals(child, **kwargs)

    if variables["previous"][0] in variables["valid_prev"][condition] and variables["first_cond"]:
        if not variables["previous"][1]:
            result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)
            if result:
                del child[condition]
                return (f"{CONDITION_PREFIX}elif", True)

    children.remove(child)
    return variables["previous"]


def run_phml_else(child: Element, children: list, condition: str, variables: dict):
    """Run the logic for manipulating the children on a `else` condition."""

    if variables["previous"][0] in variables["valid_prev"][condition] and variables["first_cond"]:
        if not variables["previous"][1]:
            del child[condition]
            return (f"{CONDITION_PREFIX}else", True)

    # Condition failed so remove element
    children.remove(child)
    return (f"{CONDITION_PREFIX}else", False)


def run_phml_for(node: Element, **kwargs) -> list:
    """Repeat the nested elements inside the `<For />` elements for the iterations provided by the
    `:each` attribute. The values from the `:each` attribute are exposed as context for each node in
    the `<For />` element for each iteration.

    Args:
        node (Element): The `<For />` element that is to be used.
    """
    clocals = build_locals(node)

    # Format for loop condition
    for_loop = sub(r"for |:\s*$", "", node[":each"]).strip()

    # Get local var names from for loop condition
    items = match(r"(for )?(.*)(?<= )in(?= )(.+)", for_loop)
    new_locals = [
        item.strip()
        for item in sub(
            r"\s+",
            " ",
            items.group(2),
        ).split(",")
    ]

    source = items.group(3)

    # Formatter for key value pairs
    key_value = "\"{key}\": {key}"

    # Set children position to 0 since all copies are generated
    children = node.children
    for child in children:
        child.position = None

    def children_with_context(context: dict):
        new_children = []
        for child in children:
            new_child = deepcopy(child)
            if check(new_child, "element"):
                new_child.context.update(context)
            new_children.append(new_child)
        return new_children

    expression = for_loop # original expression

    for_loop = f'''\
new_children = []
for {for_loop}:
    new_children.extend(
        children_with_context(
            {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}}
        )
    )
'''

    # Construct locals for dynamic for loops execution
    local_env = {
        "local_vals": clocals,
    }

    try:
        # Execute dynamic for loop
        exec(  # pylint: disable=exec-used
            for_loop,
            {
                **kwargs,
                **globals(),
                **clocals,
                "children_with_context": children_with_context
            },
            local_env,
        )
    except Exception:  # pylint: disable=broad-except
        TED.print(f"\\[[@Fred]*Error[@]\\] Failed to execute loop expression \
[@Fblue]@for[@]=[@Fgreen]'[@]{expression}[@Fgreen]'[@]")
        print_exc()

    # Return the new complete list of children after generation
    return local_env["new_children"]


class ASTRenderer:
    """Compiles an ast to a hypertext markup language. Compiles to a tag based string."""

    def __init__(self, ast: Optional[AST] = None, _offset: int = 4):
        self.ast = ast
        self.offset = _offset

    def compile(
        self,
        ast: Optional[AST] = None,
        _offset: Optional[int] = None,
        include_doctype: bool = True,
    ) -> str:
        """Compile an ast to html.

        Args:
            ast (AST): The phml ast to compile.
            offset (int | None): The amount to offset for each nested element
            include_doctype (bool): Whether to validate for doctype and auto insert if it is
            missing.
        """

        ast = ast or self.ast
        if ast is None:
            raise Exception("Converting to a file format requires that an ast is provided")

        if include_doctype:
            # Validate doctypes
            doctypes = find_all(ast.tree, "doctype")

            if any(dt.parent is None or dt.parent.type != "root" for dt in doctypes):
                raise Exception("Doctypes must be in the root of the file/tree")

            if len(doctypes) == 0:
                ast.tree.children.insert(0, DocType(parent=ast.tree))

        self.offset = _offset or self.offset
        lines = self.__compile_children(ast.tree)
        return "\n".join(lines)

    def __one_line(self, node, indent: int = 0) -> str:
        return "".join(
            [
                " " * indent + node.start_tag(),
                node.children[0].normalized(
                    indent + self.offset if node.children[0].num_lines > 1 else 0
                ),
                node.end_tag(),
            ]
        )

    def __many_children(self, node, indent: int = 0) -> list:
        lines = []
        for child in visit_children(node):
            if child.type == "element":
                if child.tag == "pre" or "pre" in path_names(child):
                    lines.append(''.join(self.__compile_children(child, 0)))
                else:
                    lines.extend(self.__compile_children(child, indent + self.offset))
            else:
                lines.append(child.stringify(indent + self.offset))
        return lines

    def __construct_element(self, node, indent: int = 0) -> list:
        lines = []
        if (
            len(node.children) == 1
            and node.children[0].type == "text"
            and node.children[0].num_lines == 1
        ):
            lines.append(self.__one_line(node, indent))
        elif len(node.children) == 0:
            lines.append(" " * indent + node.start_tag() + node.end_tag())
        else:
            lines.append(" " * indent + node.start_tag())
            lines.extend(self.__many_children(node, indent))
            lines.append(" " * indent + node.end_tag())
        return lines

    def __compile_children(self, node: NODE, indent: int = 0) -> list[str]:
        lines = []
        if node.type == "element":
            if node.startend:
                lines.append(" " * indent + node.start_tag())
            else:
                lines.extend(self.__construct_element(node, indent))
        elif node.type == "root":
            for child in visit_children(node):
                lines.extend(self.__compile_children(child))
        else:
            lines.append(node.stringify(indent + self.offset))

        return lines
