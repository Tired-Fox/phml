from __future__ import annotations

from copy import deepcopy
from re import match, sub
from traceback import print_exc
from teddecor import TED
from phml.core.nodes import Root, Element, AST, Text, NODE
from phml.core.virtual_python import VirtualPython, process_python_blocks, get_python_result
from phml.utilities import find, offset, normalize_indent, query, replace_node, check

from .compile import py_condition, CONDITION_PREFIX, valid_prev

__all__ = ["substitute_component", "replace_components", "combine_component_elements"]


WRAPPER_TAG = ["Template", ""]

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

    curr_node = find(node, ["element", {"tag": component[0]}])
    used_components: dict[str, tuple[dict, dict]] = {}

    if curr_node is not None:
        context, used_components[component[0]] = process_context(*component)

        # Assign props to locals and remaining attributes stay
        curr_node.parent.children = apply_component(
            curr_node,
            component[0],
            component[1],
            used_components,
            virtual_python,
            context,
            kwargs
        )

        __add_component_elements(node, used_components, "style")
        __add_component_elements(node, used_components, "python")
        __add_component_elements(node, used_components, "script")

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

    used_components: dict[str, tuple[dict, dict]] = {}

    for name, value in components.items():
        elements = [element for element in node.children if check(element, {"tag": name})]

        context = {}
        if len(elements) > 0:
            context, used_components[name] = process_context(name, value)

        for curr_node in elements:
            curr_node.parent.children = apply_component(
                curr_node,
                name,
                value,
                used_components,
                virtual_python,
                context,
                kwargs
            )

    # Optimize, python, style, and script tags from components
    __add_component_elements(node, used_components, "style")
    __add_component_elements(node, used_components, "script")

def get_props(node, name, value, used_components, virtual_python, **kwargs) -> dict[str, str]:
    props = used_components[name][1].pop("Props", {})
    extra_props = {}
    attrs = value["component"].properties

    attributes = node.properties

    for item in attributes:
        attr_name = item.lstrip(":").lstrip("py-")
        if attr_name in props:
            # Get value if pythonic
            context = build_locals(node, **kwargs)
            if item.startswith((":", "py-")):
                # process as python
                context.update(virtual_python.context)
                result = get_python_result(attributes[item], **context)
            else:
                # process python blocks
                result = process_python_blocks(
                    attributes[item],
                    virtual_python,
                    **context
                )
            if (
                isinstance(result, str)
                and result.lower() in ["true", "false", "yes", "no"]
            ):
                result = True if result.lower() in ["true", "yes"] else False
            props[attr_name] = result
        elif attr_name not in attrs and item not in attrs:
            # Add value to attributes
            if (
                isinstance(attributes[item], str)
                and attributes[item].lower() in ["true", "false", "yes", "no"]
            ):
                attributes[item] = True if attributes[item].lower() in ["true", "yes"] else False
            extra_props[attr_name] = attributes[item]

    if len(extra_props) > 0:
        props["props"] = extra_props

    return props, attrs

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
    kwargs.update(virtual_python.context)

    # Bring python blocks imports into scope
    for imp in virtual_python.imports:
        exec(str(imp))  # pylint: disable=exec-used

    # For each element with a python condition
    if condition in ["py-for", f"{CONDITION_PREFIX}for"]:
        new_children = run_py_for(condition, child, **kwargs)
        return new_children
    elif condition in ["py-if", f"{CONDITION_PREFIX}if"]:
        child = run_py_if(child, condition, **kwargs)
        return [child]
    elif condition in ["py-elif", f"{CONDITION_PREFIX}elif"]:
        # Can only exist if previous condition in branch failed
        child = run_py_elif(
            child,
            condition,
            {
                "previous": previous,
                "valid_prev": valid_prev,
                "first_cond": first_cond,
            },
            **kwargs,
        )
        return [child]
    elif condition in ["py-else", f"{CONDITION_PREFIX}else"]:

        # Can only exist if previous condition in branch failed
        child = run_py_else(
            child,
            condition,
            {
                "previous": previous,
                "valid_prev": valid_prev,
                "first_cond": first_cond,
            },
            **kwargs
        )
        return [child]

