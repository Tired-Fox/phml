from phml.builder import p
from phml.core.nodes import AST, Text, Element, Position, Point
from phml import inspect

with_position = {
    "el": Element(
        "div",
        position=Position(Point(1, 2), Point(3, 4), 3),
        children=[Text("Test", position=Position(Point(5, 6), Point(7, 8)))],
    ),
    "expected": '''\
element<div> [1] <1:2-3:4 ~ 3>
└0 text <5:6-7:8>
   │  "Test"\
''',
}

def test_with_ast():
    assert inspect(AST(p())) == "root"
    assert inspect(AST(p(p("div", p("div"))))) == "root [1]\n└0 element<div> [1]\n   └0 element<div/>"

def test_with_position():
    assert inspect(with_position["el"]) == with_position["expected"]

without_position = {
    "el": p("div", "Test"),
    "expected": '''\
element<div> [1]
└0 text
   │  "Test"\
''',
}

def test_without_position():
    assert inspect(without_position["el"]) == without_position["expected"]

text = {
    "el": p("Some Text"),
    "expected": '''\
text
│  "Some Text"\
''',
}

def test_literal_node():
    assert inspect(text["el"]) == text["expected"]

multiline_text = {
    "el": p("Some\nmultiline\ntext"),
    "expected": '''\
text
│  "Some
│   multiline
│   text"\
''',
}

def test_multiline_literal_node():
    assert inspect(multiline_text["el"]) == multiline_text["expected"]

with_props = {
    "el": p("div", {"id": "test", "hidden": True}),
    "expected": """\
element<div/>
│  properties: {
│    "id": \"test\",
│    "hidden": true
│  }\
""",
}

def test_element_with_props():
    assert inspect(with_props["el"]) == with_props["expected"]
