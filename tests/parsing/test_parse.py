from data import asts, strings, dicts
from phml.core import AST, PHML, Parser, Formats
from phml.builder import p
from phml.utilities import parse_component

from pytest import raises


class TestParse:
    parser = Parser()
    phml = PHML()

    def test_parse(self):
        assert self.phml.parse(strings["phml"], from_format=Formats.PHML).ast == asts["phml"]
        assert self.phml.load("tests/sample.phml").ast == asts["phml"]

        assert self.parser.parse("<meta year='2022'>").ast == AST(p(p("meta", {"year": "2022"})))

        assert self.parser.parse("<!--multi\nline-->", from_format=Formats.PHML).ast == AST(
            p(p("comment", "multi\nline"))
        )
        with raises(Exception, match="Mismatched tags .+ at .+"):
            self.parser.parse("<div></main>")
            
        assert self.parser.load("tests/sample.phml", from_format=Formats.PHML).ast == asts["phml"]
        
        with raises(Exception, match="Could not parse unknown filetype .+"):
            self.parser.load("invalid.txt")
            
        assert self.parser.parse(dicts).ast == asts["phml"]

    def core_init(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.phml = PHML(["../dir/"], {"test-cmpt": parse_component(cmpt)})
        assert self.phml._scopes == ["../dir/"]
        assert "test-cmpt" in self.phml._compiler.components

    def imports(self):
        self.phml.ast = AST(p(p("python", "import pprint\nfrom time import time")))
        assert self.phml.render() == "<!DOCTYPE html>"
