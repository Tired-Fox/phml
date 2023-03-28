from enum import EnumType
from typing import Any

from ..nodes import Element
from ..embedded import exec_embedded
from ..utils import build_recursive_context
from .base import comp_step


class Condition(EnumType):
    """Variants of valid conditions.

    Options:
        NONE (-1): No condition 
        IF (0): If condition
        ELIF (1): Else if condition
        ELSE (2): Else condition
    """
    NONE: int = -1
    IF: int = 0
    ELIF: int = 1
    ELSE: int = 2

    @staticmethod
    def to_str(condition: int):
        if condition == 0:
            return "@if"
        elif condition == 1:
            return "@elif"
        elif condition == 2:
            return "@else"
        return "No Condition"

def get_element_condition(node: Element) -> int:
    """Get the single condition attribute on a given element.

    Returns:
        int: -1 - 2 for: No condition, If, Elif, and Else
    """
    conditions = []
    if "@if" in node:
        conditions.append(Condition.IF)
    if "@elif" in node:
        conditions.append(Condition.ELIF)
    if "@else" in node:
        conditions.append(Condition.ELSE)

    if len(conditions) > 1:
        raise ValueError(
            f"More that one condition attribute found at {node.position!r}"
            + ". Expected at most one condition"
        )

    if len(conditions) == 0:
        return Condition.NONE

    return conditions[0]

def validate_condition(prev: int, cond: int, position) -> bool:
    """Validate that the new condition element is valid following the previous element."""
    if (
        (cond > Condition.NONE and cond <= Condition.ELSE) # pattern: if, elif, else
        and (
            cond == Condition.IF # pattern: else -> if, elif -> if, if -> if, None -> if
            or (prev == Condition.ELIF and cond == Condition.ELIF) # pattern: elif -> elif
            or (prev > Condition.NONE and cond > prev) # pattern: if -> else, if -> elif, elif -> else
        )
        ):
        return True
    print(prev, cond)
    raise ValueError(f"Invalid condition element order at {position!r}. Expected if -> (elif -> else) | else")

def build_condition_trees(node: Element) -> list[list[Element]]:
    """Iterates sibling nodes and creates condition trees from adjacent nodes with condition attributes."""
    condition_trees = []
    if node.children is not None:
        # 0 == if, 1 == elif, 2 == else
        previous = Condition.NONE
        for child in node:
            if isinstance(child, Element):
                condition = get_element_condition(child)
                if condition > Condition.NONE and validate_condition(previous, condition, node.position):
                    if condition == Condition.IF:
                        condition_trees.append([(condition, child)])
                    else:
                        condition_trees[-1].append((condition, child))
                previous = condition

    return condition_trees 

def get_condition_result(cond: tuple[int, Element], context: dict[str, Any], position) -> bool:
    """Parse the python condition in the attribute and return the result.

    Raises:
        ValueError: When the condition result is not a boolean
    """
    if cond[0] != Condition.ELSE:
        condition = Condition.to_str(cond[0])
        code = str(cond[1].get(condition)).strip()

        result = exec_embedded(
            code,
            f"<{cond[1].tag} {condition}='{code}'>",
            **build_recursive_context(cond[1], context)
        )

        if not isinstance(result, bool):
            raise ValueError(
                f"Expected boolean expression in condition "
                + f"attribute '{condition}' at {position!r}"
            )

        return result
    return True

def compile_condition_trees(node, trees: list[list[tuple[int, Element]]], context):
    """Compiles the conditions. This will removed False condition nodes and keep True condition nodes."""
    for tree in trees:
        state = -1
        for i, cond in enumerate(tree):
            result = get_condition_result(cond, context, node.position)
            if not result:
                cond[1].parent.remove(cond[1])
            else:
                cond[1].pop(Condition.to_str(cond[0]), None)
                for c in tree[i+1:]:
                    c.parent.remove(c)
                break
        

@comp_step
def step_execute_conditions(
        *,
        node: Element,
        context: dict[str, Any]
):
    """Step to process and compile condition attributes in sibling nodes."""
    cond_trees = build_condition_trees(node)
    compile_condition_trees(node, cond_trees, context)
