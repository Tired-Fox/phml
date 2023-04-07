from pytest import raises
from phml.utilities.misc import *
from util_data import *
from phml import p

class TestMisc:
    def test_depth(self):
        assert depth(dest) == 3

    def test_size(self):
        assert size(ast) == 14

def test_heading_rank():
    assert heading_rank(p("h1")) == 1

    with raises(TypeError, match="Node must be a heading\\. Was a .+\\..+"):
        heading_rank(p("h10"))

class TestClasses:
    def test_classnames(self):
        node = p("div", {"class": "rounded"})
        classnames(node, "red", {"shadow": True}, ["underline", "bold", 3])
        assert node["class"] == "rounded red shadow underline bold 3"

        with raises(TypeError, match="Unkown conditional statement: .+"):
            classnames(p("div"), None)

        with raises(TypeError, match="Node must be an element"):
            classnames(None, "red")

    def test_class_list(self):
        node = p("div", {"class": "red"})
        class_list = ClassList(node)

        assert "red" in class_list

        class_list.add("underline", "bold")
        assert "underline" in class_list and "bold" in class_list
        assert node["class"] == "red underline bold"

        class_list.remove("bold", "red")
        assert "bold" not in class_list and "red" not in class_list
        assert node["class"] == "underline"

        class_list.replace("underline", "shadow")
        assert "underline" not in class_list and "shadow" in class_list
        assert node["class"] == "shadow"

        class_list.toggle("shadow")
        assert "shadow" not in class_list
        assert node["class"] == ""

        class_list.remove("shadow")
        assert "class" not in node

        class_list.toggle("shadow")
        assert "shadow" in class_list
        assert node["class"] == "shadow"

        class_list.add("underline", "red")
        assert class_list.classes == "shadow underline red"
        assert node["class"] == "shadow underline red"

