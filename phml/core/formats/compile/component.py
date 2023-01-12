from __future__ import annotations

from copy import deepcopy
from re import match, sub
from phml.core.nodes import Root, Element, AST, Text, All_Nodes
from phml.core.virtual_python import VirtualPython, process_python_blocks, get_python_result
from phml.utilities import find, offset, normalize_indent, query, replace_node, check

from .compile import py_condition, CONDITION_PREFIX, valid_prev

__all__ = ["substitute_component", "replace_components"]

def substitute_component(
    node: Root | Element | AST,
    component: tuple[str, dict],
    virtual_python: VirtualPython,
    **kwargs,
):
    """Replace the first occurance of a component.

    Args:
        node (Root | Element | AST): The starting point.
        virtual_python (VirtualPython): The python state to use while evaluating prop values
    """

    if isinstance(node, AST):
        node = node.tree

    new_props = {}
    name = component[0]
    value = component[1]

    curr_node = find(node, ["element", {"tag": component[0]}])

    if curr_node is not None:
        def get_props() -> dict[str, str]:
            props = {}
            attrs = {}
            attributes = value["component"].properties
            for prop in attributes:
                if prop.startswith("@"):
                    continue
                elif prop.startswith("#"):
                    props[prop.lstrip("#")] = attributes[prop]
                else:
                    attrs[prop] = attributes[prop]

            attributes = curr_node.properties

            for prop in attributes:
                attr_name = prop.lstrip(":").lstrip("py-")
                if attr_name in props:
                    # Get value if pythonic
                    context = build_locals(curr_node, **kwargs)
                    if prop.startswith((":", "py-")):
                        # process as python
                        context.update(virtual_python.exposable)
                        props[attr_name] = get_python_result(attributes[prop], **context)
                    else:
                        # process python blocks
                        result = process_python_blocks(
                            attributes[prop], 
                            virtual_python, 
                            **context
                        )
                        if (
                            isinstance(result, str) 
                            and result.lower() in ["true", "false", "yes", "no"]
                        ):
                            result = True if result.lower() in ["true", "yes"] else False
                        props[attr_name] = result
                else:
                    # Add value to attributes
                    attrs[prop] = attributes[prop]

            return props, attrs

        # Assign props to locals and remaining attributes stay
        props, attrs = get_props()
        curr_node.properties = attrs
        curr_node.locals = props

        def execute_condition(
            condition: str,
            child: Element,
            virtual_python: VirtualPython,
            **kwargs,
        ) -> list:
            conditions = __get_previous_conditions(child)

            first_cond = (
                conditions[0] in [f"{CONDITION_PREFIX}if", "py-if"] 
                if len(conditions) > 0 else False
            )

            previous = (conditions[-1] if len(conditions) > 0 else "py-for", True)

            # Add the python blocks locals to kwargs dict
            kwargs.update(virtual_python.exposable)

            # Bring python blocks imports into scope
            for imp in virtual_python.imports:
                exec(str(imp))  # pylint: disable=exec-used

            state = False

            # For each element with a python condition
            if condition in ["py-for", f"{CONDITION_PREFIX}for"]:
                new_children = run_py_for(condition, child, **kwargs)
                return True, new_children
            elif condition in ["py-if", f"{CONDITION_PREFIX}if"]:
                state, child = run_py_if(child, condition, **kwargs)
                return state, [child]
            elif condition in ["py-elif", f"{CONDITION_PREFIX}elif"]:
                # Can only exist if previous condition in branch failed
                state, child = run_py_elif(
                    child,
                    condition,
                    {
                        "previous": previous,
                        "valid_prev": valid_prev,
                        "first_cond": first_cond,
                    },
                    **kwargs,
                )
                return state, [child]
            elif condition in ["py-else", f"{CONDITION_PREFIX}else"]:

                # Can only exist if previous condition in branch failed
                state, child = run_py_else(
                    child,
                    condition,
                    {
                        "previous": previous,
                        "valid_prev": valid_prev,
                        "first_cond": first_cond,
                    },
                    **kwargs
                )
                return state, [child]

        condition = py_condition(curr_node)
        state = True
        results = [curr_node]
        if condition is not None:
            state, results = execute_condition(condition, curr_node, virtual_python, **kwargs)

        # replace the valid components in the results list
        for i, child in enumerate(results):
            if child.tag == curr_node.tag:
                # get props and locals from current node
                props, attrs = curr_node.locals, curr_node.properties
                props["children"] = curr_node.children

                # Create a copy of the component
                new_node = deepcopy(value["component"])
                new_node.locals = props
                new_node.properties = attrs
                new_node.parent = curr_node.parent

                results[i] = new_node

        # replace the curr_node with the list of replaced nodes
        parent = curr_node.parent
        index = parent.children.index(curr_node)
        parent.children = parent.children[:index] + results + parent.children[index+1:]

        __add_component_elements(node, {component[0]: component[1]}, "style")
        __add_component_elements(node, {component[0]: component[1]}, "python")
        __add_component_elements(node, {component[0]: component[1]}, "script")

