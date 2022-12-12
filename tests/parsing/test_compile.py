from pathlib import Path
from data import asts, strings
from phml import PHML, Compiler, Formats, Format
from phml.core.compiler import ToML
from phml.core.nodes import AST
from phml.builder import p
from phml.utilities import parse_component
from pytest import raises


class TestCompile:
    compiler = Compiler()
    phml = PHML()

    def test_compile(self, tmp_path):
        """Test the compiled html file written by phml.PHML."""
        # self.phml.ast = asts["phml"]

        assert all(
            L1 == L2
            for L1, L2 in zip(
                self.compiler.compile(asts["phml"], to_format=Formats.PHML).split("\n"),
                strings["phml"].split("\n"),
            )
        )
        
        with raises(Exception, match="Must provide an ast to compile"):
            self.compiler.compile()
            
        self.phml.ast = asts["phml"]
        self.phml.scopes = ["../"]
        assert self.phml.ast == asts["phml"]
        
        assert all(
            L1 == L2
            for L1, L2 in zip(
                self.phml.render(file_type=Formats.PHML).split("\n"),
                strings["phml"].split("\n"),
            )
        )
        
        tmp_file = tmp_path / "output.phml"
        self.phml.write(tmp_file, file_type=Formats.PHML, title="sample title")
        assert all(
            L1 == L2
            for L1, L2 in zip(
                tmp_file.read_text().split("\n"),
                strings["phml"].split("\n"),
            )
        )

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
        self.compiler.add({"component": parse_component(cmpt)}, ("cmpt", parse_component(cmpt)))
        self.phml.add({"component": cmpt}, ("cmpt", cmpt))
        self.phml.add(Path("tests/component.phml"))

        assert "component" in self.compiler.components
        assert "cmpt" in self.compiler.components
        assert "component" in self.phml.compiler.components
        assert "cmpt" in self.phml.compiler.components
        self.compiler.compile(ast=ast)

    def test_remove_component(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.compiler.add({"component": cmpt}, ("cmpt", cmpt))
        self.phml.add(Path("tests/component.phml"), ("cmpt", cmpt))

        with raises(KeyError, match="Invalid component name '.+'"):
            self.compiler.remove("invalid")

        self.compiler.remove(p("div", "Hello World!"))
        assert "component" not in self.compiler.components
        self.compiler.remove("cmpt")
        assert "cmpt" not in self.compiler.components
        
        self.phml.remove(p("div", "Hello World!"))
        assert "cmpt" not in self.phml.compiler.components
        self.phml.remove("component")
        assert "component" not in self.phml.compiler.components

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


def test_to_ml():
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
