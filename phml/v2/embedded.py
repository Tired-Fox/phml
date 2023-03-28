"""
Embedded has all the logic for processing python elements, attributes, and text blocks.
"""
from __future__ import annotations
from html import escape
from functools import cached_property
from shutil import get_terminal_size
import traceback

from typing import Any
from traceback import FrameSummary, extract_tb 
from pathlib import Path
import ast
import re

from .nodes import Element, Literal, LiteralType
from .utils import normalize_indent
from .built_in import built_in_types, built_in_funcs

IMPORTS = {}
FROM_IMPORTS = {}


# PERF: Only allow assignments, methods, imports, and classes?
class EmbeddedTryCatch:
    def __init__(
        self,
        path: str | Path | None = None,
        content: str | None = None,
        pos: tuple[int, int] | None = None,
    ):
        self._path = str(path or "_embedded_")
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
                    exc_tb
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
                parts = [line[j:j+max_width] for j in range(0, len(line), max_width)]
                result.append(self.format_line(parts[0], width, str(i+1)))
                for part in parts[1:]:
                    result.append(self.format_line(part, width))
            else:
                result.append(self.format_line(line, width, str(i+1)))
        return result

    def __str__(self) -> str:
        message = ""
        if self._path != "":
            pos = (self._pos[0] + (self.l_slice[0] or 0), self.c_slice[0] or self._pos[1])
            message = f"[{pos[0]+1}:{pos[1]}] {self._path} Failed to execute phml embedded python"
        if self._content != "":
            lines = self._content.split("\n")
            target_lines = lines[self.l_slice[0]-1:self.l_slice[1]]
            if len(target_lines) > 0:
                if self.l_slice[0] == self.l_slice[1]:
                    target_lines[0] = (
                        target_lines[0][:self.c_slice[0]]
                        + "\x1b[31m"
                        + target_lines[0][self.c_slice[0]:self.c_slice[1]]
                        + "\x1b[0m"
                        + target_lines[0][self.c_slice[1]:]
                    )
                else:
                    target_lines[0] = target_lines[0][:self.c_slice[0]+1] + "\x1b[31m" + target_lines[0][self.c_slice[0]+1:] + "\x1b[0m"
                    for i, line in enumerate(target_lines[1:-1]):
                        target_lines[i+1] = "\x1b[31m" + line + "\x1b[0m"
                    target_lines[-1] = "\x1b[31m" + target_lines[-1][:self.c_slice[-1]+1] + "\x1b[0m" + target_lines[-1][self.c_slice[-1]+1:]
                
                lines = [
                    *lines[:self.l_slice[0]-1],
                    *target_lines,
                    *lines[self.l_slice[1]:]
                ]

            w_fmt = len(f"{len(lines)}")
            content = "\n".join(
                self.generate_exception_lines(lines, w_fmt)
            )
            line_width = self.max_width-w_fmt-2

            exception = f"{self.msg} at <{self.l_slice[0]}:{self.c_slice[0]}-{self.l_slice[1]}:{self.c_slice[1]}>"
            ls = [exception[i:i+line_width] for i in range(0, len(exception), line_width)]
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


def parse_import_values(_import: str) -> list[str]:
    values = []
    for value in re.finditer(r"(?:([^,\s]+) as (.+)|([^,\s]+))(?=\s*,)?", _import):
        if value.group(1) is not None:
            values.append(value.group(1))
        elif value.groups(3) is not None:
            values.append(value.group(3))
    return values


class Import:
    """Data representation of an import."""

    package: str | None
    """Package where the import(s) are from."""

    values: list[str]
    """The imported objects."""

    def __init__(self, _import: str, data: dict[str, str | Any]):
        self._import = _import.strip()

        values: str | None = data["values"]
        value: str | None = data["value"]
        self.package = data["key"]

        if self.package is not None:
            if values is None:
                raise ValueError(
                    "Invalid from <module> import <...objects> syntax. Expected objects"
                )
            self.values = parse_import_values(values)
        else:
            if value is None:
                raise ValueError("Invalid import <object> syntax. Expected object")
            self.values = [value]

    @cached_property
    def data(self) -> dict[str, Any]:
        """The actual imports stored by a name to value mapping."""
        values = list(filter(lambda v: v not in IMPORTS, self.values))
        if len(values) > 0:
            local_env = {}
            exec_val = compile(self._import, "_embedded_import_", "exec")
            exec(exec_val, {}, local_env)
            if self.package is not None:
                if self.package not in FROM_IMPORTS:
                    FROM_IMPORTS[self.package] = {}
                FROM_IMPORTS[self.package].update(local_env)
        if self.package is not None:
            return {key: FROM_IMPORTS[self.package][key] for key in self.values}
        return {key: IMPORTS[key] for key in self.values}

    def __getitem__(self, key: str) -> Any:
        self.data[key]


