from tedtest import UnitTest
from tedtest.UnitTest import Test, assertThat, eq
from phml import AST, Parser, Root, Element, Text, Comment, DocType, Position, Point


class Parse(Test):
    def __init__(self):
        self.expected = {
            "ast": AST(
                Root(
                    children=[
                        DocType(position=Position(Point(1, 0), Point(1, 0))),
                        Element(
                            "html",
                            {"lang": "en"},
                            position=Position(Point(2, 0), Point(13, 0), 0),
                            children=[
                                Element(
                                    "head",
                                    {},
                                    position=Position(Point(3, 4), Point(8, 4), 1),
                                    children=[
                                        Element(
                                            "meta",
                                            {"charset": "UTF-8"},
                                            position=Position(Point(4, 8), Point(4, 30)),
                                            openclose=True,
                                        ),
                                        Element(
                                            "meta",
                                            {
                                                "http-equiv": "X-UA-Compatible",
                                                "content": "IE=edge",
                                            },
                                            position=Position(Point(5, 8), Point(5, 61)),
                                            openclose=True,
                                        ),
                                        Element(
                                            "meta",
                                            {
                                                "name": "viewport",
                                                "content": "width=device-width, initial-scale=1.0",
                                            },
                                            position=Position(Point(6, 8), Point(6, 78)),
                                            openclose=True,
                                        ),
                                        Element(
                                            "title",
                                            {},
                                            position=Position(Point(7, 8), Point(7, 23)),
                                            children=[
                                                Text(
                                                    "Document",
                                                    position=Position(Point(7, 15), Point(7, 23)),
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                                Element(
                                    "body",
                                    {},
                                    position=Position(Point(9, 4), Point(12, 4), 1),
                                    children=[
                                        Comment(
                                            " Text Comment ",
                                            position=Position(Point(10, 8), Point(10, 29)),
                                        ),
                                        Element(
                                            "h1",
                                            {},
                                            position=Position(Point(11, 8), Point(11, 24)),
                                            children=[
                                                Text(
                                                    "Hello World!",
                                                    position=Position(Point(11, 12), Point(11, 24)),
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ]
                )
            ),
            "phml": '''\
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Document</title>
    </head>
    <body>
        <!-- Text Comment -->
        <h1>Hello World!</h1>
    </body>
</html>\
''',
        "json": {
            "type": "root",
            "children": [
                {
                "type": "doctype",
                "value": "html"
                },
                {
                "type": "element",
                "tag": "html",
                "properties": {
                    "lang": "en"
                },
                "startend": False,
                "children": [
                    {
                    "type": "element",
                    "tag": "head",
                    "properties": {},
                    "startend": False,
                    "children": [
                        {
                        "type": "element",
                        "tag": "meta",
                        "properties": {
                            "charset": "UTF-8"
                        },
                        "startend": True,
                        "children": []
                        },
                        {
                        "type": "element",
                        "tag": "meta",
                        "properties": {
                            "http-equiv": "X-UA-Compatible",
                            "content": "IE=edge"
                        },
                        "startend": True,
                        "children": []
                        },
                        {
                        "type": "element",
                        "tag": "meta",
                        "properties": {
                            "name": "viewport",
                            "content": "width=device-width, initial-scale=1.0"
                        },
                        "startend": True,
                        "children": []
                        },
                        {
                        "type": "element",
                        "tag": "title",
                        "properties": {},
                        "startend": False,
                        "children": [
                            {
                            "type": "text",
                            "value": "Document"
                            }
                        ]
                        }
                    ]
                    },
                    {
                    "type": "element",
                    "tag": "body",
                    "properties": {},
                    "startend": False,
                    "children": [
                        {
                        "type": "comment",
                        "value": " Text Comment "
                        },
                        {
                        "type": "element",
                        "tag": "h1",
                        "properties": {},
                        "startend": False,
                        "children": [
                            {
                            "type": "text",
                            "value": "Hello World!"
                            }
                        ]
                        }
                    ]
                    }
                ]
                }
            ]
            }
        }

    @UnitTest.test
    def valid_ast(self):
        parser = Parser()

        parser.parse("sample.phml")

        UnitTest.assertThat(
            self.expected["ast"], UnitTest.eq(parser.ast), "Ast values are not equal"
        )
        
    @UnitTest.test
    def ast_output_phml(self):
        parser = Parser()
        parser.parse("sample.phml")
        
        assertThat(self.expected["phml"], eq(parser.ast.to_phml()))

    @UnitTest.test
    def ast_output_json(self):
        from json import dumps
        parser = Parser()
        parser.parse("sample.phml")
        
        with open("log.txt", "+a", encoding="utf-8") as  log_file:
            log_file.write(parser.ast.to_json())
            log_file.write("\n----------------\n")
            log_file.write(dumps(self.expected["json"], indent=2))
        
        assertThat(dumps(self.expected["json"], indent=2), eq(parser.ast.to_json()))
   
    @UnitTest.test
    def ast_output_html(self):
        raise NotImplementedError
        parser = Parser()
        parser.parse("sample.phml")
        
        assertThat(self.expected["html"], eq(parser.ast.to_html()))