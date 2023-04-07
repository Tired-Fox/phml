"""
Embedded has all the logic for processing python elements, attributes, and text blocks.
"""
from __future__ import annotations

import ast
from functools import cached_property
from html import escape
import re
import types
from pathlib import Path
from shutil import get_terminal_size
from traceback import FrameSummary, extract_tb
from typing import Any, Iterator, TypedDict

from phml.embedded.built_in import built_in_funcs, built_in_types
from phml.helpers import normalize_indent
from phml.nodes import Element, Literal

ESCAPE_OPTIONS = {
    "quote": False,
}

# Global cached imports
__IMPORTS__ = {}
__FROM_IMPORTS__ = {}


# PERF: Only allow assignments, methods, imports, and classes?
class EmbeddedTryCatch:
    """Context manager around embedded python execution. Will parse the traceback
    and the content being executed to create a detailed error message. The final
    error message is raised in a custom EmbeddedPythonException.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        content: str | None = None,
        pos: tuple[int, int] | None = None,
    ) -> None:
        self._path = str(path or "<python>")
        self._content = content or ""
        self._pos = pos or (0, 0)

    def __enter__(self):
        pass

    def __exit__(self, _, exc_val, exc_tb):
        if exc_val is not None and not isinstance(exc_val, SystemExit):
            raise EmbeddedPythonException(
                self._path,
                self._content,
                self._pos,
                exc_val,
                exc_tb,
            ) from exc_val


class EmbeddedPythonException(Exception):
    def __init__(self, path, content, pos, exc_val, exc_tb) -> None:
        self.max_width, _ = get_terminal_size((20, 0))
        self.msg = exc_val.msg if hasattr(exc_val, "msg") else str(exc_val)
        if isinstance(exc_val, SyntaxError):
            self.l_slice = (exc_val.lineno or 0, exc_val.end_lineno or 0)
            self.c_slice = (exc_val.offset or 0, exc_val.end_offset or 0)
        else:
            fs: FrameSummary = extract_tb(exc_tb)[-1]
            self.l_slice = (fs.lineno or 0, fs.end_lineno or 0)
            self.c_slice = (fs.colno or 0, fs.end_colno or 0)

        self._content = content
        self._path = path
        self._pos = pos

    def format_line(self, line, c_width, leading: str = " "):
        return f"{leading.ljust(c_width, ' ')}│{line}"

    def generate_exception_lines(self, lines: list[str], width: int):
        max_width = self.max_width - width - 3
        result = []
        for i, line in enumerate(lines):
            if len(line) > max_width:
                parts = [
                    line[j : j + max_width] for j in range(0, len(line), max_width)
                ]
                result.append(self.format_line(parts[0], width, str(i + 1)))
                for part in parts[1:]:
                    result.append(self.format_line(part, width))
            else:
                result.append(self.format_line(line, width, str(i + 1)))
        return result

    def __str__(self) -> str:
        message = ""
        if self._path != "":
            pos = (
                self._pos[0] + (self.l_slice[0] or 0),
                self.c_slice[0] or self._pos[1],
            )
            if pos[0] > self._content.count("\n"):
                message = f"{self._path} Failed to execute phml embedded python"
            else:
                message = f"[{pos[0]+1}:{pos[1]}] {self._path} Failed to execute phml embedded python"
        if self._content != "":
            lines = self._content.split("\n")
            target_lines = lines[self.l_slice[0] - 1 : self.l_slice[1]]
            if len(target_lines) > 0:
                if self.l_slice[0] == self.l_slice[1]:
                    target_lines[0] = (
                        target_lines[0][: self.c_slice[0]]
                        + "\x1b[31m"
                        + target_lines[0][self.c_slice[0] : self.c_slice[1]]
                        + "\x1b[0m"
                        + target_lines[0][self.c_slice[1] :]
                    )
                else:
                    target_lines[0] = (
                        target_lines[0][: self.c_slice[0] + 1]
                        + "\x1b[31m"
                        + target_lines[0][self.c_slice[0] + 1 :]
                        + "\x1b[0m"
                    )
                    for i, line in enumerate(target_lines[1:-1]):
                        target_lines[i + 1] = "\x1b[31m" + line + "\x1b[0m"
                    target_lines[-1] = (
                        "\x1b[31m"
                        + target_lines[-1][: self.c_slice[-1] + 1]
                        + "\x1b[0m"
                        + target_lines[-1][self.c_slice[-1] + 1 :]
                    )

                lines = [
                    *lines[: self.l_slice[0] - 1],
                    *target_lines,
                    *lines[self.l_slice[1] :],
                ]

            w_fmt = len(f"{len(lines)}")
            content = "\n".join(
                self.generate_exception_lines(lines, w_fmt),
            )
            line_width = self.max_width - w_fmt - 2

            exception = f"{self.msg}"
            if len(target_lines) > 0:
                exception += f" at <{self.l_slice[0]}:{self.c_slice[0]}-{self.l_slice[1]}:{self.c_slice[1]}>"
            ls = [
                exception[i : i + line_width]
                for i in range(0, len(exception), line_width)
            ]
            exception_line = self.format_line(ls[0], w_fmt, "#")
            for l in ls[1:]:
                exception_line += "\n" + self.format_line(l, w_fmt)

            message += (
                f"\n{'─'.ljust(w_fmt, '─')}┬─{'─'*(line_width)}\n"
                + exception_line
                + "\n"
                + f"{'═'.ljust(w_fmt, '═')}╪═{'═'*(line_width)}\n"
                + f"{content}"
            )

        return message


def parse_import_values(_import: str) -> list[str | tuple[str, str]]:
    values = []
    for value in re.finditer(r"(?:([^,\s]+) as (.+)|([^,\s]+))(?=\s*,)?", _import):
        if value.group(1) is not None:
            values.append((value.group(1), value.group(2)))
        elif value.groups(3) is not None:
            values.append(value.group(3))
    return values


class ImportStruct(TypedDict):
    key: str
    values: str | list[str]


class Module:
    """Object used to access the gobal imports. Readonly data."""

    def __init__(self, module: str, *, imports: list[str] | None = None) -> None:
        self.objects = imports or []
        if imports is not None and len(imports) > 0:
            if module not in __FROM_IMPORTS__:
                raise ValueError(f"Unkown module {module!r}")
            try:
                imports = {
                    _import: __FROM_IMPORTS__[module][_import] for _import in imports
                }
            except KeyError as kerr:
                back_frame = kerr.__traceback__.tb_frame.f_back
                back_tb = types.TracebackType(
                    tb_next=None,
                    tb_frame=back_frame,
                    tb_lasti=back_frame.f_lasti,
                    tb_lineno=back_frame.f_lineno,
                )
                FrameSummary("", 2, "")
                raise ValueError(
                    f"{', '.join(kerr.args)!r} {'arg' if len(kerr.args) > 1 else 'is'} not found in cached imported module {module!r}",
                ).with_traceback(back_tb)

            globals().update(imports)
            locals().update(imports)
            self.module = module
        else:
            if module not in __IMPORTS__:
                raise ValueError(f"Unkown module {module!r}")

            imports = {module: __IMPORTS__[module]}
            locals().update(imports)
            globals().update(imports)
            self.module = module

    def collect(self) -> Any:
        """Collect the imports and return the single import or a tuple of multiple imports."""
        if len(self.objects) > 0:
            if len(self.objects) == 1:
                return __FROM_IMPORTS__[self.module][self.objects[0]]
            return tuple(
                [__FROM_IMPORTS__[self.module][object] for object in self.objects]
            )
        return __IMPORTS__[self.module]


class EmbeddedImport:
    """Data representation of an import."""

    module: str
    """Package where the import(s) are from."""

    objects: list[str]
    """The imported objects."""

    def __init__(
        self, module: str, values: str | list[str] | None = None, *, push: bool = False
    ) -> None:
        self.module = module

        if isinstance(values, list):
            self.objects = values
        else:
            self.objects = parse_import_values(values or "")

        if push:
            self.data

    def _parse_from_import(self):
        if self.module in __FROM_IMPORTS__:
            values = list(
                filter(
                    lambda v: (v if isinstance(v, str) else v[0])
                    not in __FROM_IMPORTS__[self.module],
                    self.objects,
                )
            )
        else:
            values = self.objects

        if len(values) > 0:
            local_env = {}
            exec_val = compile(str(self), "_embedded_import_", "exec")
            exec(exec_val, {}, local_env)

            if self.module not in __FROM_IMPORTS__:
                __FROM_IMPORTS__[self.module] = {}
            __FROM_IMPORTS__[self.module].update(local_env)

        keys = [key if isinstance(key, str) else key[1] for key in self.objects]
        return {key: __FROM_IMPORTS__[self.module][key] for key in keys}

    def _parse_import(self):
        if self.module not in __IMPORTS__:
            local_env = {}
            exec_val = compile(str(self), "_embedded_import_", "exec")
            exec(exec_val, {}, local_env)
            __IMPORTS__.update(local_env)

        return {self.module: __IMPORTS__[self.module]}

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        if len(self.objects) > 0:
            if self.module not in __FROM_IMPORTS__:
                raise KeyError(f"{self.module} is not a known exposed module")
            yield from __FROM_IMPORTS__[self.module].items()
        else:
            if self.module not in __IMPORTS__:
                raise KeyError(f"{self.module} is not a known exposed module")
            yield __IMPORTS__[self.module]

    @cached_property
    def data(self) -> dict[str, Any]:
        """The actual imports stored by a name to value mapping."""
        if len(self.objects) > 0:
            return self._parse_from_import()
        return self._parse_import()

    def __getitem__(self, key: str) -> Any:
        self.data[key]

    def __repr__(self) -> str:
        if len(self.objects) > 0:
            return f"FROM({self.module}).IMPORT({', '.join(self.objects)})"
        return f"IMPORT({self.module})"

    def __str__(self) -> str:
        if len(self.objects) > 0:
            return f"from {self.module} import {', '.join(obj if isinstance(obj, str) else f'{obj[0]} as {obj[1]}' for obj in self.objects)}"
        return f"import {self.module}"


class Embedded:
    """Logic for parsing and storing locals and imports of dynamic python code."""

    context: dict[str, Any]
    """Variables and locals found in the python code block."""

    imports: list[EmbeddedImport]
    """Imports needed for the python in this scope. Imports are stored in the module globally
    to reduce duplicate imports.
    """

    def __init__(self, content: str | Element, path: str | None = None) -> None:
        self._path = path or "<python>"
        self._pos = (0, 0)
        if isinstance(content, Element):
            if len(content) > 1 or (
                len(content) == 1 and not Literal.is_text(content[0])
            ):
                # TODO: Custom error
                raise ValueError(
                    "Expected python elements to contain one text node or nothing",
                )
            if content.position is not None:
                start = content.position.start
                self._pos = (start.line, start.column)
            content = content[0].content
        content = normalize_indent(content)
        self.imports = []
        self.context = {}
        if len(content) > 0:
            with EmbeddedTryCatch(path, content, self._pos):
                self.parse_data(content)

    def __add__(self, _o) -> Embedded:
        self.imports.extend(_o.imports)
        self.context.update(_o.context)
        return self

    def __contains__(self, key: str) -> bool:
        return key in self.context

    def __getitem__(self, key: str) -> Any:
        if key in self.context:
            return self.context[key]
        elif key in self.imports:
            return __IMPORTS__[key]

        raise KeyError(f"Key is not in Embedded context or imports: {key}")

    def split_contexts(self, content: str) -> tuple[list[str], list[EmbeddedImport]]:
        re_context = re.compile(r"class.+|def.+")
        re_import = re.compile(
            r"from (?P<key>.+) import (?P<values>.+)|import (?P<value>.+)",
        )

        imports = []
        blocks = []
        current = []

        lines = content.split("\n")
        i = 0
        while i < len(lines):
            imp_match = re_import.match(lines[i])
            if imp_match is not None:
                data = imp_match.groupdict()
                imports.append(
                    EmbeddedImport(data["key"] or data["value"], data["values"])
                )
            elif re_context.match(lines[i]) is not None:
                blocks.append("\n".join(current))
                current = [lines[i]]
                i += 1
                while i < len(lines) and lines[i].startswith(" "):
                    current.append(lines[i])
                    i += 1
                blocks.append("\n".join(current))
                current = []
            else:
                current.append(lines[i])
            if i < len(lines):
                i += 1

        if len(current) > 0:
            blocks.append("\n".join(current))

        return blocks, imports

    def parse_data(self, content: str):
        blocks, self.imports = self.split_contexts(content)

        local_env = {}
        global_env = {key: value for _import in self.imports for key, value in _import}
        context = {**global_env}

        for block in blocks:
            exec_val = compile(block, self._path, "exec")
            exec(exec_val, global_env, local_env)
            context.update(local_env)
            # update global env with found locals so they can be used inside methods and classes
            global_env.update(local_env)

        self.context = context


def _validate_kwargs(code: ast.Module, kwargs: dict[str, Any]):
    exclude_list = [*built_in_funcs, *built_in_types]
    for var in (
        name.id
        for name in ast.walk(code)
        if isinstance(
            name,
            ast.Name,
        )  # Get all variables/names used. This can be methods or values
        and name.id not in exclude_list
    ):
        if var not in kwargs:
            kwargs[var] = None


def update_ast_node_pos(dest, source):
    """Assign lineno, end_lineno, col_offset, and end_col_offset
    from a source python ast node to a destination python ast node.
    """
    dest.lineno = source.lineno
    dest.end_lineno = source.end_lineno
    dest.col_offset = source.col_offset
    dest.end_col_offset = source.end_col_offset


RESULT = "_phml_embedded_result_"


def exec_embedded(code: str, _path: str | None = None, **context: Any) -> Any:
    """Execute embedded python and return the extracted value. This is the last
    assignment in the embedded python. The embedded python must have the last line as a value
    or an assignment.

    Note:
        No local or global variables will be retained from the embedded python code.

    Args:
        code (str): The embedded python code.
        **context (Any): The additional context to provide to the embedded python.

    Returns:
        Any: The value of the last assignment or value defined
    """
    from phml.utilities import blank

    context = {
        "blank": blank,
        **context,
    }

    # last line must be an assignment or the value to be used
    with EmbeddedTryCatch(_path, code):
        code = normalize_indent(code)
        AST = ast.parse(code)
        _validate_kwargs(AST, context)

        last = AST.body[-1]
        returns = [ret for ret in AST.body if isinstance(ret, ast.Return)]

        if len(returns) > 0:
            last = returns[0]
            idx = AST.body.index(last)

            n_expr = ast.Name(id=RESULT, ctx=ast.Store())
            n_assign = ast.Assign(targets=[n_expr], value=last.value)

            update_ast_node_pos(dest=n_expr, source=last)
            update_ast_node_pos(dest=n_assign, source=last)

            AST.body = [*AST.body[:idx], n_assign]
        elif isinstance(last, ast.Expr):
            n_expr = ast.Name(id=RESULT, ctx=ast.Store())
            n_assign = ast.Assign(targets=[n_expr], value=last.value)

            update_ast_node_pos(dest=n_expr, source=last)
            update_ast_node_pos(dest=n_assign, source=last)

            AST.body[-1] = n_assign
        elif isinstance(last, ast.Assign):
            n_expr = ast.Name(id=RESULT, ctx=ast.Store())
            update_ast_node_pos(dest=n_expr, source=last)
            last.targets.append(n_expr)

        ccode = compile(AST, "_phml_embedded_", "exec")
        local_env = {}
        exec(ccode, {**context}, local_env)

        if isinstance(local_env[RESULT], str):
            return escape(local_env[RESULT], **ESCAPE_OPTIONS)
        return local_env[RESULT]


def exec_embedded_blocks(code: str, _path: str = "", **context: dict[str, Any]):
    """Execute embedded python inside `{{}}` blocks. The resulting values are subsituted
    in for the found blocks.

    Note:
        No local or global variables will be retained from the embedded python code.

    Args:
        code (str): The embedded python code.
        **context (Any): The additional context to provide to the embedded python.

    Returns:
        str: The value of the passed in string with the python blocks replaced.
    """

    result = [""]
    data = []
    next_block = re.search(r"\{\{", code)
    while next_block is not None:
        start = next_block.start()
        if start > 0:
            result[-1] += code[:start]
        code = code[start + 2 :]

        balance = 2
        index = 0
        while balance > 0 and index < len(code):
            if code[index] == "}":
                balance -= 1
            elif code[index] == "{":
                balance += 1
            index += 1

        result.append("")
        data.append(
            str(
                exec_embedded(
                    code[: index - 2].strip(),
                    _path + f" block #{len(data)+1}",
                    **context,
                ),
            ),
        )
        code = code[index:]
        next_block = re.search(r"(?<!\\)\{\{", code)

    if len(code) > 0:
        result[-1] += code

    if len(data) != len(result) - 1:
        raise ValueError(
            f"Not enough data to replace inline python blocks: expected {len(result) - 1} but there was {len(data)}"
        )

    def merge(dest: list, source: list) -> list:
        """Merge source into dest. For every item in source place each item between items of dest.
        If there is more items in source the spaces between items in dest then the extra items in source
        are ignored.

        Example:
            dest = [1, 2, 3]
            source = ["red", "blue", "green"]
            merge(dest, source) == [1, "red", 2, "blue", 3]

            or

            dest = [1, 2, 3]
            source = ["red"]
            merge(dest, source) == [1, "red", 2, 3]
        """
        combination = []
        for f_item, s_item in zip(dest, source):
            combination.extend([f_item, s_item])

        idx = len(combination) // 2
        if idx < len(dest):
            combination.extend(dest[idx:])
        return combination

    return "".join(merge(result, data))
