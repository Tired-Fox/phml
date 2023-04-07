from pathlib import Path

from pytest import raises
from phml import HypertextManager 
from data import *
from phml.nodes import AST

def construct_base(phml: HypertextManager | None = None):
    if phml is None:
        phml = HypertextManager()
    phml.add("tests/src/component.phml", ignore="tests/src/")
    phml.add("tests/src/sub/component.phml", ignore="tests/src/")
    phml.components["Component"]["hash"] = hashes["Component"]
    phml.components["Sub.Component"]["hash"] = hashes["Sub.Component"]
    return phml

class TestManager:
    def test_parse(self):
        content = Path("tests/src/index.phml").read_text()
        phml = construct_base().parse(content)
        assert phml.ast == phml_ast
        assert phml.load("tests/src/index.phml").ast == phml_ast
    
        assert phml.parse(phml_dict).ast == phml_ast
        assert isinstance(phml.parse(phml_dict["children"][0]).ast, AST)

    def test_parse_exceptions(self):
        with raises(ValueError, match="Must either provide a phml str/dict to parse or use parse in the open context manager"):
            HypertextManager().parse()

    def test_compile(self):
        ast = construct_base().load("tests/src/index.phml").compile(message=message)
        assert ast == html_ast

    def test_compile_exceptions(self):
        with raises(ValueError, match="Must first parse a phml file before compiling to an AST"):
            HypertextManager().compile()

    def test_render(self, tmp_path: Path):
        out = tmp_path / "index.html"
        start = tmp_path / "index.phml"
        
        (tmp_path / "readme.md").write_text(Path("tests/src/readme.md").read_text())

        start.write_text(phml_file, encoding="utf-8")
    
        with HypertextManager.open(start) as phml:
            construct_base(phml)
            phml.render(message=message, _phml_path_="tests/src/")
    
        assert out.read_text() == html_file

    def test_open(self, tmp_path: Path):
        out = tmp_path / "index.html"
        compressed_out = tmp_path / "index-compress.html"

        (tmp_path / "readme.md").write_text(Path("tests/src/readme.md").read_text())
    
        start = tmp_path / "index.phml"
        start.write_text(phml_file, encoding="utf-8")
    
        with HypertextManager.open("tests/src/index.phml", out) as phml:
            construct_base(phml)
            phml.parse()
            data = phml.render(message=message, _phml_path_="tests/src/")
            phml.write(compressed_out, True, message=message)
    
        assert data == html_file
        assert out.read_text() == html_file
    
        assert compressed_out.read_text() == html_file_compressed

    def test_render_exceptions(self):
        with raises(ValueError, match="Must first parse a phml file before rendering a phml AST"):
            HypertextManager().render(_phml_path_="tests/src/")


    def test_format(self, tmp_path: Path):
        file = tmp_path / "index.html"
        file.write_text(html_file, encoding="utf-8")
    
        phml = HypertextManager()
        assert phml.format(code=html_file, compress=True) == html_file_compressed
        phml.format(file=file, compress=True)
        assert file.read_text() == html_file_compressed

    def test_components(self):
        phml = construct_base()
        assert "Component" in phml.components
        phml.remove("Component")
        assert "Component" not in phml.components

    def test_module_file(self):
        phml = construct_base()
        phml.add_module((Path(__file__).parent.parent / "phml/helpers").as_posix())
        assert ".phml.helpers" in phml.imports 

        phml.remove_module(".phml.helpers")
        assert ".phml.helpers" not in phml.imports
    
    def test_module_built_in(self):
        phml = construct_base()
    
        phml.add_module("time", imports=["sleep", "time"])
        phml.add_module("time")

        assert ".time" in phml.imports
        assert ".time" in phml.from_imports
        assert "sleep" in phml.from_imports[".time"] and "time" in phml.from_imports[".time"]

        phml.remove_module("time", imports=["time"])
        assert "time" not in phml.from_imports[".time"]
        phml.remove_module("time", imports=["sleep"])
        assert ".time" not in phml.from_imports
        phml.remove_module("time")
        assert ".time" not in phml.imports

    def test_module_module(self):
        phml = construct_base()
    
        phml.add_module("..phml.builder", imports=["p"])
        phml.add_module("time")
        assert ".phml.builder" in phml.from_imports
        assert "p" in phml.from_imports[".phml.builder"]
    
        phml.remove_module(".phml.builder")
        assert ".phml.builder" not in phml.from_imports

    def test_expose(self):
        phml = construct_base().load("tests/src/index.phml")
        phml.expose({"data": None}, message=message)
        assert "message" in phml.context
        assert "data" in phml.context
        assert phml.render(_phml_path_="tests/src/") == html_file
    

    def test_redact(self):
        phml = construct_base()
        phml.context.update({"data": None, "message": message})

        phml.redact("message", "data")
        assert "message" not in phml.context
        assert "data" not in phml.context

