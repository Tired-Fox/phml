"""phml.utilities.misc.inspect

Logic to inspect any phml node. Outputs a tree representation
of the node as a string.
"""

from json import dumps, JSONEncoder

from phml.core.nodes import AST, NODE, Comment, Element, Root, Text

__all__ = ["inspect", "normalize_indent"]


def inspect(start: AST | NODE, indent: int = 2):
    """Recursively inspect the passed node or ast."""

    if isinstance(start, AST):
        start = start.tree

    def recursive_inspect(node: Element | Root, indent: int) -> list[str]:
        """Generate signature for node then for each child recursively."""
        from phml import visit_children  # pylint: disable=import-outside-toplevel

        results = [*signature(node)]

        for idx, child in enumerate(visit_children(node)):
            if isinstance(child, (Element, Root)):
                lines = recursive_inspect(child, indent)

                child_prefix = (
                    "\x1b[38;5;8m└\x1b[39m"
                    if idx == len(node.children) - 1
                    else "\x1b[38;5;8m├\x1b[39m"
                )
                nested_prefix = (
                    " " if idx == len(node.children) - 1 else "\x1b[38;5;8m│\x1b[39m"
                )

                lines[0] = f"{child_prefix}\x1b[38;5;8m{idx}\x1b[39m {lines[0]}"
                if len(lines) > 1:
                    for line in range(1, len(lines)):
                        lines[line] = f"{nested_prefix}  {lines[line]}"
                results.extend(lines)
            else:
                lines = signature(child, indent)

                child_prefix = (
                    "\x1b[38;5;8m└\x1b[39m"
                    if idx == len(node.children) - 1
                    else "\x1b[38;5;8m├\x1b[39m"
                )
                nested_prefix = (
                    " " if idx == len(node.children) - 1 else "\x1b[38;5;8m│\x1b[39m"
                )

                lines[0] = f"{child_prefix}\x1b[38;5;8m{idx}\x1b[39m {lines[0]}"
                if len(lines) > 1:
                    for line in range(1, len(lines)):
                        lines[line] = f"{nested_prefix}  {lines[line]}"

                results.extend(lines)
        return results

    if isinstance(start, (Element, Root)):
        return "\n".join(recursive_inspect(start, indent))

    return "\n".join(signature(start))


def signature(node: NODE, indent: int = 2):
    """Generate the signature or base information for a single node."""
    sig = ""
    # element node's tag
    if isinstance(node, Element):
        sig += f"\x1b[34m{node.tag}\x1b[39m"
    else:
        sig = f"\x1b[34m{node.type}\x1b[39m"

    # count of children in parent node
    if isinstance(node, (Element, Root)):
        sig += f" \x1b[38;5;8m[{len(node.children) if len(node.children) > 0 else '/'}]\x1b[39m"

    # position of non generated nodes
    if node.position is not None:
        sig += f" {node.position}"

    result = [sig]

    # element node's properties
    if hasattr(node, "properties"):
        for line in stringify_props(node):
            result.append(f"\x1b[38;5;8m│\x1b[39m{' '*indent}{line}")

    # literal node's value
    if isinstance(node, (Text, Comment)):
        for line in build_literal_value(node):
            result.append(f"\x1b[38;5;8m│\x1b[39m{' '*indent}\x1b[32m{line}\x1b[39m")

    return result


class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return JSONEncoder.default(self, obj)
        except:
            return repr(obj)


def stringify_props(node: Element) -> list[str]:
    """Generate a list of lines from strigifying the nodes properties."""

    if len(node.properties.keys()) > 0:
        lines = ["properties: \x1b[38;5;8m{\x1b[39m"]
        for key, value in node.properties.items():
            if value is None or isinstance(value, bool):
                value = f"\x1b[38;5;104m{value}\x1b[39m"
            elif isinstance(value, str):
                value = f'\x1b[32m"{value}"\x1b[39m'
            lines.append(f'  \x1b[32m"{key}"\x1b[39m: {value},')
        lines.append("\x1b[38;5;8m}\x1b[39m")
        return lines
    return []


def build_literal_value(node: Text | Comment) -> list[str]:
    """Build the lines for the string value of a literal node."""

    lines = normalize_indent(node.value).split("\n")

    if len(lines) == 1:
        lines[0] = f'"{lines[0]}"'
    else:
        lines[0] = f'"{lines[0]}'
        lines[-1] = f' {lines[-1]}"'
        if len(lines) > 2:
            for idx in range(1, len(lines) - 1):
                lines[idx] = f" {lines[idx]}"
    return lines


def normalize_indent(text: str) -> str:
    """Remove extra prefix whitespace while preserving relative indenting.

    Example:
    ```python
        if True:
            print("Hello World")
    ```

    becomes

    ```python
    if True:
        print("Hello World")
    ```
    """
    lines = text.split("\n")

    # Get min offset
    if len(lines) > 1:
        min_offset = len(lines[0])
        for line in lines:
            offset = len(line) - len(line.lstrip())
            if offset < min_offset:
                min_offset = offset
    else:
        return lines[0]

    # Remove min_offset from each line
    return "\n".join([line[min_offset:] for line in lines])
