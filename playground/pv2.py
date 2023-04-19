from __future__ import annotations
from typing import Iterator
from re import finditer, split
from phml.nodes import (
    AST,
    Attribute,
    Element,
    Literal,
    LiteralType,
    Parent,
    Position,
    inspect,
)


class ParseError(Exception):
    __module__ = Exception.__module__


WHITESPACE = [" ", "\n", "\t", "\r", "\f"]


class Location:
    __slots__ = ("line", "column", "index")

    def __init__(self, line: int = 1, col: int = 0, idx: int = 0):
        self.column: int = col
        self.line: int = line
        self.index: int = idx

    def copy(self) -> Location:
        return Location(self.line, self.column, self.index)

    def __iter__(self) -> Iterator[int]:
        yield self.line
        yield self.column

    def __str__(self) -> str:
        return self.display()

    def display(self) -> str:
        return f"{self.line}:{self.column}"


class Parser:
    __slot__ = ("loc", "content", "ast", "current", "tag_stack")

    def __init__(self):
        self.ast = AST()
        self.loc = Location()
        self.quotes = {"'": 0, '"': 0, "`": 0}
        self._reset_()

    def _reset_(self):
        self.loc.line = 0
        self.loc.column = 0
        self.loc.index = 0

        self.ast.children = []

        self.content = ""
        self.tag_stack: list[str] = []

        self.current: Parent = self.ast

    def _element_(self, capture: str) -> int:
        idx = 1

        escaped = None
        while idx < len(capture):
            if capture[idx] == "'":
                if escaped == "'":
                    escaped = None
                elif escaped is None:
                    escaped = "'"
            elif capture[idx] == '"':
                if escaped == '"':
                    escaped = None
                elif escaped is None:
                    escaped = '"'
            elif capture[idx] == "<" and escaped is None:
                return idx
            idx += 1
        return idx

    def _column_(self, data: str):
        if data.count("\n") > 0:
            return len(data.rsplit("\n", 1)[-1])
        return max(0, len(data) - 1)

    def _update_loc_(self, capture: str):
        """Update the line and column number given a string capture."""
        self.loc.line += capture.count("\n")
        if capture.count("\n") > 0:
            self.loc.column = len(capture.rsplit("\n", 1)[-1])
        else:
            self.loc.column += max(0, len(capture) - 1)

    def _capture_and_update_(self, start: int | None = None, end: int | None = None):
        """Capture a part of the code and increment index, line, and column.

        Returns:
            str: Capture slice of code.
        """
        start = start or self.loc.index
        end = end or len(self.content)

        capture = self.content[start:end]
        self.loc.index += len(capture)
        self._update_loc_(capture)
        return capture

    def _find_(self, content: str, *patterns: str) -> tuple[int, str] | None:
        self.quotes["'"] = 0
        self.quotes['"'] = 0
        self.quotes["`"] = 0

        firsts = [pattern[0] for pattern in patterns]

        i = 0
        while i < len(content):
            if content[i] in firsts:
                idx = firsts.index(content[i])
                if content[i : i + len(patterns[idx])] == patterns[idx]:
                    return i, patterns[idx]
            elif content[i] in self.quotes:
                self.quotes[content[i]] += 1
            i += 1

        return None

    def _peek_(self) -> int:
        """Find the next token.

        Returns:
            int: The index of the next token or -1 if no other token found. Meaning rest is plain text.
        """
        if len(self.tag_stack) > 0 and self.tag_stack[-1] in [
            "python",
            "script",
            "style",
        ]:
            index = int(self.loc.index)

            while (
                opening := self._find_(self.content[index:], "<", "-->")
            ) is not None:
                if opening[1] == "-->":
                    return opening[0]
                capture = self.content[index : index + opening[0]]

                # Validates if current in a string block
                for char in capture:
                    if char in self.quotes:
                        self.quotes[char] += 1

                if all(i % 2 == 0 for i in self.quotes.values()):
                    length = 2 + len(self.tag_stack[-1])
                    content = self.content[
                        (index + opening[0]) : (
                            index + opening[0] + length 
                        )
                    ]
                    if (
                        len(content) >= length
                        and content[:length]
                        == f"</{self.tag_stack[-1]}"
                    ):
                        return index + opening[0]
                    index += opening[0] + len(content)
                else:
                    index += opening[0]
        else:
            next_t = self._find_(self.content[self.loc.index :], "<", "-->")
            if next_t is not None:
                return self.loc.index + next_t[0]
        return -1

    def _next_(self) -> str:
        """Get the next token."""

        if self.content[self.loc.index] == "<":
            if self.content[self.loc.index + 1 : self.loc.index + 4] == "!--":
                return self._capture_and_update_(self.loc.index + 1, self.loc.index + 4)
            else:
                idx = self.content[self.loc.index :].find(">")

                if idx >= 0:
                    end = self._element_(
                        self.content[self.loc.index : self.loc.index + idx]
                    )

                    return self._capture_and_update_(end=self.loc.index + end + 1)
                return self._capture_and_update_()
        elif (
            self.content[self.loc.index] == "-"
            and self.content[self.loc.index : self.loc.index + 3] == "-->"
        ):
            return self._capture_and_update_(end=self.loc.index + 3)
        else:
            idx = self._peek_()

            if idx == -1:
                capture = self._capture_and_update_()
                return capture

            if (
                self.content[idx : idx + 4] == "<!--"
                or self.content[idx : idx + 3] == "-->"
            ):
                self._capture_and_update_(end=idx)

            for closing in finditer(">", self.content[idx:]):
                end = closing.start()
                if self._element_(self.content[idx + 1 : idx + end + 1]) is not None:
                    return self._capture_and_update_(end=idx)

            return self._capture_and_update_()

    def _parse_attributes_(self, attrs: str) -> dict[str, Attribute]:
        idx = 0
        attributes = {}
        apos = self.loc.copy()

        current = None
        while idx < len(attrs):
            if attrs[idx] in ["'", '"']:
                raise ParseError(
                    f"<{apos}> : Invalid character in attribute name {attrs[idx]!r}"
                )
            if attrs[idx] == "=":
                if current is None:
                    raise ParseError(f"<{apos}> : Cannot start attribute name with '='")

                pattern = None
                if attrs[idx + 1] == '"':
                    pattern = '"'
                elif attrs[idx + 1] == "'":
                    pattern = "'"

                idx += 2
                value = ""
                while (
                    idx < len(attrs) and (attrs[idx] != pattern
                    if pattern is not None
                    else attrs[idx] not in WHITESPACE)
                ):
                    value += attrs[idx]
                    idx += 1

                if pattern != attrs[idx]:
                    raise ParseError(
                        f"<{apos}> : Quoted attribute value was not closed"
                    )

                if value.lower() in ["yes", "true"]:
                    value = True
                elif value.lower() in ["no", "false"]:
                    value = False

                attributes[current["key"]] = value
                current = None
            elif attrs[idx] in WHITESPACE:
                # Whitespace seperator
                if current is not None:
                    attributes[current["key"]] = current["value"]
                    current = None

                if attrs[idx] == "\n":
                    apos.column = 0
                    apos.line += 1
            else:
                if current is None:
                    current = {"key": "", "value": True}
                current["key"] += attrs[idx]
            idx += 1
            apos.column += 1

        if current is not None:
            attributes[current["key"]] = current["value"]

        return attributes

    def _parse_token_(self) -> Literal | Element | None:
        token = self._next_()
        start = self.loc.copy()

        # switch on token
        if token == "<!--":
            content = self._next_()
            if next := self._next_() != "-->":
                raise ParseError(f"<{start}> : Comment was never closed")

            return Literal(
                LiteralType.Comment,
                content.strip(),
                position=Position(tuple(start), tuple(self.loc)),
                in_pre="pre" in self.tag_stack,
            )

        if token.startswith("<") and token.endswith(">"):
            if token[1] == "/":
                tag = token[2:-1].strip().split(" ", 1)[0]
                _tag = self.tag_stack.pop()
                if tag != _tag:
                    raise ParseError(f"<{start}> : Closing a non opened tag {tag!r}")

                if self.current.parent is None:
                    self.current = self.ast
                else:
                    self.current = self.current.parent

                return None
            elif token[1] == "!":
                content = token[2:-1]
                tag = split("\\s", content, 1)[0]
                content = content[len(tag) :].strip()
                attributes = self._parse_attributes_(content)
                return Element(
                    tag,
                    attributes,
                    in_pre="pre" in self.tag_stack or tag == "pre",
                    decl=True,
                )
            else:
                if token[-2] == "/":
                    content = token[1:-2]
                    children = None
                else:
                    content = token[1:-1]
                    children = []

                tag = split("\\s", content, 1)[0]
                content = content[len(tag) :].strip()
                attributes = self._parse_attributes_(content)
                return Element(
                    tag,
                    attributes,
                    children if not self._is_self_closing_(tag) else None,
                    in_pre="pre" in self.tag_stack,
                )

        if "pre" not in self.tag_stack and not (
            len(self.tag_stack) > 0
            and self.tag_stack[-1] in ["python", "script", "style"]
        ):
            token = token.strip()

        if token != "":
            return Literal(
                LiteralType.Text,
                token,
                position=Position(tuple(start), tuple(self.loc)),
                in_pre="pre" in self.tag_stack,
            )

    def _is_self_closing_(self, name: str) -> bool:
        """Check if the tag is self closing. Only check if auto_closing is toggled on."""

        return name in [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
            "command",
            "keygen",
            "menuitem",
            "Slot",
            "Markdown",
        ]

    def feed(self, code: str):
        self.content += code
        while self.loc.index < len(self.content):
            node = self._parse_token_()
            if isinstance(node, Element):
                # Self closing or not
                if node.children is None:
                    self.current.append(node)
                else:
                    self.tag_stack.append(node.tag)
                    self.current.append(node)
                    self.current = node
            elif isinstance(node, Literal):
                self.current.append(node)

    def parse(self, code: str) -> AST:
        self._reset_()
        self.feed(code)
        return self.ast