def replace_components(
    node: Root | Element | AST,
    components: dict[str, dict],
    virtual_python: VirtualPython,
    **kwargs,
):
    """Iterate through components and replace all of each component in the nodes children.
    Non-recursive.

    Args:
        node (Root | Element | AST): The starting point.
        virtual_python (VirtualPython): Temp
    """

    if isinstance(node, AST):
        node = node.tree

    used_components = {}

    for name, value in components.items():
        elements = [element for element in node.children if check(element, {"tag": name})]

        if len(elements) > 0:
            used_components[name] = value

        for curr_node in elements:
            def get_props() -> dict[str, str]:
                props = {}
                attrs = {}
                attributes = value["component"].properties
                for prop in attributes:
                    if prop.startswith("@"):
                        continue
                    elif prop.startswith("#"):
                        props[prop.lstrip("#")] = attributes[prop]
                    else:
                        attrs[prop] = attributes[prop]

                attributes = curr_node.properties

                for prop in attributes:
                    attr_name = prop.lstrip(":").lstrip("py-")
                    if attr_name in props:
                        # Get value if pythonic
                        context = build_locals(curr_node, **kwargs)
                        if prop.startswith((":", "py-")):
                            # process as python
                            context.update(virtual_python.exposable)
                            props[attr_name] = get_python_result(attributes[prop], **context)
                        else:
                            # process python blocks
                            result = process_python_blocks(
                                attributes[prop], 
                                virtual_python, 
                                **context
                            )
                            if (
                                isinstance(result, str) 
                                and result.lower() in ["true", "false", "yes", "no"]
                            ):
                                result = True if result.lower() in ["true", "yes"] else False
                            props[attr_name] = result
                    else:
                        # Add value to attributes
                        attrs[prop] = attributes[prop]

                return props, attrs

            # Assign props to locals and remaining attributes stay
            props, attrs = get_props()
            curr_node.properties = attrs
            curr_node.locals = props

            def execute_condition(
                condition: str,
                child: Element,
                virtual_python: VirtualPython,
                **kwargs,
            ) -> list:
                conditions = __get_previous_conditions(child)

                first_cond = (
                    conditions[0] in [f"{CONDITION_PREFIX}if", "py-if"] 
                    if len(conditions) > 0 else False
                )

                previous = (conditions[-1] if len(conditions) > 0 else "py-for", True)

                # Add the python blocks locals to kwargs dict
                kwargs.update(virtual_python.exposable)

                # Bring python blocks imports into scope
                for imp in virtual_python.imports:
                    exec(str(imp))  # pylint: disable=exec-used

                state = False

                # For each element with a python condition
                if condition in ["py-for", f"{CONDITION_PREFIX}for"]:
                    new_children = run_py_for(condition, child, **kwargs)
                    return True, new_children
                elif condition in ["py-if", f"{CONDITION_PREFIX}if"]:
                    state, child = run_py_if(child, condition, **kwargs)
                    return state, [child]
                elif condition in ["py-elif", f"{CONDITION_PREFIX}elif"]:
                    # Can only exist if previous condition in branch failed
                    state, child = run_py_elif(
                        child,
                        condition,
                        {
                            "previous": previous,
                            "valid_prev": valid_prev,
                            "first_cond": first_cond,
                        },
                        **kwargs,
                    )
                    return state, [child]
                elif condition in ["py-else", f"{CONDITION_PREFIX}else"]:

                    # Can only exist if previous condition in branch failed
                    state, child = run_py_else(
                        child,
                        condition,
                        {
                            "previous": previous,
                            "valid_prev": valid_prev,
                            "first_cond": first_cond,
                        },
                        **kwargs
                    )
                    return state, [child]

            condition = py_condition(curr_node)
            state = True
            results = [curr_node]
            if condition is not None:
                state, results = execute_condition(condition, curr_node, virtual_python, **kwargs)

            # replace the valid components in the results list
            for i, child in enumerate(results):
                if child.tag == curr_node.tag:
                    # get props and locals from current node
                    props, attrs = curr_node.locals, curr_node.properties
                    props["children"] = curr_node.children

                    # Create a copy of the component
                    new_node = deepcopy(value["component"])
                    new_node.locals = props
                    new_node.properties = attrs
                    new_node.parent = curr_node.parent

                    results[i] = new_node

            # replace the curr_node with the list of replaced nodes
            parent = curr_node.parent
            index = parent.children.index(curr_node)
            parent.children = parent.children[:index] + results + parent.children[index+1:]

    # Optimize, python, style, and script tags from components
    __add_component_elements(node, used_components, "style")
    __add_component_elements(node, used_components, "python")
    __add_component_elements(node, used_components, "script")


