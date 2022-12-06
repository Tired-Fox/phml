"""Helper methods for processing dynamic python attributes and blocks."""

from __future__ import annotations

from copy import deepcopy
from re import match, search, sub
from typing import Optional

from phml.nodes import AST, All_Nodes, Element, Root
from phml.utils import check, find, path, replace_node, visit_children
from phml.virtual_python import VirtualPython, get_vp_result, process_vp_blocks

# ? Change prefix char for `if`, `elif`, `else`, and `fore` here
CONDITION_PREFIX = "@"

# ? Change prefix char for python attributes here
ATTR_PREFIX = ":"


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

    for name, value in components.items():
        curr_node = find(node, ["element", {"tag": name}])
        while curr_node is not None:
            new_props = {}

            # Retain conditional properties
            conditions = py_conditions(curr_node)
            if len(conditions) > 0:
                for condition in conditions:
                    new_props[condition] = curr_node[condition]

            for prop in curr_node.properties:
                if prop not in conditions:
                    if prop.startswith((ATTR_PREFIX, "py-")):
                        local_env = {**kwargs}
                        local_env.update(virtual_python.locals)
                        new_props[prop.lstrip(ATTR_PREFIX).lstrip("py-")] = get_vp_result(
                            curr_node[prop], **local_env
                        )
                    elif match(r".*\{.*\}.*", str(curr_node[prop])) is not None:
                        new_props[prop] = process_vp_blocks(
                            curr_node[prop], virtual_python, **kwargs
                        )
                    else:
                        new_props[prop] = curr_node[prop]

            props = new_props
            props["children"] = curr_node.children

            rnode = deepcopy(value["component"])
            rnode.locals.update(props)
            rnode.parent = curr_node.parent

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
            curr_node = find(node, ["element", {"tag": name}])


# def __has_py_condition(node: Element) -> Optional[tuple[str, str]]:
#     for cond in [
#         "py-for",
#         "py-if",
#         "py-elif",
#         "py-else",
#         f"{CONDITION_PREFIX}if",
#         f"{CONDITION_PREFIX}elif",
#         f"{CONDITION_PREFIX}else",
#         f"{CONDITION_PREFIX}for",
#     ]:
#         if cond in node.properties.keys():
#             return (cond, node[cond])
#     return None


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
                new_props = {}

                for prop in child.properties:
                    if prop.startswith((ATTR_PREFIX, "py-")):
                        local_env = {**virtual_python.locals}
                        local_env.update(local_vars)
                        new_props[prop.lstrip(ATTR_PREFIX).lstrip("py-")] = get_vp_result(
                            child[prop], **local_env
                        )
                    elif match(r".*\{.*\}.*", str(child[prop])) is not None:
                        new_props[prop] = process_vp_blocks(
                            child[prop], virtual_python, **local_vars
                        )
                    else:
                        new_props[prop] = child[prop]

                child.properties = new_props
                process_children(child, {**local_vars})
            elif (
                check(child, "text")
                and child.parent.tag not in ["script", "style"]
                and search(r".*\{.*\}.*", child.value) is not None
            ):
                child.value = process_vp_blocks(child.value, virtual_python, **local_env)

    process_children(current, {**kwargs})


def py_conditions(node: Element) -> bool:
    """Return all python condition attributes on an element."""
    return [
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


def process_conditions(tree: Root | Element, virtual_python: VirtualPython, **kwargs):
    """Process all python condition attributes in the phml tree.

    Args:
        tree (Root | Element): The tree to process conditions on.
        virtual_python (VirtualPython): The collection of information from the python blocks.
    """

    conditions = []
    for child in visit_children(tree):
        if check(child, "element"):
            if len(py_conditions(child)) == 1:
                if py_conditions(child)[0] not in [
                    "py-for",
                    "py-if",
                    f"{CONDITION_PREFIX}for",
                    f"{CONDITION_PREFIX}if",
                ]:
                    idx = child.parent.children.index(child)
                    previous = child.parent.children[idx - 1] if idx > 0 else None
                    prev_cond = (
                        py_conditions(previous)
                        if previous is not None and isinstance(previous, Element)
                        else None
                    )
                    if (
                        prev_cond is not None
                        and len(prev_cond) == 1
                        and prev_cond[0]
                        in ["py-elif", "py-if", f"{CONDITION_PREFIX}elif", f"{CONDITION_PREFIX}if"]
                    ):
                        conditions.append((py_conditions(child)[0], child))
                    else:
                        raise Exception(
                            f"Condition statements that are not py-if or py-for must have py-if or\
 py-elif as a prevous sibling.\n{child.start_tag()}{f' at {child.position}' or ''}"
                        )
                else:
                    conditions.append((py_conditions(child)[0], child))
            elif len(py_conditions(child)) > 1:
                raise Exception(
                    f"There can only be one python condition statement at a time:\n{repr(child)}"
                )

    tree.children = execute_conditions(conditions, tree.children, virtual_python, **kwargs)


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

    # Whether the current conditional branch began with an `if` condition.
    first_cond = False

    # Previous condition that was run and whether it was successful.
    previous = (f"{CONDITION_PREFIX}for", True)

    # Add the python blocks locals to kwargs dict
    kwargs.update(virtual_python.locals)

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

            # Condition failed so remove element
            children.remove(child)
            return (f"{CONDITION_PREFIX}elif", False)

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
            match(r"(for )?(.*)in", for_loop).group(2),
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
        **kwargs,
    }

    # Execute dynamic for loop
    exec(  # pylint: disable=exec-used
        for_loop,
        {**globals()},
        local_env,
    )

    # Return the new complete list of children after generation
    return local_env["children"]