if __name__ == "__main__":
    from phml import HypertextManager
    from phml.parser import HypertextMarkupParser
    from time import time_ns

    phml = HypertextManager()

    code = """\
<!DOCTYPE html>
<sample
    open
    @else
    :type="some_type"
>Some Text</sample>
<meta type="stylesheet">
"""
    n_parser = Parser()
    o_parser = HypertextMarkupParser()

    ast = n_parser.parse(code)
    print(
        inspect(
            ast,
            color=True,
            text=True,
        )
    )
    print(phml.render(_ast=ast))

    with open("../examples/loops/src/unicode.html", "r", encoding="utf-8") as file:
        code = file.read()

    count= 3

    n_times = []
    for i in range(count):
        n_start = time_ns()
        n_ast = n_parser.parse(code)
        n_total = time_ns() - n_start
        n_times.append(n_total)
    n_average = sum(n_times) / count

    o_times = []
    for i in range(count):
        o_start = time_ns()
        o_ast = o_parser.parse(code)
        o_total = time_ns() - o_start
        o_times.append(o_total)
    o_average = sum(o_times) / count

    result = "<" if n_average < o_average else ">"
    print(
        f"Tokenize {result} Regex:\n  {round(n_average * (10**-9), 9)}s {result} {round(o_average * (10**-9), 9)}s"
    )
