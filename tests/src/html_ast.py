AST(
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
                                "value": "Start with this, not end.",
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