def process_context(name, value):
    context = {}

    local_virtual_python = VirtualPython()
    for python in value["python"]:
        if len(python.children) == 1 and check(python.children[0], "text"):
            text = python.children[0].value
            local_virtual_python += VirtualPython(text)

    if "Props" in local_virtual_python.context:
        if not isinstance(local_virtual_python.context["Props"], dict):
            raise Exception(
                f"Props must be a dict was "
                + f"{type(local_virtual_python.context['Props']).__name__}: <{name} />"
            )

    context = {
        key:value 
        for key,value in local_virtual_python.context.items()
        if key != "Props"
    }

    return context, (value, local_virtual_python.context)

def apply_component(node, name, value, used_components, virtual_python, context, kwargs) -> list:
    props, attrs = get_props(
        node,
        name,
        value,
        used_components,
        virtual_python,
        **kwargs
    )

    node.properties = attrs
    node.context = props

    condition = py_condition(node)
    results = [node]
    if condition is not None:
        results = execute_condition(condition, node, virtual_python, **kwargs)

    # replace the valid components in the results list
    new_children = []
    for child in results:
        attrs = child.properties
        # get props and locals from current node
        props, attrs = node.context, node.properties
        props.update(context)
        props["children"] = node.children

        component = deepcopy(value["component"])
        if component.tag in WRAPPER_TAG:
            # Create a copy of the component
            for sub_child in component.children:
                if isinstance(sub_child, Element):
                    sub_child.context.update(props)
                    sub_child.parent = node.parent

            new_children.extend(component.children)
        else:
            component.context = props
            component.properties = attrs
            component.parent = node.parent
            new_children.append(component)
    # replace the curr_node with the list of replaced nodes
    parent = node.parent
    index = parent.children.index(node)
    return parent.children[:index] + new_children + parent.children[index+1:]

def __add_component_elements(node, used_components: dict, tag: str):
    if find(node, {"tag": tag}) is not None:
        new_elements = __retrieve_component_elements(used_components, tag)
        if len(new_elements) > 0:
            replace_node(
                node,
                {"tag": tag},
                combine_component_elements(
                    [
                        find(node, {"tag": tag}),
                        *new_elements,
                    ],
                    tag,
                ),
            )
    else:
        new_element = combine_component_elements(
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


def combine_component_elements(elements: list[Element], tag: str) -> Element:
    """Combine text from elements like python, script, and style.

    Returns:
        Element: With tag of element list but with combined text content
    """

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
        if element in value[0]:
            result.extend(value[0][element])
    return result

def run_py_if(child: Element, condition: str, **kwargs):
    """Run the logic for manipulating the children on a `if` condition."""

    clocals = build_locals(child, **kwargs)
    result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)

    if result:
        return child

    # Condition failed, so remove the node
    return child


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
                return child

    return child


def run_py_else(child: Element, condition: str, variables: dict, **kwargs):
    """Run the logic for manipulating the children on a `else` condition."""

    if variables["previous"][0] in variables["valid_prev"][condition] and variables["first_cond"]:
        if not variables["previous"][1]:
            clocals = build_locals(child, **kwargs)
            result = get_python_result(sub(r"\{|\}", "", child[condition].strip()), **clocals)
            if result:
                return child

    # Condition failed so remove element
    return child


def run_py_for(condition: str, child: NODE, **kwargs) -> list:
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
    expression = for_loop
    for_loop = f'''\
new_children = []
for {for_loop}:
    new_child = deepcopy(child)
    new_child.context = {{**local_vals}}
    new_child.context.update({{{", ".join([f"{key_value.format(key=key)}" for key in new_locals])}}})
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
        TED.print(f"\\[[@Fred]*Error[@]\\] Failed to execute loop expression \
[@Fblue]@for[@]=[@Fgreen]'[@]{expression}[@Fgreen]'[@]")
        print_exc()

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
            clocals.update(parent.context)

    clocals.update(child.context)
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
