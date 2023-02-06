"""phml.virtual_python

Data strucutures to store the compiled locals and imports from
python source code.
"""
from __future__ import annotations

import ast
from html import escape
from re import sub, findall
from typing import Any, Optional

from phml.utilities import normalize_indent

from .built_in import built_in_funcs, built_in_types
from .import_objects import Import, ImportFrom

__all__ = ["VirtualPython", "get_python_result", "process_python_blocks"]


class VirtualPython:
    """Represents a python string. Extracts the imports along
    with the locals.
    """

    def __init__(
        self,
        content: Optional[str] = None,
        imports: Optional[list] = None,
        context: Optional[dict] = None,
        *,
        file_name: Optional[str] = None,
    ):
        self.content = content or ""
        self.imports = imports or []
        self.context = context or {}
        self.file_name = file_name or ""

        if self.content != "":

            self.content = normalize_indent(content)

            # Extract imports from content
            for node in ast.parse(self.content).body:
                if isinstance(node, ast.ImportFrom):
                    self.imports.append(ImportFrom.from_node(node))
                elif isinstance(node, ast.Import):
                    self.imports.append(Import.from_node(node))

            # Extract context from python source with additional context
            self.context = self.get_python_context(self.content)

    def get_python_context(self, source: str) -> dict[str, Any]:
        """Get the locals built from the python source code string.
        Splits the def's and classes into their own chunks and passes in
        all other local context to allow for outer scope to be seen in inner scope.
        """

        chunks = [[]]
        lines = source.split("\n")
        i = 0

        # Split the python source code into chunks
        # This is a way of exposing outer most scope to functions and classes
        while i < len(lines):
            if lines[i].startswith(("def","class")):
                chunks.append([lines[i]])
                i+=1
                while i < len(lines) and lines[i].startswith((" ", "\t")):
                    chunks[-1].append(lines[i])
                    i+=1
                chunks.append([])
                continue

            chunks[-1].append(lines[i])
            i+=1

        chunks = [compile("\n".join(chunk), self.file_name, "exec") for chunk in chunks]
        local_env = {}

        # Process each chunk and build locals
        for chunk in chunks:
            exec(chunk, {**local_env}, local_env)

        return local_env


    def __add__(self, obj: VirtualPython) -> VirtualPython:
        local_env = {**self.context}
        local_imports = set(self.imports)
        local_env.update(obj.context)
        for _import in obj.imports:
            local_imports.add(_import)
        return VirtualPython(
            imports=list(local_imports),
            context=local_env,
        )

    def __repr__(self) -> str:
        return f"VP(imports: {len(self.imports)}, locals: {len(self.context.keys())})"


def parse_ast_assign(vals: list[ast.Name | tuple[ast.Name]]) -> list[str]:
    """Parse an ast.Assign node."""

    values = vals[0]
    if isinstance(values, ast.Name):
        return [values.id]

    if isinstance(values, tuple):
        return [name.id for name in values]

    return []


def __validate_kwargs(
    kwargs: dict, expr: str, excludes: Optional[list] = None, safe_vars: bool = False
):
    """Validates the used variables and methods in the expression. If they are
    missing then they are added to the kwargs as None. This means that it will
    give a NoneType error if the method or variable is not provided in the kwargs.

    After validating all variables and methods to be used are in kwargs it then escapes
    all string kwargs for injected html.
    """
    excludes = excludes or []
    exclude_list = [*built_in_funcs, *built_in_types]

    for var in [
        name.id  # Add the non built-in missing variable or method as none to kwargs
        for name in ast.walk(ast.parse(expr))  # Iterate through entire ast of expression
        if isinstance(name, ast.Name)  # Get all variables/names used this can be methods or values
        and name.id not in exclude_list
        and name.id not in excludes
    ]:
        if var not in kwargs:
            kwargs[var] = None

    if not safe_vars:
        escape_args(kwargs)


