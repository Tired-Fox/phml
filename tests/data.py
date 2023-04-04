from phml.nodes import *
from pathlib import Path

__all__ = [
    "phml_file",
    "html_file",
    "phml_ast",
    "html_ast",
    "hashes",
    "message",
    "html_file_compressed",
    "phml_dict",
]

phml_file = """\
<!DOCTYPE html>
<html>
    <head>
        <title>
            Sample title
        </title>
        <python>
            start = "Start"
            end = "end."

            errors = [
                "1",
                "2"
            ]
        </python>
    </head>
    <body>
        <Component :message="message" />
        <!-- Sample Comment 1 -->
        Sample Text
        <!-- Sample Comment 2 -->
        <Sub.Component>
            <p>Child</p>
            Generic text
            <p slot="extra">Extra</p>
        </Sub.Component>
        <input
            type="text"
            max="100"
            value="{{ start }} with this, not {{ end }}"
            :hidden="True"
            data-is-active="no"
        >
        <p @if="False">Never shows</p>
        <p @elif="not blank(message)">{{ message }}</p>
        <p @else>Fallback</p>
        <pre>text</pre>
        <ul>
            <For :each="error in errors">
                <li>{{error}}</li>
            </For>
            <li @else>Loop fallback</li>
        </ul>
        <Markdown
          src="tests/src/readme.md"
          extras="footnotes"
          :configs="{
            'footnotes': {
              'BACKLINK_TEXT': '$'
            }
          }"
        />
    </body>
</html>
<!--Extra comment at end of file-->
Extra text at end of file\
"""

html_file = """\
<!DOCTYPE html>
<html>
  <head>
    <title>Sample title</title>
    <style>
      div {
        margin: 0;
      }
      [data-phml-cmpt-scope='Component~3090413834174898802'] div {
        color: red
      }

      [data-phml-cmpt-scope='Component~3090413834174898802'] :is(.card),
      [data-phml-cmpt-scope='Component~3090413834174898802'] span {
        border: 1px solid black;
      }
    </style>
    <script>
      window.onload = () => {
        alert("Test");
      };
    </script>
  </head>
  <body>
    <div data-phml-cmpt-scope="Component~3090413834174898802">
      <p>Component</p>
      <p>Hello World!</p>
    </div>
    <!--Sample Comment 1-->
    Sample Text
    <!--Sample Comment 2-->
    <div data-phml-cmpt-scope="Sub.Component~6689333506419787003">
      <div>
        <p>Sub component</p>
        <p>Child</p>
        Generic text
        <p>Extra</p>
      </div>
    </div>
    <input
      type="text"
      max="100"
      value="Startwith this, not end."
      data-is-active="false"
      hidden
    />
    <p>Hello World!</p>
<pre>text</pre>
    <ul>
      <li>1</li>
      <li>2</li>
    </ul>
    <article>
      <h1>Sample Markdown</h1>
      <p>Markdown text here</p>
    </article>
  </body>
</html>
<!--Extra comment at end of file-->
Extra text at end of file\
"""

html_file_compressed = """\
<!DOCTYPE html><html><head><title>Sample title</title><style>div {
  margin: 0;
}
[data-phml-cmpt-scope='Component~3090413834174898802'] div {
  color: red
}

[data-phml-cmpt-scope='Component~3090413834174898802'] :is(.card),
[data-phml-cmpt-scope='Component~3090413834174898802'] span {
  border: 1px solid black;
}</style><script>window.onload = () => {
  alert("Test");
};</script></head><body><div data-phml-cmpt-scope="Component~3090413834174898802"><p>Component</p><p>Hello World!</p></div><!--Sample Comment 1-->Sample Text<!--Sample Comment 2--><div data-phml-cmpt-scope="Sub.Component~6689333506419787003"><div><p>Sub component</p><p>Child</p>Generic text<p>Extra</p></div></div><input type="text" max="100" value="Startwith this, not end." data-is-active="false" hidden/><p>Hello World!</p><pre>text</pre><ul><li>1</li><li>2</li></ul><article><h1>Sample Markdown</h1><p>Markdown text here</p></article></body></html><!--Extra comment at end of file-->Extra text at end of file\
"""

