from pytest import raises

from phml.nodes import (AST, Element, Literal, LiteralType, Node, NodeType,
                        Parent, Point, Position)


def test_point():
    with raises(IndexError, match="Point.line must be >= 0 but was .+"):
        Point(-1, 0)

    with raises(IndexError, match="Point.column must be >= 0 but was .+"):
        Point(0, -1)

    assert Point.from_dict({"line": 0, "column": 0}) == Point(0, 0), "Expected from_dict to produce Point(0, 0)"


class TestPosition:
    position = Position((0, 0), (0, 0))
    pos_dict = {"start": {"line": 0, "column": 0}, "end": {"line": 0, "column": 0}}

    def test_alt_constructor(self):
        assert self.position == Position(Point(0, 0), Point(0, 0))

    def test_from_pos(self):
        assert Position.from_pos(self.position) == self.position

    def test_dict(self):
        assert Position.from_dict(self.pos_dict) == self.position
        assert self.position.as_dict() == self.pos_dict


class TestNode:
    def test_constructor(self):
        node = Node(NodeType.AST, None, None, False)
        assert node.type == NodeType.AST, "Expected node.type to be 'ast'"
        assert node.position == None, "Expected position to be None"


    def test_dict_literal(self):
        literal = Node.from_dict(
            {"type": "literal", "name": "text", "content": ""}
        )

        assert isinstance(literal, Literal) and Literal.is_text(
            literal
        ), "Expected from_dict to produce a text literal"

    def test_dict_element(self):
        node = Node(NodeType.AST, None, None, False)
        element = {
            "type": "element",
            "children": None,
            "attributes": {},
            "tag": "div",
            "decl": False
        }

        assert node.as_dict() == {"type": "ast"}

        assert isinstance(Node.from_dict(element), Element), "Expected from_dict to produce an Element"
        assert isinstance(
            Node.from_dict({"type": "ast", "children": None}), AST
        ), "Expected from_dict to produce an AST without children"
    
        assert isinstance(
            Node.from_dict(
                {
                    "type": "ast",
                    "children": [
                        {"type": "literal", "name": "text", "content": ""}
                    ],
                }
            ),
            AST,
        ), "Expected from_dict to produce an AST with children"

    def test_dict_exceptions(self):
        with raises(
            ValueError, match="Phml ast dicts must have nodes with the following types: .+"
        ):
            Node.from_dict({"type": "invalid"})


class TestParent:
    @property
    def node(self):
        return Node(NodeType.ELEMENT)

    @property
    def literal(self):
        return Literal(LiteralType.Text, "")

    def test_self_closing(self):
        parent = Parent(NodeType.ELEMENT, None)
        assert (
            parent.children is None
        )
        assert len(parent) == 0
        assert len([node for node in parent]) == 0

    def test_assigns_parent(self):
        parent = Parent(NodeType.ELEMENT, [self.literal])
        assert parent.children == [self.literal]
        assert parent.children is not None and parent.children[0].parent == parent
    
    def test_self_closing_exceptions(self):
        parent = Parent(NodeType.ELEMENT, None)

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
    
    def test_get(self):
        parent = Parent(NodeType.ELEMENT, [self.node, self.literal])
        assert parent[0] == self.node
        assert parent[:] == [self.node, self.literal]
        assert parent.index(self.literal) == 1

    def test_add(self):
        parent = Parent(NodeType.ELEMENT, [])

        parent.append(self.node)
        assert parent[0] == self.node

        parent.extend([self.node, self.node])
        assert parent[:] == [self.node, self.node, self.node]

        parent.insert(0, self.literal)
        assert parent[0] == self.literal

        parent.insert(0, [self.node, self.node])
        assert len(parent) == 6 and parent.children == [self.node, self.node, self.literal, self.node, self.node, self.node]

    def test_remove(self):
        node = self.node
        literal = self.literal
        parent = Parent(NodeType.ELEMENT, [node, literal])

        parent.remove(node)
        assert len(parent) == 1, "Expected len to be 0"

        del parent[0]
        assert len(parent) == 0

        parent.children = [self.node, self.literal, self.literal, self.node, self.literal]
        del parent[1:3]
        assert len(parent) == 3 and parent.children == [self.node, self.node, self.literal]

        parent.pop()
        assert (
            len(parent) == 2 and parent.children == [self.node, self.literal]
        )
       
        assert parent.pop(1) == self.literal and len(parent) == 1
        
    def test_set(self):
        parent = Parent(NodeType.ELEMENT, [self.node, self.node, self.node])

        parent[1] = self.literal
        assert parent[1] == self.literal

        parent[:] = [self.literal, self.literal]
        assert parent[:] == [
            self.literal,
            self.literal,
        ]

    
    def test_dict(self):
        parent = Parent(NodeType.ELEMENT, [self.literal])
        parent_dict = {
            "type": "element",
            "children": [
                {"type": "literal", "name": "text", "content": ""}
            ],
        }

        assert parent.as_dict() == parent_dict


def test_ast():
    ast = AST()
    assert ast.children == []


class TestElement:
    @property
    def elem(self):
        return Element("div", attributes={"id": "test", "hidden": True}, children=[])

    @property
    def nc(self):
        return Element("div", attributes={"id": "test", "hidden": True}, in_pre=True)

    def test_self_closing(self):
        element_nc = self.nc 
    
        with raises(ValueError, match="A self closing element can not pop a child node"):
            element_nc.pop()
        with raises(TypeError, match="_default value must be str, bool, or MISSING"):
            element_nc.get("invalid", 3)
        with raises(ValueError, match="Attribute '.+' not found"):
            element_nc.get("invalid")
        with raises(ValueError, match="A self closing element can not have it's children indexed"):
            element_nc[0]

    def test_dict(self):
        element = self.elem
        el = {
            "type": "element",
            "attributes": {"id": "test", "hidden": True},
            "children": [],
            "tag": "div",
            "decl": False
        }
        assert Element.from_dict(el) == element, "Not a valid element from a dict"
        assert element.as_dict() == el, "Invalid dict from an element"

    def test_tag_path(self):
        element = self.elem 
    
        element.append(Element("div"))
        assert element[0].tag_path == [
            "div",
            "div",
        ]

    def test_get(self):
        element = self.elem 

        assert "id" in element
        assert element["id"] == "test"

        assert element.get("id") == "test"
        assert element.get("invalid", "default") == "default"

    def test_set(self):
        element = self.elem 

        element.attributes["id"] = "test-mod"
        assert element["id"] == "test-mod"

    def test_remove(self):
        element = self.elem 
        element.children.append(Element(""))

        assert element.pop("id") == "test"
        assert element.pop("invalid", "default") == "default"
        assert element.pop() == Element("")

        assert "hidden" in element
        del element["hidden"]
        assert "hidden" not in element

def test_literal():
    literal_text = Literal(LiteralType.Text, "text")
    literal_comment = Literal(LiteralType.Comment, "comment")

    assert literal_text.as_dict() == {
        "type": "literal",
        "name": "text",
        "content": "text",
    }, "Invalid dict produced from as_dict"
    assert literal_comment.as_dict() == {
        "type": "literal",
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