def get_python_result(expr: str, **kwargs) -> Any:
    """Execute the given python expression, while using
    the kwargs as the global variables.

    This will collect the result of the expression and return it.
    """
    from phml.utilities import (  # pylint: disable=import-outside-toplevel,unused-import
        blank,
        classnames,
    )

    # Data being passed is concidered to be safe and shouldn't be sanatized
    safe_vars = kwargs.pop("safe_vars", None) or False
    
    # Global utilities provided by phml
    kwargs.update({"classnames": classnames, "blank": blank})

    avars = []
    result = "phml_vp_result"
    expression = f"{result} = {expr}\n"

    if "\n" in expr:
        # Find all assigned vars in expression
        avars = []
        assignment = None
        for assign in ast.walk(ast.parse(expr)):
            if isinstance(assign, ast.Assign):
                assignment = parse_ast_assign(assign.targets)
                avars.extend(parse_ast_assign(assign.targets))

        result = assignment[-1]
        expression = f"{expr}\n"

    # validate kwargs and replace missing variables with None
    __validate_kwargs(kwargs, expr, safe_vars=safe_vars)

    try:
        # Compile and execute python source
        source = compile(expression, expr, "exec")

        local_env = {**kwargs}
        global_env = {**kwargs}
        exec(source, global_env, local_env)  # pylint: disable=exec-used
        return local_env[result] if result in local_env else None
    except Exception as exception:  # pylint: disable=broad-except
        from teddecor import TED  # pylint: disable=import-outside-toplevel

        # print_exc()
        TED.print(f"[@F red]*Error[]: [$]{exception}: {expr}")

        return False


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

    index = 0
    while index < len(data):
        start, end, block = extract_block(data[index:])
        if block is None:
            if index < len(data):
                results.append(data[index:])
            break

        if start > 0:
            results.append(data[index : index + start])

        index += end + 1
        results.append(block)

    return results


def extract_block(data: str) -> tuple[int, int, PythonBlock]:
    """Extract the first python block from a given string"""
    start = data.find("{")
    index = start
    if index != -1:
        open_brackets = 1
        while open_brackets > 0:
            new_index = data.find("}", index + 1)
            if len(findall(r"\{", data[index + 1 : new_index])) > 0:
                open_brackets += len(findall(r"\{", data[index + 1 : new_index]))
            index = new_index
            open_brackets -= 1
        end = index
        if "\n" in data[start + 1 : end]:
            return start, end, MultiLineBlock(data[start + 1 : end])
        return start, end, InlineBlock(data[start + 1 : end])
    return 0, 0, None


def process_python_blocks(python_value: str, virtual_python: VirtualPython, **kwargs) -> str:
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

    expressions = extract_expressions(python_value)
    kwargs.update(virtual_python.context)
    for idx, expression in enumerate(expressions):
        if isinstance(expression, PythonBlock):
            expressions[idx] = expression.exec(**kwargs)
            if isinstance(expressions[idx], bool):
                return expressions[idx]

    return "".join([str(expression) for expression in expressions])


class PythonBlock:
    """Base class for python blocks."""

    def __init__(self, expr: str) -> None:
        self.expr = expr

    def __str__(self) -> str:
        return self.expr

    def __repr__(self) -> str:
        return f"{{{self.expr}}}"

    def exec(self, **kwargs):
        """Execute the inline python block"""
        return get_python_result(self.expr, **kwargs)


class InlineBlock(PythonBlock):
    """Formats and stores a inline python expr/source."""

    def __init__(self, expr: str) -> None:
        super().__init__(expr.strip().lstrip("{").rstrip("}"))


class MultiLineBlock(PythonBlock):
    """Formats and stores a multiline python expr/source."""

    def __init__(self, expr: str) -> None:
        from phml.core.formats.parse import (  # pylint: disable=import-outside-toplevel
            strip_blank_lines,
        )

        expr = expr.split("\n")

        # strip brackets
        expr[0] = sub(r"(\s+){", r"\1", expr[0], 1)
        expr[-1] = sub(r"(.+)}", r"\1", expr[-1].rstrip(), 1)

        # strip blank lines
        expr = strip_blank_lines(expr)

        # normalize indent
        super().__init__(normalize_indent("\n".join(expr)))
