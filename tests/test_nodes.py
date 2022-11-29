from phml.nodes import *

def test_point():
    point = Point(1, 3)
    assert (
        point.line == 1
        and point.column == 3
        and point.offset == None
    )

def test_position():
    position = Position(Point(1, 2), Point(3, 4))
    assert (
        (
            position.start.line == 1
            and position.start.column == 2
        )
        and (
            position.end.line == 3
            and position.end.column == 4
        )
        and position.indent is None
    )

def test_root():
    root = Root()
    assert (
        root.parent is None
        and root.position is None
        and len(root.children) == 0
    )
    
def test_element():
    element = Element()
    assert (
        element.tag == "element"
        and element.properties == {}
        and element.parent == None
        and element.position == None
        and element.startend == False
        and len(element.children) == 0
    )
    
    element = Element("div", {"id": "test"})
    assert element.start_tag() == '<div id="test">' and element.end_tag() == "</div>"
    
    element = Element("input", {"type": "checkbox"}, startend=True)
    assert element.start_tag() == '<input type="checkbox" />' and element.end_tag() is None
    
def test_doctype():
    doctype = DocType()
    assert (
        doctype.parent is None
        and doctype.position is None
        and doctype.lang == "html"
    )
    
    assert doctype.stringify() == "<!DOCTYPE html>"
    
def test_text():
    text = Text()
    assert text.value == "" and text.position is None and text.parent is None
    
    text = Text("Sample")
    assert text.stringify() == "Sample" and text.stringify(2) == "  Sample"
    
    raw = """\
multiline
text\
"""
    rendered = """\
  multiline
  text\
"""
    text = Text(raw)
    assert text.stringify() == raw and text.stringify(2) == rendered

def test_comment():
    comment = Comment()
    assert comment.value == "" and comment.position is None and comment.parent is None
    
    comment = Comment("Sample")
    assert comment.stringify() == "<!--Sample-->" and comment.stringify(2) == "  <!--Sample-->"
    
    raw = """\
<!--multiline
text-->\
"""
    rendered = """\
  <!--multiline
  text-->\
"""
    comment = Comment("""\
multiline
text\
""")
    assert comment.stringify() == raw and comment.stringify(2) == rendered