from phml.nodes import *
from pathlib import Path

__all__ = ["phml_file", "html_file", "phml_ast", "html_ast", "hashes"]

phml_file = """\
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
            <p slot="extra">Extra</p>
        </Sub.Component>
        <input
            type="text"
            max="100"
            value="{{ start }} with this, not {{ end }}"
            :hidden="True"
        >
        <p @if="False">Never shows</p>
        <p @elif="not blank(message)">{{ message }}</p>
        <p @else>Fallback</p>
        <ul>
            <For :each="error in errors">
                <li>{{error}}</li>
            </For>
            <li @else>Loop fallback</li>
        </ul>
    </body>
</html>
<!--Extra comment at end of file-->
Extra text at end of file\
"""

html_file = """\
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
    </style>
    <script>
      window.onload = () => {
        alert("Test");
      };
    </script>
    <style>
      div {
        margin: 0;
      }
      [data-phml-cmpt-scope='Component~3090413834174898802'] div {
        color: red
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
        <p>Extra</p>
      </div>
    </div>
    <input
      type="text"
      max="100"
      value="Startwith this, not end."
      hidden
    />
    <p>Hello World!</p>
    <ul>
      <li>1</li>
      <li>2</li>
    </ul>
  </body>
</html>
<!--Extra comment at end of file-->
Extra text at end of file\
"""

phml_ast = AST(
    position=None,
    children=[
        Element(
            "html",
            position=Position(Point(0, 0), Point(17, 37)),
            attributes={},
            children=[
                Element(
                    "head",
                    position=Position(Point(0, 6), Point(10, 24)),
                    attributes={},
                    children=[
                        Element(
                            "title",
                            position=Position(Point(0, 12), Point(2, 16)),
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
                    position=Position(Point(10, 24), Point(17, 30)),
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
                            position=Position(Point(12, 33), Point(12, 25)),
                            attributes={},
                            children=[
                                Element(
                                    "p",
                                    position=Position(Point(12, 48), Point(12, 9)),
                                    attributes={},
                                    children=[Literal("text", "Child")],
                                ),
                                Element(
                                    "p",
                                    position=Position(Point(12, 9), Point(12, 9)),
                                    attributes={"slot": "extra"},
                                    children=[Literal("text", "Extra")],
                                ),
                            ],
                        ),
                        Element(
                            "input",
                            position=Position(Point(12, 25), Point(17, 40)),
                            attributes={
                                "type": "text",
                                "max": "100",
                                "value": "{{ start }} with this, not {{ end }}",
                                ":hidden": "True",
                            },
                            children=None,
                        ),
                        Element(
                            "p",
                            position=Position(Point(17, 40), Point(17, 15)),
                            attributes={"@if": "False"},
                            children=[Literal("text", "Never shows")],
                        ),
                        Element(
                            "p",
                            position=Position(Point(17, 15), Point(17, 17)),
                            attributes={"@elif": "not blank(message)"},
                            children=[Literal("text", "{{ message }}")],
                        ),
                        Element(
                            "p",
                            position=Position(Point(17, 17), Point(17, 12)),
                            attributes={"@else": True},
                            children=[Literal("text", "Fallback")],
                        ),
                        Element(
                            "ul",
                            position=Position(Point(17, 12), Point(17, 23)),
                            attributes={},
                            children=[
                                Element(
                                    "For",
                                    position=Position(Point(17, 16), Point(17, 20)),
                                    attributes={":each": "error in errors"},
                                    children=[
                                        Element(
                                            "li",
                                            position=Position(
                                                Point(17, 45), Point(17, 14)
                                            ),
                                            attributes={},
                                            children=[Literal("text", "{{error}}")],
                                        )
                                    ],
                                ),
                                Element(
                                    "li",
                                    position=Position(Point(17, 20), Point(17, 18)),
                                    attributes={"@else": True},
                                    children=[Literal("text", "Loop fallback")],
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

html_ast = AST(
    position=None,
    children=[
        Element(
            "html",
            position=Position(Point(0, 0), Point(17, 37)),
            attributes={},
            children=[
                Element(
                    "head",
                    position=Position(Point(0, 6), Point(10, 24)),
                    attributes={},
                    children=[
                        Element(
                            "title",
                            position=Position(Point(0, 12), Point(2, 16)),
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
                                    "\ndiv {\n  margin: 0;\n}\n[data-phml-cmpt-scope='Component~3090413834174898802'] div {\n  color: red\n}\n",
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
                    position=Position(Point(10, 24), Point(17, 30)),
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
                                    position=Position(Point(0, 0), Point(0, 48)),
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
                                        Element(
                                            "p",
                                            position=Position(
                                                Point(12, 9), Point(12, 9)
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
                            position=Position(Point(12, 25), Point(17, 40)),
                            attributes={
                                "type": "text",
                                "max": "100",
                                "value": "Startwith this, not end.",
                                "hidden": True,
                            },
                            children=None,
                        ),
                        Element(
                            "p",
                            position=Position(Point(17, 15), Point(17, 17)),
                            attributes={},
                            children=[Literal("text", "Hello World!")],
                        ),
                        Element(
                            "ul",
                            position=Position(Point(17, 12), Point(17, 23)),
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
                    ],
                ),
            ],
        ),
        Literal("comment", "Extra comment at end of file"),
        Literal("text", "Extra text at end of file"),
    ],
)

hashes = {
    "Component": "Component~3090413834174898802",
    "Sub.Component": "Sub.Component~6689333506419787003",
}

if __name__ == "__main__":
    #!PERF: This should only be used in manual testing
    from phml import HypertextManager

    with Path("src/index.phml").open("+w", encoding="utf-8") as file:
        file.write(phml_file)

    with HypertextManager.open("src/index.phml") as phml:
        phml.parse()

        print(p_code(phml.ast), "\n\n")

        # Add components
        phml.add("src/component.phml", ignore="src/")
        phml.add("src/sub/component.phml", ignore="src/")

        # Set hashes for components for testing
        phml.components["Component"]["hash"] = hashes["Component"]
        phml.components["Sub.Component"]["hash"] = hashes["Sub.Component"]

        print(p_code(phml.compile(message="Hello World!")))

        phml.render(message="Hello World!")