class Embedded:
    """Logic for parsing and storing locals and imports of dynamic python code."""

    context: dict[str, Any]
    """Variables and locals found in the python code block."""

    imports: list[Import]
    """Imports needed for the python in this scope. Imports are stored in the module globally
    to reduce duplicate imports.
    """

    def __init__(self, content: str | Element, path: str | None = None) -> None:
        self._path = path or "_embedded_"
        self._pos = (0, 0)
        if isinstance(content, Element):
            if (
                len(content) > 1
                or not isinstance(content[0], Literal)
                or content[0].name != LiteralType.Text
            ):
                # TODO: Custom error
                raise ValueError(
                    "Expected python elements to contain one text node or nothing"
                )
            if content.position is not None:
                start = content.position.start
                self._pos = (start.line, start.column) 
            content = content[0].content
        content = normalize_indent(content.strip())
        self.imports = []
        self.context = {}
        if len(content) > 0:
            with EmbeddedTryCatch(path, content, self._pos):
                self.parse_data(content)

    def __add__(self, _o) -> Embedded:
        self.imports.extend(_o.imports)
        self.context.update(_o.context)
        return self

    def __getitem__(self, key: str) -> Any:
        if key in self.context:
            return self.context[key]
        elif key in self.imports:
            return IMPORTS[key]

        raise KeyError(f"Key is not in Embedded context or imports: {key}")

    def split_contexts(self, content: str) -> tuple[list[str], list[Import]]:
        re_context = re.compile(r"class.+|def.+")
        re_import = re.compile(
            r"from (?P<key>.+) import (?P<values>.+)|import (?P<value>.+)"
        )

        imports = []
        blocks = []
        current = []

        lines = content.split("\n")
        i = 0
        while i < len(lines):
            imp_match = re_import.match(lines[i])
            if imp_match is not None:
                imports.append(Import(lines[i], imp_match.groupdict()))
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
        global_env = {
            key: value
            for _import in self.imports
            for key, value in _import.data.items()
        }
        context = {**global_env}

        for block in blocks:
            exec_val = compile(block, self._path, "exec")
            exec(exec_val, global_env, local_env)
            context.update(local_env)
            # update global env with found locals so they can be used inside methods and classes
            global_env.update(local_env)

        self.context = context


def escape_args(args: dict):
    """Take a dictionary of args and escape the html inside string values.

    Args:
        args (dict): Collection of values to html escape.

    Returns:
        A html escaped collection of arguments.
    """

    for key in args:
        if isinstance(args[key], str):
            args[key] = escape(args[key], quote=False)


def _validate_kwargs(code: str, kwargs: dict[str, Any], esc_vars: bool = True):
    exclude_list = [*built_in_funcs, *built_in_types]
    for var in (
        name.id
        for name in ast.walk(
            ast.parse(code, "_phml_get_used_vars_")
        )  # Iterate through entire ast of expression
        if isinstance(
            name, ast.Name
        )  # Get all variables/names used this can be methods or values
        and name.id not in exclude_list
    ):
        if var not in kwargs:
            kwargs[var] = None

    if esc_vars:
        escape_args(kwargs)


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
    # last line must be an assignment or the value to be used
    with EmbeddedTryCatch(_path, code):
        code = normalize_indent(code)
        lines = code.split("\n")
        lines[-1] = "_phml_result_ = " + lines[-1].lstrip()
        code = "\n".join(lines)

        _validate_kwargs(code, context)
        exec_val = compile(code, _path or "_embedded_", "exec")
        exec(exec_val, {}, context)
        return context.get("_phml_result_", None)
