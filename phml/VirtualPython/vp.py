from functools import cached_property
from typing import Any
from .ImportObjects import Import, ImportFrom


class VirtualPython:
    """Represents a python string. Extracts the imports along
    with the locals.
    """

    def __init__(self, content: str):
        self.content = content

    @cached_property
    def imports(self) -> list[Import | ImportFrom]:
        import ast

        imports = []
        for node in ast.parse(self.content).body:
            if isinstance(node, ast.ImportFrom):
                imports.append(ImportFrom.from_node(node))
            elif isinstance(node, ast.Import):
                imports.append(Import.from_node(node))

        return imports

    @cached_property
    def locals(self) -> dict[str, Any]:
        local_env = {}
        exec(self.content, globals(), local_env)
        return local_env


def get_vp_result(expr: str, **kwargs) -> Any:
    """Execute the given python expression, while using
    the kwargs as the local variables.

    This will collect the result of the expression and return it.
    """
    if len(expr.split("\n")) > 1:
        exec(expr, {}, kwargs)
        return kwargs["result"] or kwargs["results"]
    else:
        exec(f"phml_vp_result = {expr}", {}, kwargs)
        return kwargs["phml_vp_result"]


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
                expression=joiner.join(lines)
            else:
                expression=expr[0]
    return expressions

def process_vp_blocks(line: str, vp: VirtualPython, **kwargs) -> str:
    """Process a lines python blocks. Use the VirtualPython locals,
    and kwargs as local variables for each python block. Import
    VirtualPython imports in this methods scope.

    Args:
        line (str): The line to process
        vp (VirtualPython): The virtual python code to use.

    Returns:
        str: The processed line as str.
    """
    from re import sub
    
    # Bring vp imports into scope
    for imp in vp.imports:
        exec(str(imp))
    
    expr = extract_expressions(line)
    if expr is not None:
        for e in expr:
            result = get_vp_result(e, **vp.locals, **kwargs)
            line = sub(
                r"\{.*\}", result, line
            )
    
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
