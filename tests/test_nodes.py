from pytest import raises

from phml.nodes import (
    LiteralType,
    Point,
    Position,
    Node,
    Parent,
    AST,
    Element,
    Literal,
    NodeType,
)


def test_point():
    with raises(IndexError, match="Point.line must be >= 0 but was .+"):
        Point(-1, 0)
    with raises(IndexError, match="Point.column must be >= 0 but was .+"):
        Point(0, -1)

    assert Point.from_dict({"line": 0, "column": 0}) == Point(0, 0), "Expected from_dict to produce Point(0, 0)"


def test_position():
    position = Position((0, 0), (0, 0))
    pos_dict = {"start": {"line": 0, "column": 0}, "end": {"line": 0, "column": 0}}
    assert position == Position(Point(0, 0), Point(0, 0)), "Expected that both forms of constructor create the same object"
    assert Position.from_pos(position) == position, "Expected from_pos to create a copy of another position"
    assert Position.from_dict(pos_dict) == position, "Expected from_dict to produce Position((0, 0), (0, 0))"
    assert position.as_dict() == pos_dict, "Invalid dict produced form as_dict"


def test_node():
    node = Node(NodeType.AST, None, None, False)
    assert node.type == NodeType.AST, "Expected node.type to be 'ast'"
    assert node.position == None, "Expected position to be None"
    assert node.as_dict() == {"type": "ast", "position": None}, "Invalid dict produced from as_dict"
    element = {
        "type": "element",
        "children": None,
        "position": None,
        "attributes": {},
        "tag": "div",
    }
    assert isinstance(Node.from_dict(element), Element), "Expected from_dict to produce an Element"
    assert isinstance(
        Node.from_dict({"type": "ast", "position": None, "children": None}), AST
    ), "Expected from_dict to produce an AST without children"

    assert isinstance(
        Node.from_dict(
            {
                "type": "ast",
                "position": None,
                "children": [
                    {"type": "literal", "position": None, "name": "text", "content": ""}
                ],
            }
        ),
        AST,
    ), "Expected from_dict to produce an AST with children"
    literal = Node.from_dict(
        {"type": "literal", "position": None, "name": "text", "content": ""}
    )
    assert isinstance(literal, Literal) and Literal.is_text(
        literal
    ), "Expected from_dict to produce a text literal"
    with raises(
        ValueError, match="Phml ast dicts must have nodes with the following types: .+"
    ):
        Node.from_dict({"type": "invalid", "position": None})


def test_parent():
    parent = Parent(NodeType.ELEMENT, None)
    node = Node(NodeType.ELEMENT)
    literal = Literal(LiteralType.Text, "")

    # No errors when iterating None children
    assert (
        len([node for node in parent]) == 0
    ), "Expected that len is 0 even though children is None"

    with raises(ValueError, match="A self closing element can not pop a child node"):
        parent.pop(0)
    with raises(ValueError, match="A self closing element can not be indexed"):
        parent[0]
    with raises(ValueError, match="A self closing element can not be indexed"):
        parent.index(AST())
    with raises(
        ValueError, match="A child node can not be appended to a self closing element"
    ):
        parent.append(AST())
    with raises(
        ValueError, match="A self closing element can not have it's children extended"
    ):
        parent.extend([])
    with raises(
        ValueError, match="A child node can not be inserted into a self closing element"
    ):
        parent.insert(0, AST())
    with raises(
        ValueError, match="A child node can not be removed from a self closing element."
    ):
        parent.remove(AST())

    parent.children = []
    parent.append(node)
    assert parent[0] == node, "Expected first child to be node"
    parent.remove(node)
    assert len(parent) == 0, "Expected len to be 0"
    parent.extend([node, node])
    assert parent[:] == [node, node], "Expected children slice to be [node, node]"
    parent.insert(0, literal)
    assert parent[0] == literal, "Expected first child to be a literal"
    parent.remove(literal)
    parent[1] = literal
    assert parent[1] == literal, "Expected second child to be a literal"
    parent[:] = [node, literal]
    assert parent[:] == [
        node,
        literal,
    ], "Expected slice of children to be [node, literal]"
    del parent[0]
    assert (
        len(parent) == 1 and parent[0] == literal
    ), "Expected len of 1 and only child to be a literal"
    parent.insert(0, [node, node])
    del parent[:-1]
    assert (
        len(parent) == 1 and parent[0] == literal
    ), "Expected len of 1 and only child to be a literal"
    parent.append(node)
    parent.pop(0)
    assert (
        len(parent) == 1 and parent[0] == node
    ), "Expected len of of 1 and the only child to be a node"
    assert parent.index(node) == 0, "Expected node at index 0"
    parent[0] = literal

    parent_dict = {
        "type": "element",
        "position": None,
        "children": [
            {"type": "literal", "position": None, "name": "text", "content": ""}
        ],
    }
    assert parent.as_dict() == parent_dict, "Invalid dict from parent node"