def __add_component_elements(node, used_components: dict, tag: str):
    if find(node, {"tag": tag}) is not None:
        new_elements = __retrieve_component_elements(used_components, tag)
        if len(new_elements) > 0:
            replace_node(
                node,
                {"tag": tag},
                __combine_component_elements(
                    [
                        find(node, {"tag": tag}),
                        *new_elements,
                    ],
                    tag,
                ),
            )
    else:
        new_element = __combine_component_elements(
            __retrieve_component_elements(used_components, tag),
            tag,
        )
        if new_element.children[0].value.strip() != "":
            if tag == "style":
                head = query(node, "head")
                if head is not None:
                    head.append(new_element)
                else:
                    node.append(new_element)
            else:
                html = query(node, "html")
                if html is not None:
                    html.append(new_element)
                else:
                    node.append(new_element)


def __combine_component_elements(elements: list[Element], tag: str) -> Element:
    values = []

    indent = -1
    for element in elements:
        if len(element.children) == 1 and isinstance(element.children[0], Text):
            # normalize values
            if indent == -1:
                indent = offset(element.children[0].value)
            values.append(normalize_indent(element.children[0].value, indent))

    return Element(tag, children=[Text("\n\n".join(values))])


def __retrieve_component_elements(collection: dict, element: str) -> list[Element]:
    result = []
    for value in collection.values():
        if element in value:
            result.extend(value[element])
    return result

def run_py_if(child: Element, condition: str, **kwargs):
    """Run the logic for manipulating the children on a `if` condition."""

    clocals = build_locals(child, **kwargs)
    result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)

    if result:
        return (True, child)

    # Condition failed, so remove the node
    return (False, child)


def run_py_elif(
    child: Element,
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
                return (True, child)

    return (False, child)


def run_py_else(child: Element, condition: str, variables: dict, **kwargs):
    """Run the logic for manipulating the children on a `else` condition."""

    if variables["previous"][0] in variables["valid_prev"][condition] and variables["first_cond"]:
        if not variables["previous"][1]:
            clocals = build_locals(child, **kwargs)
            result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)
            if result:
                return (True, child)

    # Condition failed so remove element
    return (False, child)


def run_py_for(condition: str, child: All_Nodes, **kwargs) -> list:
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

    # Construct dynamic for loop
    #   Uses for loop condition from above
    #       Creates deepcopy of looped element
    #       Adds locals from what was passed to exec and what is from for loop condition
    #       add generated element to list
    for_loop = f'''\
new_children = []
for {for_loop}:
    new_child = deepcopy(child)
    new_child.locals = {{**local_vals}}
    new_child.locals.update({{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}})
    new_children.append(new_child)
'''

    # Prep the child to be used as a copy for new children

    # Delete the py-for condition from child's attributes
    del child[condition]
    # Set the position to None since the copies are generated
    child.position = None

    # Construct locals for dynamic for loops execution
    local_env = {
        "child": child,
        "local_vals": clocals,
        "deepcopy": deepcopy
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
    except Exception as exception:  # pylint: disable=broad-except
        from teddecor import TED  # pylint: disable=import-outside-toplevel

        new_line = "\n"
        TED.print(
            f"""[@F red]*Error <component.py:439:8>[@]: {TED.encode(str(exception))} [@F yellow]|[@] \
{
    TED.escape(for_loop.split(new_line)[1]
    .replace('for', '')
    .replace(':', ''))
    .replace(' in ', '[@F green] in [@]')
}"""
        )
        
        print(exception)

    # Return the new complete list of children after generation
    return local_env["new_children"]

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

def __get_previous_conditions(child: Element) -> list[str]:
    idx = child.parent.children.index(child)
    conditions = []
    for i in range(0, idx):
        if isinstance(child.parent.children[i], Element):
            condition = py_condition(child.parent.children[i])
            if condition is not None:
                conditions.append(condition)

    return conditions
