from data import asts, strings, dicts
from phml import PHMLCore, Compiler, Formats
from phml.nodes import AST, Element, Point, Position
from phml.builder import p
from phml.utils import parse_component
from pytest import raises
import re


class TestCompile:
    compiler = Compiler()
    core = PHMLCore()

    def test_compile_to_phml_str(self):
        """Test the compiled phml strings from both
        phml.core.Compiler and phml.PHMLCOre.
        """

        self.core.ast = asts["phml"]

        compare = [
            line
            for line in self.compiler.compile(asts["phml"], Formats.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

        compare = [
            line
            for line in self.core.render(Formats.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_json_str(self):
        """Test the compiled json strings from both
        phml.core.Compiler and phml.PHMLCOre.
        """

        from json import loads

        self.core.ast = asts["phml"]

        assert loads(self.compiler.compile(asts["phml"], Formats.JSON)) == dicts
        assert loads(self.core.render(Formats.JSON)) == dicts

        with raises(Exception, match="Root nodes must only occur as the root of an ast/tree."):
            self.compiler.compile(
                ast=AST(
                    p(
                        p(
                            "div",
                            Element("div", Position(Point(0, 1), Point(2, 3))),
                            p(),
                        )
                    )
                ),
                to_format=Formats.JSON,
            )

    def test_compile_to_html_str(self):
        """Test the compiled html strings from both
        phml.core.Compiler and phml.PHMLCOre.
        """

        self.core.ast = asts["phml"]

        compare = [
            line
            for line in self.compiler.compile(asts["phml"], title="sample title").split("\n")
            if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

        compare = [
            line
            for line in self.core.render(title="sample title").split("\n")
            if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_phml_file(self, tmp_path):
        """Test the compiled phml file written by phml.PHMLCore."""

        self.core.ast = asts["phml"]

        file = tmp_path / "core.txt"
        self.core.write(file, file_type=Formats.PHML)

        compare = [
            line for line in file.read_text().split("\n") if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_html_file(self, tmp_path):
        """Test the compiled html file written by phml.PHMLCore."""

        self.core.ast = asts["phml"]

        file = tmp_path / "temp.txt"
        self.core.write(file, title="sample title")

        compare = [
            line for line in file.read_text().split("\n") if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

        # Exceptions
        self.core.ast = AST(p(p("div", {"@else": "True"})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.\n.+",
        ):
            self.core.render()

        self.core.ast = AST(p(p("div", {"@else": "True", "@elif": "False"})))
        with raises(
            Exception, match=r"There can only be one python condition statement at a time:\n.+"
        ):
            self.core.render()

        self.core.ast = AST(p(p("div", {"@if": "False"})))
        assert self.core.render() == "<!DOCTYPE html>"

        self.core.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@elif": "True"})))
        assert self.core.render() == "<!DOCTYPE html>\n<div />"

        self.core.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@elif": "False"})))
        assert self.core.render() == "<!DOCTYPE html>"

        self.core.ast = AST(p(p("div", {"@for": "i in range(1)"}), p("div", {"@elif": "False"})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.+",
        ):
            self.core.render()

        self.core.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@else": True})))
        assert self.core.render() == "<!DOCTYPE html>\n<div />"

        self.core.ast = AST(p(p("div", {"@for": "i in range(1)"}), p("div", {"@else": True})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.+",
        ):
            self.core.render()

    def test_compile_to_json_file(self, tmp_path):
        """Test the compiled json file written by phml.PHMLCore."""
        from json import loads

        self.core.ast = asts["phml"]

        file = tmp_path / "temp.txt"
        self.core.write(file, file_type=Formats.JSON, title="sample title")

        assert loads(file.read_text()) == dicts

    def test_add_component(self):
        cmpt = AST(
            p(
                p(
                    "div",
                    {
                        "title": "{title}",
                        "py-aria-label": "message",
                    },
                    p("slot"),
                    "Hello World!",
                ),
                p("python", "message = 'test'"),
            )
        )
        ast = AST(
            p(p("main", p("cmpt", {"@if": "True", ":title": "'Today'", "message": "{'Today'}", "data-info": "info"}, "Sunny Day")))
        )

        self.compiler.add({"component": cmpt}, ("cmpt", cmpt))
        self.compiler.add({"component": parse_component(cmpt)})

        assert "component" in self.compiler.components
        assert "cmpt" in self.compiler.components
        self.compiler.compile(ast=ast)

    def test_remove_component(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.compiler.add({"component": cmpt}, ("cmpt", cmpt))

        with raises(KeyError, match="Invalid component name .+"):
            self.compiler.remove("invalid")

        self.compiler.remove(p("div", "Hello World!"))
        assert "component" not in self.compiler.components

    def test_scopes(self, tmp_path):
        self.core.scopes = ["../dir/"]
        self.core.render(scopes=["./"])
        file = tmp_path / "temp.txt"
        self.core.write(file, scopes=["./"])

    def test_compiler_no_ast_or_doctype(self):
        self.compiler.ast = None
        with raises(Exception, match="Must provide an ast to compile."):
            self.compiler.compile()

        self.compiler.ast = AST(p(p("html")))
        with raises(Exception, match=r"Unkown format < .+ >"):
            self.compiler.compile(to_format="markdown")

        def handler(*args, **kwargs):
            return "# Markdown String"

        assert self.compiler.compile(to_format="markdown", handler=handler) == "# Markdown String"
