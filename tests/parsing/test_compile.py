from data import asts, strings, dicts
from phml import PHML, Compiler, Formats, Format
from phml.core.compiler import ToML
from phml.core.nodes import AST, Element, Point, Position
from phml.builder import p
from phml.utilities import parse_component
from pytest import raises


def to_ml():
    with raises(
        Exception,
        match="Converting to a file format requires that an ast is provided",
    ):
        ToML().compile()

    with raises(
        Exception,
        match="Doctypes must be in the root of the file/tree",
    ):
        ToML().compile(AST(p(p("div", p("doctype")))))
        
class TestCompile:
    compiler = Compiler()
    phml = PHML()

    def compile_to_phml_str(self):
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

    def compile_to_html_file(self, tmp_path):
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

    def add_component(self):
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
            p(
                p(
                    "main",
                    p(
                        "cmpt",
                        {
                            "@if": "True",
                            ":title": "'Today'",
                            "message": "{'Today'}",
                            "data-info": "info",
                        },
                        "Sunny Day",
                    ),
                )
            )
        )

        self.compiler.add({"component": cmpt}, ("cmpt", cmpt))
        self.compiler.add({"component": parse_component(cmpt)})

        assert "component" in self.compiler.components
        assert "cmpt" in self.compiler.components
        self.compiler.compile(ast=ast)

    def remove_component(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.compiler.add({"component": cmpt}, ("cmpt", cmpt))

        with raises(KeyError, match="Invalid component name .+"):
            self.compiler.remove("invalid")

        self.compiler.remove(p("div", "Hello World!"))
        assert "component" not in self.compiler.components

    def scopes(self, tmp_path):
        self.phml.ast = AST(p(p("div")))
        self.phml.scopes = ["../dir/"]
        self.phml.render(scopes=["./"])
        file = tmp_path / "temp.txt"
        self.phml.write(file, scopes=["./"])

    def compiler_no_ast_or_doctype(self):
        self.compiler.ast = None
        with raises(Exception, match="Must provide an ast to compile."):
            self.compiler.compile()

        self.compiler.ast = AST(p(p("h1", "Markdown String")))
        with raises(Exception, match="Base class Format's compile method should never be called"):
            self.compiler.compile(to_format=Format)