phml_ast = AST(
    position=None,
    children=[
        Element(
            "doctype",
            position=Position(Point(0, 0), Point(0, 15)),
            attributes={"lang": "html"},
            children=None,
        ),
        Element(
            "html",
            position=Position(Point(0, 15), Point(28, 56)),
            attributes={},
            children=[
                Element(
                    "head",
                    position=Position(Point(0, 21), Point(10, 24)),
                    attributes={},
                    children=[
                        Element(
                            "title",
                            position=Position(Point(0, 27), Point(2, 16)),
                            attributes={},
                            children=[Literal("text", "Sample title")],
                        ),
                        Element(
                            "python",
                            position=Position(Point(2, 16), Point(10, 17)),
                            attributes={},
                            children=[
                                Literal(
                                    "text",
                                    '\n            start = "Start"\n            end = "end."\n\n            errors = [\n                "1",\n                "2"\n            ]\n        ',
                                )
                            ],
                        ),
                    ],
                ),
                Element(
                    "body",
                    position=Position(Point(10, 24), Point(28, 49)),
                    attributes={},
                    children=[
                        Element(
                            "Component",
                            position=Position(Point(10, 30), Point(10, 62)),
                            attributes={":message": "message"},
                            children=None,
                        ),
                        Literal("comment", " Sample Comment 1 "),
                        Literal("text", "Sample Text"),
                        Literal("comment", " Sample Comment 2 "),
                        Element(
                            "Sub.Component",
                            position=Position(Point(12, 33), Point(14, 25)),
                            attributes={},
                            children=[
                                Element(
                                    "p",
                                    position=Position(Point(12, 48), Point(12, 9)),
                                    attributes={},
                                    children=[Literal("text", "Child")],
                                ),
                                Literal("text", "Generic text"),
                                Element(
                                    "p",
                                    position=Position(Point(14, 12), Point(14, 9)),
                                    attributes={"slot": "extra"},
                                    children=[Literal("text", "Extra")],
                                ),
                            ],
                        ),
                        Element(
                            "input",
                            position=Position(Point(14, 25), Point(20, 40)),
                            attributes={
                                "type": "text",
                                "max": "100",
                                "value": "{{ start }} with this, not {{ end }}",
                                ":hidden": "True",
                                "data-is-active": False,
                            },
                            children=None,
                        ),
                        Element(
                            "p",
                            position=Position(Point(20, 40), Point(20, 15)),
                            attributes={"@if": "False"},
                            children=[Literal("text", "Never shows")],
                        ),
                        Element(
                            "p",
                            position=Position(Point(20, 15), Point(20, 17)),
                            attributes={"@elif": "not blank(message)"},
                            children=[Literal("text", "{{ message }}")],
                        ),
                        Element(
                            "p",
                            position=Position(Point(20, 17), Point(20, 12)),
                            attributes={"@else": True},
                            children=[Literal("text", "Fallback")],
                        ),
                        Element(
                            "pre",
                            position=Position(Point(20, 12), Point(20, 10)),
                            attributes={},
                            children=[Literal("text", "text", in_pre=True)],
                            in_pre=True,
                        ),
                        Element(
                            "ul",
                            position=Position(Point(20, 10), Point(20, 23)),
                            attributes={},
                            children=[
                                Element(
                                    "For",
                                    position=Position(Point(20, 14), Point(20, 20)),
                                    attributes={":each": "error in errors"},
                                    children=[
                                        Element(
                                            "li",
                                            position=Position(
                                                Point(20, 43), Point(20, 14)
                                            ),
                                            attributes={},
                                            children=[Literal("text", "{{error}}")],
                                        )
                                    ],
                                ),
                                Element(
                                    "li",
                                    position=Position(Point(20, 20), Point(20, 18)),
                                    attributes={"@else": True},
                                    children=[Literal("text", "Loop fallback")],
                                ),
                            ],
                        ),
                        Element(
                            "Markdown",
                            position=Position(Point(20, 23), Point(28, 42)),
                            attributes={
                                "src": "tests/src/readme.md",
                                "extras": "footnotes",
                                ":configs": "{\n            'footnotes': {\n              'BACKLINK_TEXT': '$'\n            }\n          }",
                            },
                            children=None,
                        ),
                    ],
                ),
            ],
        ),
        Literal("comment", "Extra comment at end of file"),
        Literal("text", "Extra text at end of file"),
    ],
)