def test_ast():
    AST()


def test_element():
    element = Element("div", attributes={"id": "test", "hidden": True}, children=[])
    element_nc = Element("div", attributes={"id": "test", "hidden": True}, in_pre=True)

    with raises(ValueError, match="A self closing element can not pop a child node"):
        element_nc.pop()
    with raises(TypeError, match="_default value must be str, bool, or MISSING"):
        element_nc.get("invalid", 3)
    with raises(ValueError, match="Attribute '.+' not found"):
        element_nc.get("invalid")
    with raises(ValueError, match="A self closing element can not have it's children indexed"):
        element_nc[0]

    el = {
        "type": "element",
        "position": None,
        "attributes": {"id": "test", "hidden": True},
        "children": [],
        "tag": "div",
    }
    assert Element.from_dict(el) == element, "Not a valid element from a dict"
    assert element.as_dict() == el, "Invalid dict from an element"
    element.append(Element("div"))
    assert element[0].tag_path == [
        "div",
        "div",
    ], "Invalid tag path, expected ['div', 'div']"

    assert "id" in element, "Expected attribute 'id' to be in element"
    assert element["id"] == "test", "Expected element attribute 'id' to be 'test'"
    element["id"] = "test-mod"
    assert element["id"] == "test-mod", "Expected element attribute 'id' to be 'test-mod'" 
    assert element.get("id") == "test-mod", "Expected element.get('id') to be 'test-mod'"
    assert element.get("invalid", "default") == "default", "Expected element.get to return default value 'default'"
    assert element.pop("id") == "test-mod", "Expected element.pop to return value of element attribute 'id'"
    assert element.pop("invalid", "default") == "default", "Expected element.pop to return default value 'default'"
    assert element.pop() == Element("div"), "Expected element.pop() to return first element"
    assert "hidden" in element, "Expected attribute 'hidden' to be in element"
    del element["hidden"]
    assert "hidden" not in element, "Expected attribute 'hidden' to be deleted from element"


def test_literal():
    literal_text = Literal(LiteralType.Text, "text")
    literal_comment = Literal(LiteralType.Comment, "comment")

    assert literal_text.as_dict() == {
        "type": "literal",
        "position": None,
        "name": "text",
        "content": "text",
    }, "Invalid dict produced from as_dict"
    assert literal_comment.as_dict() == {
        "type": "literal",
        "position": None,
        "name": "comment",
        "content": "comment",
    }, "Invalid dict produced from as_dict"

    assert Literal.is_text(literal_text), "Expected node to be a Literal text node"
    assert Literal.is_comment(literal_comment), "Expected node to be a Literal comment node"
    assert Literal.is_text(literal_comment) == False, "Expected comment node to not be a Literal text node"


def test_literal_type():
    assert LiteralType.From("text") == "text", "Expected to get 'text' back"
    with raises(ValueError, match="Expected on of.+"):
        LiteralType.From("invalid")
