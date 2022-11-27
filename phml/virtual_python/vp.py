from __future__ import annotations

from typing import Any, Optional
from .ImportObjects import Import, ImportFrom
from ast import walk, parse, Name, Assign


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
            import ast

            self.__normalize_indent()

            # Extract imports from content
            for node in ast.parse(self.content).body:
                if isinstance(node, ast.ImportFrom):
                    self.imports.append(ImportFrom.from_node(node))
                elif isinstance(node, ast.Import):
                    self.imports.append(Import.from_node(node))

            # Retreive locals from content
            exec(self.content, globals(), self.locals)

    def __normalize_indent(self):
        self.content = self.content.split("\n")
        offset = len(self.content[0]) - len(self.content[0].lstrip())
        lines = [line[offset:] for line in self.content]
        joiner = "\n"
        self.content = joiner.join(lines)

    def __add__(self, obj: VirtualPython) -> VirtualPython:
        return VirtualPython(
            imports=[*self.imports, *obj.imports],
            local_env={**self.locals, **obj.locals},
        )

    def __repr__(self) -> str:
        return f"VP(imports: {len(self.imports)}, locals: {len(self.locals.keys())})"


def parse_ast_assign(vals: list[Name | tuple[Name]]) -> list[str]:
    values = vals[0]
    if isinstance(values, Name):
        return [values.id]
    elif isinstance(values, tuple):
        return [name.id for name in values]


def get_vp_result(expr: str, **kwargs) -> Any:
    """Execute the given python expression, while using
    the kwargs as the local variables.

    This will collect the result of the expression and return it.
    """
    # Find all assigned vars in expression
    avars = []
    for assign in walk(parse(expr)):
        if isinstance(assign, Assign):
            avars.extend(parse_ast_assign(assign.targets))

    # Find all variables being used that are not are not assigned
    used_vars = [
        name.id for name in walk(parse(expr)) if isinstance(name, Name) and name.id not in avars
    ]

    # For all variables used if they are not in kwargs then they == None
    for uv in used_vars:
        if uv not in kwargs:
            kwargs[uv] = None

    if len(expr.split("\n")) > 1:
        exec(expr, {}, kwargs)
        return kwargs["result"] or kwargs["results"]
    else:
        try:
            exec(f"phml_vp_result = {expr}", {}, kwargs)
            return kwargs["phml_vp_result"]
        except NameError as e:
            print(e, expr, kwargs)


def extract_expressions(data: str) -> str:
    """Extract a phml python expr from a string.
    This method also handles multiline strings,
    strings with `\\n`

    Note:
        phml python blocks/expressions are indicated
        with curly brackets, {}.
    """
    from re import findall

    expressions = findall(r"\{(.*)\}", data)
    if expressions is not None:
        for expression in expressions:
            expression = expression.lstrip("{").rstrip("}")
            expr = expression.split("\n")
            if len(expr) > 1:
                offset = len(expr[0]) - len(expr[0].lstrip())
                lines = [line[offset:] for line in expr]
                joiner = "\n"
                expression = joiner.join(lines)
            else:
                expression = expr[0]
    return expressions


def process_vp_blocks(line: str, vp: VirtualPython, **kwargs) -> str:
    """Process a lines python blocks. Use the VirtualPython locals,
    and kwargs as local variables for each python block. Import
    VirtualPython imports in this methods scope.

    Args:
        line (str): The line to process
        **kwargs (Any): The extra data to pass to the exec function

    Returns:
        str: The processed line as str.
    """
    from re import sub

    # Bring vp imports into scope
    for imp in vp.imports:
        exec(str(imp))

    expr = extract_expressions(line)
    kwargs.update(vp.locals)
    if expr is not None:
        for e in expr:
            result = get_vp_result(e, **kwargs)
            if isinstance(result, bool):
                line = result  # sub(r"\{.*\}", "yes" if result else "no", line)
            else:
                line = sub(r"\{.*\}", str(result), line)

    return line


if __name__ == "__main__":
    # Extra data to similuate extra info a user may pass
    date = "11/14/2022"

    with open("sample_python.txt", "r") as sample_python:
        # Extract python and process as vp
        vp = VirtualPython(sample_python.read())

    # Read source file and export to output file
    with open("sample.phml", "r", encoding="utf-8") as source_file:
        with open("output.html", "+w", encoding="utf-8") as out_file:
            # If line has a inline python block process it
            for line in source_file.readlines():
                out_file.write(process_vp_blocks(line, vp, date=date))