html_ast = AST(
    position=None,
    children=[
        Element(
            "doctype",
            position=Position(Point(0, 0), Point(0, 15)),
            attributes={"lang": "html"},
            children=None,
        ),
        Element(
            "html",
            position=Position(Point(0, 15), Point(28, 56)),
            attributes={},
            children=[
                Element(
                    "head",
                    position=Position(Point(0, 21), Point(10, 24)),
                    attributes={},
                    children=[
                        Element(
                            "title",
                            position=Position(Point(0, 27), Point(2, 16)),
                            attributes={},
                            children=[Literal("text", "Sample title")],
                        ),
                        Element(
                            "style",
                            position=None,
                            attributes={},
                            children=[
                                Literal(
                                    "text",
                                    "\ndiv {\n  margin: 0;\n}\n[data-phml-cmpt-scope='Component~3090413834174898802'] div {\n  color: red\n}\n\n[data-phml-cmpt-scope='Component~3090413834174898802'] :is(.card),\n[data-phml-cmpt-scope='Component~3090413834174898802'] span {\n  border: 1px solid black;\n}\n",
                                )
                            ],
                        ),
                        Element(
                            "script",
                            position=None,
                            attributes={},
                            children=[
                                Literal(
                                    "text",
                                    '\nwindow.onload = () => {\n  alert("Test");\n};\n',
                                )
                            ],
                        ),
                    ],
                ),
                Element(
                    "body",
                    position=Position(Point(10, 24), Point(28, 49)),
                    attributes={},
                    children=[
                        Element(
                            "div",
                            position=None,
                            attributes={
                                "data-phml-cmpt-scope": "Component~3090413834174898802"
                            },
                            children=[
                                Element(
                                    "p",
                                    position=Position(Point(4, 11), Point(4, 13)),
                                    attributes={},
                                    children=[Literal("text", "Component")],
                                ),
                                Element(
                                    "p",
                                    position=Position(Point(4, 13), Point(4, 17)),
                                    attributes={},
                                    children=[Literal("text", "Hello World!")],
                                ),
                            ],
                        ),
                        Literal("comment", " Sample Comment 1 "),
                        Literal("text", "Sample Text"),
                        Literal("comment", " Sample Comment 2 "),
                        Element(
                            "div",
                            position=None,
                            attributes={
                                "data-phml-cmpt-scope": "Sub.Component~6689333506419787003"
                            },
                            children=[
                                Element(
                                    "div",
                                    position=Position(Point(0, 0), Point(0, 70)),
                                    attributes={},
                                    children=[
                                        Element(
                                            "p",
                                            position=Position(
                                                Point(0, 5), Point(0, 17)
                                            ),
                                            attributes={},
                                            children=[Literal("text", "Sub component")],
                                        ),
                                        Element(
                                            "p",
                                            position=Position(
                                                Point(12, 48), Point(12, 9)
                                            ),
                                            attributes={},
                                            children=[Literal("text", "Child")],
                                        ),
                                        Literal("text", "Generic text"),
                                        Element(
                                            "p",
                                            position=Position(
                                                Point(14, 12), Point(14, 9)
                                            ),
                                            attributes={},
                                            children=[Literal("text", "Extra")],
                                        ),
                                    ],
                                )
                            ],
                        ),
                        Element(
                            "input",
                            position=Position(Point(14, 25), Point(20, 40)),
                            attributes={
                                "type": "text",
                                "max": "100",
                                "value": "Startwith this, not end.",
                                "data-is-active": False,
                                "hidden": True,
                            },
                            children=None,
                        ),
                        Element(
                            "p",
                            position=Position(Point(20, 15), Point(20, 17)),
                            attributes={},
                            children=[Literal("text", "Hello World!")],
                        ),
                        Element(
                            "pre",
                            position=Position(Point(20, 12), Point(20, 10)),
                            attributes={},
                            children=[Literal("text", "text", in_pre=True)],
                            in_pre=True,
                        ),
                        Element(
                            "ul",
                            position=Position(Point(20, 10), Point(20, 23)),
                            attributes={},
                            children=[
                                Element(
                                    "li",
                                    position=None,
                                    attributes={},
                                    children=[Literal("text", "1")],
                                ),
                                Element(
                                    "li",
                                    position=None,
                                    attributes={},
                                    children=[Literal("text", "2")],
                                ),
                            ],
                        ),
                        Element(
                            "article",
                            position=None,
                            attributes={},
                            children=[
                                Element(
                                    "h1",
                                    position=Position(Point(0, 0), Point(0, 20)),
                                    attributes={},
                                    children=[Literal("text", "Sample Markdown")],
                                ),
                                Element(
                                    "p",
                                    position=Position(Point(0, 20), Point(0, 22)),
                                    attributes={},
                                    children=[Literal("text", "Markdown text here")],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Literal("comment", "Extra comment at end of file"),
        Literal("text", "Extra text at end of file"),
    ],
)

phml_dict = {
    "children": [
        {
            "tag": "doctype",
            "attributes": {"lang": "html"},
            "children": None,
            "type": "element",
            "position": {
                "start": {"line": 0, "column": 0},
                "end": {"line": 0, "column": 15},
            },
        },
        {
            "tag": "html",
            "attributes": {},
            "children": [
                {
                    "tag": "head",
                    "attributes": {},
                    "children": [
                        {
                            "tag": "title",
                            "attributes": {},
                            "children": [
                                {
                                    "name": "text",
                                    "content": "Sample title",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 2, "column": 8},
                                        "end": {"line": 2, "column": 8},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 0, "column": 27},
                                "end": {"line": 2, "column": 16},
                            },
                        },
                        {
                            "tag": "python",
                            "attributes": {},
                            "children": [
                                {
                                    "name": "text",
                                    "content": '\n            start = "Start"\n            end = "end."\n\n            errors = [\n                "1",\n                "2"\n            ]\n        ',
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 10, "column": 8},
                                        "end": {"line": 10, "column": 8},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 2, "column": 16},
                                "end": {"line": 10, "column": 17},
                            },
                        },
                    ],
                    "type": "element",
                    "position": {
                        "start": {"line": 0, "column": 21},
                        "end": {"line": 10, "column": 24},
                    },
                },
                {
                    "tag": "body",
                    "attributes": {},
                    "children": [
                        {
                            "tag": "Component",
                            "attributes": {":message": "message"},
                            "children": None,
                            "type": "element",
                            "position": {
                                "start": {"line": 10, "column": 30},
                                "end": {"line": 10, "column": 62},
                            },
                        },
                        {
                            "name": "comment",
                            "content": " Sample Comment 1 ",
                            "type": "literal",
                            "position": {
                                "start": {"line": 10, "column": 62},
                                "end": {"line": 10, "column": 87},
                            },
                        },
                        {
                            "name": "text",
                            "content": "Sample Text",
                            "type": "literal",
                            "position": {
                                "start": {"line": 12, "column": 8},
                                "end": {"line": 12, "column": 8},
                            },
                        },
                        {
                            "name": "comment",
                            "content": " Sample Comment 2 ",
                            "type": "literal",
                            "position": {
                                "start": {"line": 12, "column": 8},
                                "end": {"line": 12, "column": 33},
                            },
                        },
                        {
                            "tag": "Sub.Component",
                            "attributes": {},
                            "children": [
                                {
                                    "tag": "p",
                                    "attributes": {},
                                    "children": [
                                        {
                                            "name": "text",
                                            "content": "Child",
                                            "type": "literal",
                                            "position": {
                                                "start": {"line": 12, "column": 5},
                                                "end": {"line": 12, "column": 56},
                                            },
                                        }
                                    ],
                                    "type": "element",
                                    "position": {
                                        "start": {"line": 12, "column": 48},
                                        "end": {"line": 12, "column": 9},
                                    },
                                },
                                {
                                    "name": "text",
                                    "content": "Generic text",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 14, "column": 12},
                                        "end": {"line": 14, "column": 12},
                                    },
                                },
                                {
                                    "tag": "p",
                                    "attributes": {"slot": "extra"},
                                    "children": [
                                        {
                                            "name": "text",
                                            "content": "Extra",
                                            "type": "literal",
                                            "position": {
                                                "start": {"line": 14, "column": 5},
                                                "end": {"line": 14, "column": 33},
                                            },
                                        }
                                    ],
                                    "type": "element",
                                    "position": {
                                        "start": {"line": 14, "column": 12},
                                        "end": {"line": 14, "column": 9},
                                    },
                                },
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 12, "column": 33},
                                "end": {"line": 14, "column": 25},
                            },
                        },
                        {
                            "tag": "input",
                            "attributes": {
                                "type": "text",
                                "max": "100",
                                "value": "{{ start }} with this, not {{ end }}",
                                ":hidden": "True",
                                "data-is-active": False,
                            },
                            "children": None,
                            "type": "element",
                            "position": {
                                "start": {"line": 14, "column": 25},
                                "end": {"line": 20, "column": 40},
                            },
                        },
                        {
                            "tag": "p",
                            "attributes": {"@if": "False"},
                            "children": [
                                {
                                    "name": "text",
                                    "content": "Never shows",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 20, "column": 11},
                                        "end": {"line": 20, "column": 66},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 40},
                                "end": {"line": 20, "column": 15},
                            },
                        },
                        {
                            "tag": "p",
                            "attributes": {"@elif": "not blank(message)"},
                            "children": [
                                {
                                    "name": "text",
                                    "content": "{{ message }}",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 20, "column": 13},
                                        "end": {"line": 20, "column": 58},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 15},
                                "end": {"line": 20, "column": 17},
                            },
                        },
                        {
                            "tag": "p",
                            "attributes": {"@else": True},
                            "children": [
                                {
                                    "name": "text",
                                    "content": "Fallback",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 20, "column": 8},
                                        "end": {"line": 20, "column": 34},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 17},
                                "end": {"line": 20, "column": 12},
                            },
                        },
                        {
                            "tag": "pre",
                            "attributes": {},
                            "children": [
                                {
                                    "name": "text",
                                    "content": "text",
                                    "type": "literal",
                                    "position": {
                                        "start": {"line": 20, "column": 4},
                                        "end": {"line": 20, "column": 21},
                                    },
                                }
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 12},
                                "end": {"line": 20, "column": 10},
                            },
                        },
                        {
                            "tag": "ul",
                            "attributes": {},
                            "children": [
                                {
                                    "tag": "For",
                                    "attributes": {":each": "error in errors"},
                                    "children": [
                                        {
                                            "tag": "li",
                                            "attributes": {},
                                            "children": [
                                                {
                                                    "name": "text",
                                                    "content": "{{error}}",
                                                    "type": "literal",
                                                    "position": {
                                                        "start": {
                                                            "line": 20,
                                                            "column": 9,
                                                        },
                                                        "end": {
                                                            "line": 20,
                                                            "column": 56,
                                                        },
                                                    },
                                                }
                                            ],
                                            "type": "element",
                                            "position": {
                                                "start": {"line": 20, "column": 43},
                                                "end": {"line": 20, "column": 14},
                                            },
                                        }
                                    ],
                                    "type": "element",
                                    "position": {
                                        "start": {"line": 20, "column": 14},
                                        "end": {"line": 20, "column": 20},
                                    },
                                },
                                {
                                    "tag": "li",
                                    "attributes": {"@else": True},
                                    "children": [
                                        {
                                            "name": "text",
                                            "content": "Loop fallback",
                                            "type": "literal",
                                            "position": {
                                                "start": {"line": 20, "column": 13},
                                                "end": {"line": 20, "column": 43},
                                            },
                                        }
                                    ],
                                    "type": "element",
                                    "position": {
                                        "start": {"line": 20, "column": 20},
                                        "end": {"line": 20, "column": 18},
                                    },
                                },
                            ],
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 10},
                                "end": {"line": 20, "column": 23},
                            },
                        },
                        {
                            "tag": "Markdown",
                            "attributes": {
                                "src": "tests/src/readme.md",
                                "extras": "footnotes",
                                ":configs": "{\n            'footnotes': {\n              'BACKLINK_TEXT': '$'\n            }\n          }",
                            },
                            "children": None,
                            "type": "element",
                            "position": {
                                "start": {"line": 20, "column": 23},
                                "end": {"line": 28, "column": 42},
                            },
                        },
                    ],
                    "type": "element",
                    "position": {
                        "start": {"line": 10, "column": 24},
                        "end": {"line": 28, "column": 49},
                    },
                },
            ],
            "type": "element",
            "position": {
                "start": {"line": 0, "column": 15},
                "end": {"line": 28, "column": 56},
            },
        },
        {
            "name": "comment",
            "content": "Extra comment at end of file",
            "type": "literal",
            "position": {
                "start": {"line": 28, "column": 56},
                "end": {"line": 28, "column": 91},
            },
        },
        {
            "name": "text",
            "content": "Extra text at end of file",
            "type": "literal",
            "position": {
                "start": {"line": 30, "column": 0},
                "end": {"line": 30, "column": 0},
            },
        },
    ],
    "type": "ast",
    "position": None,
}

hashes = {
    "Component": "Component~3090413834174898802",
    "Sub.Component": "Sub.Component~6689333506419787003",
}

message = "Hello World!"

if __name__ == "__main__":
    #!PERF: This should only be used in manual testing
    from phml import HypertextManager

    with Path("src/index.phml").open("+w", encoding="utf-8") as file:
        file.write(phml_file)

    phml = HypertextManager()
    phml.load("src/index.phml")
    print(phml.ast.as_dict(), "\n\n")
    print(p_code(phml.ast), "\n\n")

    # Add components
    phml.add("src/component.phml", ignore="src/")
    phml.add("src/sub/component.phml", ignore="src/")

    # Set hashes for components for testing
    phml.components["Component"]["hash"] = hashes["Component"]
    phml.components["Sub.Component"]["hash"] = hashes["Sub.Component"]

    print(p_code(phml.compile(message=message)))
    print(phml.render(message=message), "\n\n")
    print(phml.render(True, message=message))

    phml.write("src/index.html", message=message).write(
        "src/index-compressed.html", True, message=message
    )
