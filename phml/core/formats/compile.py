"""Helper methods for processing dynamic python attributes and blocks."""

from __future__ import annotations

from copy import deepcopy
from re import match, search, sub
from typing import Optional
import ast

from phml.core.nodes import AST, All_Nodes, DocType, Element, Root
from phml.core.virtual_python import VirtualPython, get_vp_result, process_vp_blocks
from phml.utilities import check, find, find_all, replace_node, visit_children

# ? Change prefix char for `if`, `elif`, `else`, and `fore` here
CONDITION_PREFIX = "@"

# ? Change prefix char for python attributes here
ATTR_PREFIX = ":"

valid_prev = {
    "py-for": [
        "py-if",
        "py-elif",
        "py-else",
        "py-for",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}else",
        f"{CONDITION_PREFIX}for",
    ],
    "py-if": [
        "py-if",
        "py-elif",
        "py-else",
        "py-for",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}else",
        f"{CONDITION_PREFIX}for",
    ],
    "py-elif": ["py-if", "py-elif", f"{CONDITION_PREFIX}if", f"{CONDITION_PREFIX}elif"],
    "py-else": ["py-if", "py-elif", f"{CONDITION_PREFIX}if", f"{CONDITION_PREFIX}elif"],
    f"{CONDITION_PREFIX}for": [
        "py-if",
        "py-elif",
        "py-else",
        "py-for",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}else",
        f"{CONDITION_PREFIX}for",
    ],
    f"{CONDITION_PREFIX}if": [
        "py-if",
        "py-elif",
        "py-else",
        "py-for",
        f"{CONDITION_PREFIX}if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}else",
        f"{CONDITION_PREFIX}for",
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


def replace_components(
    node: Root | Element | AST,
    components: dict[str, All_Nodes],
    virtual_python: VirtualPython,
    **kwargs,
):
    """Replace all nodes in the tree with matching components.

    Args:
        node (Root | Element | AST): The starting point.
        virtual_python (VirtualPython): Temp
    """

    if isinstance(node, AST):
        node = node.tree

    def find_next():
        for name, value in components.items():
            curr_node = find(node, ["element", {"tag": name}])
            if curr_node is not None:
                return curr_node, value
        return None, None

    curr_node, value = find_next()
    while curr_node is not None:
        new_props = {}

        # Retain conditional properties
        condition = py_condition(curr_node)
        if condition is not None:
            new_props[condition] = curr_node[condition]
            del curr_node[condition]

        # Generate and process the props
        props = __process_props(curr_node, virtual_python, kwargs)
        props["children"] = curr_node.children

        # Create a duplicate of the component and assign values
        rnode = deepcopy(value["component"])
        rnode.locals.update(props)
        rnode.parent = curr_node.parent

        # Replace the component
        idx = curr_node.parent.children.index(curr_node)
        curr_node.parent.children = (
            curr_node.parent.children[:idx]
            + [
                *components[curr_node.tag]["python"],
                *components[curr_node.tag]["script"],
                *components[curr_node.tag]["style"],
                rnode,
            ]
            + curr_node.parent.children[idx + 1 :]
        )

        # Find the next node that is of the current component.
        curr_node, value = find_next()


def apply_conditions(node: Root | Element | AST, virtual_python: VirtualPython, **kwargs):
    """Applys all `py-if`, `py-elif`, `py-else`, and `py-for` to the node
    recursively.

    Args:
        node (Root | Element): The node to recursively apply `py-` attributes too.
        virtual_python (VirtualPython): All of the data from the python elements.
    """

    if isinstance(node, AST):
        node = node.tree

    process_conditions(node, virtual_python, **kwargs)
    for child in node.children:
        if isinstance(child, (Root, Element)):
            apply_conditions(child, virtual_python, **kwargs)


def __process_props(child: Element, virtual_python: VirtualPython, local_vars: dict) -> dict:
    new_props = {}

    for prop in child.properties:
        if prop.startswith((ATTR_PREFIX, "py-")):
            local_env = {**virtual_python.exposable}
            local_env.update(local_vars)
            new_props[prop.lstrip(ATTR_PREFIX).lstrip("py-")] = get_vp_result(
                child[prop], **local_env
            )
        elif match(r".*\{.*\}.*", str(child[prop])) is not None:
            new_props[prop] = process_vp_blocks(child[prop], virtual_python, **local_vars)
        else:
            new_props[prop] = child[prop]

    return new_props


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
                if "children" in child.locals.keys():
                    replace_node(child, ["element", {"tag": "slot"}], child.locals["children"])

                local_vars = {**local_env}
                local_vars.update(child.locals)

                child.properties = __process_props(child, virtual_python, local_vars)
                process_children(child, {**local_vars})
            elif (
                check(child, "text")
                and child.parent.tag not in ["script", "style"]
                and search(r".*\{.*\}.*", child.value) is not None
            ):
                child.value = process_vp_blocks(child.value, virtual_python, **local_env)

    process_children(current, {**kwargs})


def py_condition(node: Element) -> bool:
    """Return all python condition attributes on an element."""
    conditions = [
        k
        for k in node.properties.keys()
        if k
        in [
            "py-for",
            "py-if",
            "py-elif",
            "py-else",
            f"{CONDITION_PREFIX}if",
            f"{CONDITION_PREFIX}elif",
            f"{CONDITION_PREFIX}else",
            f"{CONDITION_PREFIX}for",
        ]
    ]
    if len(conditions) > 1:
        raise Exception(
            f"There can only be one python condition statement at a time:\n{repr(node)}"
        )
    return conditions[0] if len(conditions) == 1 else None


def __validate_previous_condition(child: Element) -> Optional[str]:
    idx = child.parent.children.index(child)
    previous = child.parent.children[idx - 1] if idx > 0 else None
    prev_cond = (
        py_condition(previous) if previous is not None and isinstance(previous, Element) else None
    )

    if prev_cond is None or prev_cond not in [
        "py-elif",
        "py-if",
        f"{CONDITION_PREFIX}elif",
        f"{CONDITION_PREFIX}if",
    ]:
        raise Exception(
            f"Condition statements that are not py-if or py-for must have py-if or\
 py-elif as a prevous sibling.\n{child.start_tag()}\
{f' at {child.position}' if child.position is not None else ''}"
        )


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
                "py-elif",
                "py-else",
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
    previous = (f"{CONDITION_PREFIX}for", True)

    # Add the python blocks locals to kwargs dict
    kwargs.update(virtual_python.exposable)

    # Bring python blocks imports into scope
    for imp in virtual_python.imports:
        exec(str(imp))  # pylint: disable=exec-used

    # For each element with a python condition
    for condition, child in cond:
        if condition in ["py-for", f"{CONDITION_PREFIX}for"]:

            children = run_py_for(condition, child, children, **kwargs)

            previous = (f"{CONDITION_PREFIX}for", False)

            # End any condition branch
            first_cond = False

        elif condition in ["py-if", f"{CONDITION_PREFIX}if"]:
            previous = run_py_if(child, condition, children, **kwargs)

            # Start of condition branch
            first_cond = True

        elif condition in ["py-elif", f"{CONDITION_PREFIX}elif"]:
            # Can only exist if previous condition in branch failed
            previous = run_py_elif(
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
        elif condition in ["py-else", f"{CONDITION_PREFIX}else"]:

            # Can only exist if previous condition in branch failed
            previous = run_py_else(
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
            clocals.update(parent.locals)

    clocals.update(child.locals)
    return clocals


def run_py_if(child: Element, condition: str, children: list, **kwargs):
    """Run the logic for manipulating the children on a `if` condition."""

    clocals = build_locals(child, **kwargs)
    result = get_vp_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)

    if result:
        del child[condition]
        return (f"{CONDITION_PREFIX}if", True)

    # Condition failed, so remove the node
    children.remove(child)
    return (f"{CONDITION_PREFIX}if", False)


def run_py_elif(
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
            result = get_vp_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)
            if result:
                del child[condition]
                return (f"{CONDITION_PREFIX}elif", True)

    children.remove(child)
    return variables["previous"]


def run_py_else(child: Element, children: list, condition: str, variables: dict):
    """Run the logic for manipulating the children on a `else` condition."""

    if variables["previous"][0] in variables["valid_prev"][condition] and variables["first_cond"]:
        if not variables["previous"][1]:
            del child[condition]
            return (f"{CONDITION_PREFIX}else", True)

    # Condition failed so remove element
    children.remove(child)
    return (f"{CONDITION_PREFIX}else", False)


def run_py_for(condition: str, child: All_Nodes, children: list, **kwargs) -> list:
    """Take a for loop condition, child node, and the list of children and
    generate new nodes.

    Nodes are duplicates from the child node with variables provided
    from the for loop and child's locals.
    """
    clocals = build_locals(child)

    # Format for loop condition
    for_loop = sub(r"for |:", "", child[condition]).strip()

    # Get local var names from for loop condition
    new_locals = [
        item.strip()
        for item in sub(
            r"\s+",
            " ",
            match(r"(for )?(.*)(?<= )in(?= )", for_loop).group(2),
        ).split(",")
    ]

    # Formatter for key value pairs
    key_value = "\"{key}\": {key}"

    # Start index on where to insert generated children
    insert = children.index(child)

    # Construct dynamic for loop
    #   Uses for loop condition from above
    #       Creates deepcopy of looped element
    #       Adds locals from what was passed to exec and what is from for loop condition
    #       concat and generate new list of children
    for_loop = f'''\
new_children = []
for {for_loop}:
    new_child = deepcopy(child)
    new_child.locals = {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}, **local_vals}}
    children = [*children[:insert], new_child, *children[insert+1:]]
    insert += 1\
'''

    # Prep the child to be used as a copy for new children

    # Delete the py-for condition from child's props
    del child[condition]
    # Set the position to None since the copies are generated
    child.position = None

    # Construct locals for dynamic for loops execution
    local_env = {
        "children": children,
        "insert": insert,
        "child": child,
        "local_vals": clocals,
    }

    try:
        # Execute dynamic for loop
        exec(  # pylint: disable=exec-used
            for_loop,
            {
                **kwargs,
                **clocals,
                **globals(),
            },
            local_env,
        )
    except Exception as exception:
        from teddecor import TED
        new_line = "\n"
        TED.print(f"[@F red]*Error[@]: {TED.encode(str(exception))} [@F yellow]|[@] {TED.encode(for_loop.split(new_line)[1].replace('for', '').replace(':', '')).replace(' in ', '[@F green] in [@]')}")

    # Return the new complete list of children after generation
    return local_env["children"]


class ToML:
    """Compiles an ast to a hypertext markup language. Compiles to a tag based string."""

    def __init__(self, ast: Optional[AST] = None, offset: int = 4):
        self.ast = ast
        self.offset = offset

    def compile(
        self,
        ast: Optional[AST] = None,
        offset: Optional[int] = None,
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

        self.offset = offset or self.offset
        lines = self.__compile_children(ast.tree)
        return "\n".join(lines)

    def __one_line(self, node, indent: int = 0) -> str:
        return "".join(
            [
                " " * indent + node.start_tag(),
                node.children[0].stringify(
                    indent + self.offset if node.children[0].num_lines > 1 else 0
                ),
                node.end_tag(),
            ]
        )

    def __many_children(self, node, indent: int = 0) -> list:
        lines = []
        for child in visit_children(node):
            if child.type == "element":
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
        else:
            lines.append(" " * indent + node.start_tag())
            lines.extend(self.__many_children(node, indent))
            lines.append(" " * indent + node.end_tag())
        return lines

    def __compile_children(self, node: All_Nodes, indent: int = 0) -> list[str]:
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
