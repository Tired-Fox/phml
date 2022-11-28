from __future__ import annotations

from copy import deepcopy
from re import sub, match, search
from typing import Optional

from phml.nodes import *
from phml.utils import (
    path,
    visit_children,
    replace_node,
    test,
)
from phml.virtual_python import VirtualPython, get_vp_result, process_vp_blocks

# ? Change prefix char for `if`, `elif`, `else`, and `fore` here
condition_prefix = "@"

# ? Change prefix char for python attributes here
python_attr_prefix = ":"


def replace_components(
    node: Root | Element | AST, components: dict[str, All_Nodes], vp: VirtualPython, **kwargs
):
    """Replace all nodes in the tree with matching components.

    Args:
        node (Root | Element | AST): The starting point.
        vp (VirtualPython): Temp
    """
    from phml.utils import find

    if isinstance(node, AST):
        node = node.tree

    for name, value in components.items():
        curr_node = find(node, ["element", {"tag": name}])
        while curr_node is not None:
            new_props = {}
            for prop in curr_node.properties:
                if prop.startswith((python_attr_prefix, "py-")):
                    new_props[prop.lstrip(python_attr_prefix).lstrip("py-")] = get_vp_result(
                        curr_node.properties[prop], **vp.locals, **kwargs
                    )
                elif match(r".*\{.*\}.*", str(curr_node.properties[prop])) is not None:
                    new_props[prop] = process_vp_blocks(curr_node.properties[prop], vp, **kwargs)
                else:
                    new_props[prop] = curr_node.properties[prop]

            props = new_props
            props["children"] = curr_node.children

            rnode = deepcopy(value["component"])
            rnode.locals.update(props)
            rnode.parent = curr_node.parent

            # Retain conditional properties
            condition = __has_py_condition(curr_node)
            if condition is not None:
                rnode.properties[condition[0]] = condition[1]
                rnode.locals.pop(condition[0], None)

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


def __has_py_condition(node: Element) -> Optional[tuple[str, str]]:
    for cond in [
        "py-for",
        "py-if",
        "py-elif",
        "py-else",
        f"{condition_prefix}if",
        f"{condition_prefix}elif",
        f"{condition_prefix}else",
        f"{condition_prefix}for",
    ]:
        if cond in node.properties.keys():
            return (cond, node.properties[cond])
    return None


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
                if "children" in child.locals.keys():
                    replace_node(child, ["element", {"tag": "slot"}], child.locals["children"])

                le = {**local_env}
                le.update(child.locals)
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
            elif (
                test(child, "text")
                and child.parent.tag not in ["script", "style"]
                and search(r".*\{.*\}.*", child.value) is not None
            ):
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

    # Whether the current conditional branch began with an `if` condition.
    first_cond = False

    # Previous condition that was run and whether it was successful.
    previous = (f"{condition_prefix}for", True)

    # Add the python blocks locals to kwargs dict
    kwargs.update(vp.locals)

    # Bring python blocks imports into scope
    for imp in vp.imports:
        exec(str(imp))

    # For each element with a python condition
    for condition, child in cond:
        if condition in ["py-for", f"{condition_prefix}for"]:

            children = run_py_for(condition, child, children, **kwargs)

            previous = (f"{condition_prefix}for", False)

            # End any condition branch
            first_cond = False

        elif condition in ["py-if", f"{condition_prefix}if"]:

            clocals = build_locals(child, **kwargs)
            result = get_vp_result(
                sub(r"\{|\}", "", child.properties[condition].strip()), **clocals
            )

            if result:
                del child.properties[condition]
                previous = (f"{condition_prefix}if", True)
            else:
                # Condition failed so remove element
                children.remove(child)
                previous = (f"{condition_prefix}if", False)
                
            # Start of condition branch
            first_cond = True

        elif condition in ["py-elif", f"{condition_prefix}elif"]:
            clocals = build_locals(child, **kwargs)

            # Can only exist if previous condition in branch failed
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    result = get_vp_result(
                        sub(r"\{|\}", "", child.properties[condition].strip()), **clocals
                    )
                    if result:
                        del child.properties[condition]
                        previous = (f"{condition_prefix}elif", True)
                    else:
                        
                        # Condition failed so remove element
                        children.remove(child)
                        previous = (f"{condition_prefix}elif", False)
                else:
                    children.remove(child)
            else:
                raise Exception(
                    f"py-elif must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child}"
                )
        elif condition in ["py-else", f"{condition_prefix}else"]:
            
            # Can only exist if previous condition in branch failed
            if previous[0] in valid_prev[condition] and first_cond:
                if not previous[1]:
                    del child.properties[condition]
                    previous = (f"{condition_prefix}else", True)
                else:
                    
                    # Condition failed so remove element
                    children.remove(child)
                    
                # End of condition branch
                first_cond = False
            else:
                raise Exception(
                    f"py-else must follow a py-if. It may follow a py-elif if the first condition was a py-if.\n{child.parent.type}.{child.tag} at {child.position}"
                )
        else:
            raise Exception(f"Unkown condition property: {condition}")

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


def run_py_for(condition: str, child: All_Nodes, children: list, **kwargs) -> list:
    """Take a for loop condition, child node, and the list of children and
    generate new nodes.

    Nodes are duplicates from the child node with variables provided
    from the for loop and child's locals.
    """
    clocals = build_locals(child)

    # Format for loop condition
    for_loop = sub(r"for |:", "", child.properties[condition]).strip()

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
new_children.append(deepcopy(child))
new_children[-1].locals = {{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}, **local_vals}}
children = [*children[:insert], *new_children, *children[insert+1:]]\
'''

    # Prep the child to be used as a copy for new children

    # Delete the py-for condition from child's props
    del child.properties[condition]
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
    exec(
        for_loop,
        {**globals()},
        local_env,
    )

    # Return the new complete list of children after generation
    return local_env["children"]
