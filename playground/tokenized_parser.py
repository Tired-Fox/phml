"""
This is about twice as slow as the current regex parser.
"""
from dataclasses import dataclass
from pathlib import Path
from phml.nodes import *
from phml.parser import HypertextMarkupParser

phml = """
<!DOCTYPE html>
<html>
    <head>
        <meta content="">
        <title>Some title</title>
    </head>
    <body>
        <input
            type="number"
            max="100"
            min="2"
            placeholder="10"
            hidden
        >
    </body>
</html>
"""

self_closing = [
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


class Token:
    content: str
    """Content of the token."""

    start: tuple[int, int]
    """The starting line and column in the phml string."""

    end: tuple[int, int]
    """The ending line and column in the phml string."""

    def __init__(
        self, content: str, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        self.content = content
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"<{self.content!r} {self.start[0]}:{self.start[1]}-{self.end[0]}:{self.end[1]}>"


@dataclass
class States:
    Text: str = "Text"
    Tag: str = "Tag"
    Attribute: str = "Attribute"
    AttributeAlt: str = "Attribute Alt"
    AttrValue: str = "Attribute Aalue"
    DQuote: str = "Aouble Auote Aalue"
    SQuote: str = "Aingle Quote Value"
    Closing: str = "Closing Tag"
    Comment: str = "Comment Tag"
    CommentOpen: str = "Comment Open Tag"
    CommentBody: str = "Comment Body"
    CommentClose: str = "Comment Close Tag"


@dataclass
class Ops:
    NoOp: str = "NO_OPERATION"
    Close: str = "CLOSE_TAG"


# Special keys are `*` and `\\s` for any char and whitespace char respectively
# Order goes, specific char to key, if char is only whitespace then check for `\\s`, then check agains `*`
# Error if key not in current state's mapping

STATES = {
    States.Text: {"*": States.Text, "<": States.Tag},
    States.Tag: {
        "/": States.Closing,
        "\\s": States.Attribute,
        "<": None,
        ">": States.Text,
        "*": States.Tag,
        "!": States.Comment,
    },
    States.Attribute: {
        "*": States.Attribute,
        "=": States.AttrValue,
        ">": States.Text,
        "<": States.Tag,
        "\\s": States.AttributeAlt,
        "/": States.Closing,
    },
    States.AttributeAlt: {
        "*": States.Attribute,
        "=": States.AttrValue,
        ">": States.Text,
        "<": States.Tag,
        "\\s": States.Attribute,
    },
    States.AttrValue: {
        "\\s": States.Attribute,
        "*": States.AttrValue,
        '"': States.DQuote,
        "'": States.SQuote,
        ">": States.Text,
        "<": States.Tag,
    },
    States.DQuote: {"*": States.DQuote, '"': States.Tag},
    States.SQuote: {"*": States.SQuote, "'": States.Tag},
    States.Closing: {"*": States.Closing, ">": States.Text, "<": States.Tag},
    States.Comment: {"-": States.CommentOpen, "*": States.Tag},
    States.CommentOpen: {"-": States.CommentBody, "*": States.Tag},
    States.CommentBody: {"*": States.CommentBody, "-": States.CommentClose},
    States.CommentClose: {"-": States.CommentClose, ">": States.Text},
}


def increment_pos(char: str, pos: list[int]) -> list[int]:
    if char == "\n":
        pos[0] += 1
        pos[1] = 0
    else:
        pos[1] += 1
    return pos


class Parser:
    def __init__(self) -> None:
        self.tag_stack = []

    def tokenize(self, code: str) -> list[Token]:
        t_start = time_ns()
        state = States.Text
        tokens: list[Token] = []

        start = (1, 0)
        end = [1, 0]

        pos = 0
        for i, char in enumerate(code):
            if char in STATES[state]:
                next_state = STATES[state][char]
            elif char.strip() == "" and "\\s" in STATES[state]:
                next_state = STATES[state]["\\s"]
            elif "*" in STATES[state]:
                next_state = STATES[state]["*"]
            else:
                raise Exception(
                    f"Unkown token {char!r} in <{state}>; expected tokens: {', '.join(STATES[state].keys())} <{end[0]}:{end[1]}>"
                )

            if next_state == state:
                end = increment_pos(char, end)
            else:
                if pos - i > 0:
                    tokens.append(Token(code[pos:i+1], start, tuple(end)))
                end = increment_pos(char, end)

                tokens.append(Token(char, tuple(end), tuple(end)))
                start = tuple(end)

                if next_state is not None:
                    state = next_state

        if pos < len(code):
            tokens.append(Token(code[pos:], start, tuple(end)))
        print(round((time_ns() - t_start) * (10**-9), 9))
        return tokens

    def _get_end_of_tag(self, tokens: list[Token], idx: int) -> Token | None:
        escaped = False
        if "".join(token.content for token in tokens[idx : idx + 2]).startswith("!--"):
            while idx < len(tokens):
                if (
                    tokens[idx].content == ">"
                    and "".join(token.content for token in tokens[idx - 3 : idx + 1])
                    == "-->"
                ):
                    return tokens[idx]
                idx += 1
            return None
        else:
            while idx < len(tokens):
                if tokens[idx].content in ["'", '"']:
                    escaped = not escaped
                elif tokens[idx].content == "<" and not escaped:
                    return None
                elif tokens[idx].content == ">" and not escaped:
                    return tokens[idx]
                idx += 1

    def _parses_attr_tokens(self, tokens: list[Token]) -> dict[str, Attribute]:
        attrs: dict[str, Attribute] = {}
        key = None

        i = 0
        while i < len(tokens):
            if tokens[i].content.strip() == "" and key is not None:
                attrs[key] = True
                key = None
            elif key is None and tokens[i].content.strip() != "":
                key = tokens[i].content
            elif tokens[i].content == "=":
                if key is None:
                    raise Exception("Cannot set value to None key")

                if tokens[i + 1] == "'":
                    stop = "'"
                elif tokens[i + 1] == '"':
                    stop = '"'
                else:
                    stop = None

                j = i + 2
                while j < len(tokens):
                    if (stop is None and tokens[j].content.strip() == "") or tokens[
                        j
                    ] == stop:
                        break
                    j += 1

                j -= 1
                value = "".join(token.content for token in tokens[i + 2 : j])
                if value.lower() in ["yes", "true"]:
                    value = True
                elif value.lower() in ["no", "false"]:
                    value = False

                attrs[key] = value
                i = j
                key = None
            i += 1

        if key is not None:
            attrs[key] = True
            key = None

        return attrs

    def _parse_tag_tokens(self, tokens: list[Token]) -> Element | Literal | str:
        # Check for comment
        if (
            len(tokens) >= 4
            and "".join(token.content for token in tokens[:4]) == "<!--"
        ):
            return Literal(
                LiteralType.Comment,
                "".join(token.content for token in tokens[4:-3]),
                position=Position(tokens[0].start, tokens[-1].end),
            )
        else:
            # First token is name or >

            if tokens[1].content.strip() in ["", ">"]:
                name = ""
                if len(tokens[2:]) > 1:
                    raise Exception("Tags with empty names can not have attributes")
                self_close = False
                attrs = {}
            elif tokens[1].content == "/":
                name = "".join([token.content for token in tokens[2:-1]]).strip()
                if self.tag_stack in ["python", "script", "style"] and name not in [
                    "python",
                    "script",
                    "style",
                ]:
                    return Ops.NoOp

                if self.tag_stack[-1] != name:
                    raise Exception(
                        f"Found closing tag '</{name}>' but expected '</{self.tag_stack[-1]}>'"
                    )
                self.tag_stack.pop()
                return Ops.Close
            elif tokens[1].content == "!":
                name = ""
                j = 2
                while j < len(tokens):
                    if tokens[j].content.strip() == "":
                        break
                    else:
                        name += tokens[j].content
                    j += 1

                self_close = True
                attr_tokens = tokens[j + 1 : -1]
                attrs = self._parses_attr_tokens(attr_tokens)
            else:
                name = tokens[1].content.strip()
                self_close = tokens[-2] == "/" or name in self_closing
                attr_tokens = tokens[3 : -2 if self_close else -1]
                attrs = self._parses_attr_tokens(attr_tokens)

            if (
                len(self.tag_stack) > 0
                and self.tag_stack[-1] in ["python", "script", "style"]
                and name
                not in [
                    "python",
                    "script",
                    "style",
                ]
            ):
                return Ops.NoOp
            return Element(
                name,
                attributes=attrs,
                children=None if self_close else [],
                position=Position(tokens[0].start, tokens[-1].end),
            )

    def parse(self, code: str) -> AST:
        tokens = self.tokenize(code)

        root = AST()
        current: Parent = root

        i = 0
        text_tokens = []
        while i < len(tokens):
            if tokens[i].content == "<":
                end = self._get_end_of_tag(tokens, i + 1)
                if end is not None:
                    # Parse tokens into a tag opening
                    content = "".join(token.content for token in text_tokens)
                    idx = tokens.index(end)

                    node = self._parse_tag_tokens(tokens[i : idx + 1])
                    if node != Ops.NoOp and len(text_tokens) > 0:
                        if "pre" in self.tag_stack or content.strip() != "":
                            current.append(
                                Literal(
                                    LiteralType.Text,
                                    content,
                                    position=Position(
                                        text_tokens[0].start, text_tokens[-1].end
                                    ),
                                )
                            )
                        text_tokens = []

                    if isinstance(node, Node):
                        current.append(node)
                        if isinstance(node, Element) and node.children is not None:
                            self.tag_stack.append(node.tag)
                            current = node
                    elif node == Ops.Close:
                        if current.position is not None:
                            current.position.end = Point(*tokens[idx].end)
                        if current.parent is not None:
                            current = current.parent
                    else:
                        print(repr(current))
                        text_tokens.extend(tokens[i : idx + 1])

                    i = idx
                else:
                    text_tokens.append(tokens[i])
            else:
                text_tokens.append(tokens[i])
            i += 1

        if len(text_tokens) > 0:
            content = "".join(token.content for token in text_tokens)
            if "pre" in self.tag_stack or content.strip() != "":
                current.append(
                    Literal(
                        LiteralType.Text,
                        "".join(token.content for token in text_tokens),
                        position=Position(text_tokens[0].start, text_tokens[-1].end),
                    )
                )

        if len(self.tag_stack) > 0:
            raise Exception(
                f"Tags were expected to be closed; {', '.join(self.tag_stack)}"
            )

        return current


if __name__ == "__main__":
    from time import time_ns 

    n_parser = Parser()
    h_parser = HypertextMarkupParser()

    #     code = """\
    # <!DOCTYPE html>
    # <!-- Comment -->
    # """

    with Path("../examples/loops/unicode.phml").open("r", encoding="utf-8") as file:
        code = file.read()

    # code = phml

    # print(parser.tokenize(code))
    n_start = time_ns()
    n_ast = n_parser.parse(code)
    n_total = time_ns() - n_start

    h_start = time_ns()
    h_ast = h_parser.parse(code)
    h_total = time_ns() - h_start

    # print(inspect(n_ast, color=True, text=True))
    # print(inspect(h_ast, color=True, text=True))
    result = "<" if n_total < h_total else ">"
    print(f"Tokenize {result} Regex:\n  {round(n_total * (10**-9), 9)}s {result} {round(h_total * (10**-9), 9)}s")
