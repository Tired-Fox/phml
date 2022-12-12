from data import asts, strings, dicts
from phml import PHML, Compiler, Formats
from phml.core.nodes import AST, Element, Point, Position
from phml.builder import p
from phml.utilities import parse_component
from pytest import raises


class TestCompile:
    compiler = Compiler()
    phml = PHML()

    def test_compile_to_phml_str(self):
        """Test the compiled phml strings from both
        phml.core.Compiler and phml.PHML.
        """

        self.phml.ast = asts["phml"]

        compare = [
            line
            for line in self.compiler.compile(asts["phml"], Formats.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

        compare = [
            line
            for line in self.phml.render(Formats.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_json_str(self):
        """Test the compiled json strings from both
        phml.core.Compiler and phml.PHML.
        """

        from json import loads

        self.phml.ast = asts["phml"]

        assert loads(self.compiler.compile(asts["phml"], Formats.JSON)) == dicts
        assert loads(self.phml.render(Formats.JSON)) == dicts

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
        phml.core.Compiler and phml.PHML.
        """

        self.phml.ast = asts["phml"]

        compare = [
            line
            for line in self.compiler.compile(asts["phml"], title="sample title").split("\n")
            if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

        compare = [
            line
            for line in self.phml.render(title="sample title").split("\n")
            if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_phml_file(self, tmp_path):
        """Test the compiled phml file written by phml.PHML."""

        self.phml.ast = asts["phml"]

        file = tmp_path / "core.txt"
        self.phml.write(file, file_type=Formats.PHML)

        compare = [
            line for line in file.read_text().split("\n") if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_html_file(self, tmp_path):
        """Test the compiled html file written by phml.PHML."""

        self.phml.ast = asts["phml"]

        file = tmp_path / "temp.txt"
        self.phml.write(file, title="sample title")

        compare = [
            line for line in file.read_text().split("\n") if line not in strings["html"].split("\n")
        ]
        assert len(compare) == 0

        # Exceptions
        self.phml.ast = AST(p(p("div", {"@else": "True"})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.\n.+",
        ):
            self.phml.render()

        self.phml.ast = AST(p(p("div", {"@else": "True", "@elif": "False"})))
        with raises(
            Exception, match=r"There can only be one python condition statement at a time:\n.+"
        ):
            self.phml.render()

        self.phml.ast = AST(p(p("div", {"@if": "False"})))
        assert self.phml.render() == "<!DOCTYPE html>"

        self.phml.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@elif": "True"})))
        assert self.phml.render() == "<!DOCTYPE html>\n<div />"

        self.phml.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@elif": "False"})))
        assert self.phml.render() == "<!DOCTYPE html>"

        self.phml.ast = AST(p(p("div", {"@for": "i in range(1)"}), p("div", {"@elif": "False"})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.+",
        ):
            self.phml.render()

        self.phml.ast = AST(p(p("div", {"@if": "False"}), p("div", {"@else": True})))
        assert self.phml.render() == "<!DOCTYPE html>\n<div />"

        self.phml.ast = AST(p(p("div", {"@for": "i in range(1)"}), p("div", {"@else": True})))
        with raises(
            Exception,
            match=r"Condition statements that are not py-if or py-for must have py-if or py-elif as a prevous sibling.+",
        ):
            self.phml.render()

    def test_compile_to_json_file(self, tmp_path):
        """Test the compiled json file written by phml.PHML."""
        from json import loads

        self.phml.ast = asts["phml"]

        file = tmp_path / "temp.txt"
        self.phml.write(file, file_type=Formats.JSON, title="sample title")

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
        self.phml.scopes = ["../dir/"]
        self.phml.render(scopes=["./"])
        file = tmp_path / "temp.txt"
        self.phml.write(file, scopes=["./"])

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
