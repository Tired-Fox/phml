"""phml.virtual_python

Data strucutures to store the compiled locals and imports from
python source code.
"""
from __future__ import annotations

import ast
from html import escape
from re import finditer, sub
from typing import Any, Optional

from .built_in import built_in_funcs
from .import_objects import Import, ImportFrom

__all__ = ["VirtualPython", "get_vp_result", "process_vp_blocks"]


class VirtualPython:
    """Represents a python string. Extracts the imports along
    with the locals.
    """

    def __init__(
        self,
        content: Optional[str] = None,
        imports: Optional[list] = None,
        local_env: Optional[dict] = None,
    ):
        self.content = content or ""
        self.imports = imports or []
        self.locals = local_env or {}

        if self.content != "":
            self.__normalize_indent()

            # Extract imports from content
            for node in ast.parse(self.content).body:
                if isinstance(node, ast.ImportFrom):
                    self.imports.append(ImportFrom.from_node(node))
                elif isinstance(node, ast.Import):
                    self.imports.append(Import.from_node(node))

            # Retreive locals from content
            exec(self.content, globals(), self.locals)  # pylint: disable=exec-used

    def __normalize_indent(self):
        self.content = self.content.split("\n")
        offset = len(self.content[0]) - len(self.content[0].lstrip())
        lines = [line[offset:] for line in self.content]
        joiner = "\n"
        self.content = joiner.join(lines)

    def __add__(self, obj: VirtualPython) -> VirtualPython:
        local_env = {**self.locals}
        local_env.update(obj.locals)
        return VirtualPython(
            imports=[*self.imports, *obj.imports],
            local_env=local_env,
        )

    def __repr__(self) -> str:
        return f"VP(imports: {len(self.imports)}, locals: {len(self.locals.keys())})"


def parse_ast_assign(vals: list[ast.Name | tuple[ast.Name]]) -> list[str]:
    """Parse an ast.Assign node."""

    values = vals[0]
    if isinstance(values, ast.Name):
        return [values.id]

    if isinstance(values, tuple):
        return [name.id for name in values]

    return []


def get_vp_result(expr: str, **kwargs) -> Any:
    """Execute the given python expression, while using
    the kwargs as the local variables.

    This will collect the result of the expression and return it.
    """
    from phml.utilities import (  # pylint: disable=import-outside-toplevel,unused-import
        ClassList,
        blank,
        classnames,
    )

    safe_vars = kwargs.pop("safe_vars", None) or False
    kwargs.update({"classnames": classnames, "blank": blank})

    if len(expr.split("\n")) > 1:
        # Find all assigned vars in expression
        avars = []
        assignment = None
        for assign in ast.walk(ast.parse(expr)):
            if isinstance(assign, ast.Assign):
                assignment = parse_ast_assign(assign.targets)
                avars.extend(parse_ast_assign(assign.targets))

        # Find all variables being used that are not are not assigned
        used_vars = [
            name.id
            for name in ast.walk(ast.parse(expr))
            if isinstance(name, ast.Name) and name.id not in avars and name.id not in built_in_funcs
        ]

        # For all variables used if they are not in kwargs then they == None
        for var in used_vars:
            if var not in kwargs:
                kwargs[var] = None

        if not safe_vars:
            escape_args(kwargs)

        source = compile(f"{expr}\n", f"{expr}", "exec")
        exec(source, globals(), kwargs)  # pylint: disable=exec-used
        # Get the last assignment and use it as the result
        return kwargs[assignment[-1]]

    # For all variables used if they are not in kwargs then they == None
    for var in [name.id for name in ast.walk(ast.parse(expr)) if isinstance(name, ast.Name)]:
        if var not in kwargs:
            kwargs[var] = None

    if not safe_vars:
        escape_args(kwargs)

    source = compile(f"phml_vp_result = {expr}", expr, "exec")
    exec(source, globals(), kwargs)  # pylint: disable=exec-used
    return kwargs["phml_vp_result"] if "phml_vp_result" in kwargs else None


def escape_args(args: dict) -> dict:
    """Take a dictionary of args and escape the html inside string values.

    Args:
        args (dict): Collection of values to html escape.

    Returns:
        A html escaped collection of arguments.
    """

    for key in args:
        if isinstance(args[key], str):
            args[key] = escape(args[key], quote=False)


def extract_expressions(data: str) -> str:
    """Extract a phml python expr from a string.
    This method also handles multiline strings,
    strings with `\\n`

    Note:
        phml python blocks/expressions are indicated
        with curly brackets, {}.
    """
    results = []

    for expression in finditer(r"\{[^}]+\}", data):
        expression = expression.group().lstrip("{").rstrip("}")
        expression = [expr for expr in expression.split("\n") if expr.strip() != ""]
        if len(expression) > 1:
            offset = len(expression[0]) - len(expression[0].lstrip())
            lines = [line[offset:] for line in expression]
            results.append("\n".join(lines))
        else:
            results.append(expression[0])

    return results


def process_vp_blocks(pvb_value: str, virtual_python: VirtualPython, **kwargs) -> str:
    """Process a lines python blocks. Use the VirtualPython locals,
    and kwargs as local variables for each python block. Import
    VirtualPython imports in this methods scope.

    Args:
        value (str): The line to process.
        virtual_python (VirtualPython): Parsed locals and imports from all python blocks.
        **kwargs (Any): The extra data to pass to the exec function.

    Returns:
        str: The processed line as str.
    """

    # Bring vp imports into scope
    for imp in virtual_python.imports:
        exec(str(imp))  # pylint: disable=exec-used

    expressions = extract_expressions(pvb_value)
    kwargs.update(virtual_python.locals)
    if expressions is not None:
        for expr in expressions:
            result = get_vp_result(expr, **kwargs)
            if isinstance(result, bool):
                pvb_value = result
            else:
                pvb_value = sub(r"\{[^}]+\}", str(result), pvb_value, 1)

    return pvb_value
