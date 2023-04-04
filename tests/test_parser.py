from pytest import raises
from phml.nodes import inspect
from phml.parser import HypertextMarkupParser
from data import *

class TestHyperTextParser:
    parser = HypertextMarkupParser()

    def test_parse(self):
        ast = self.parser.parse(phml_file)
        assert ast == phml_ast, "Invalid parsed AST"

    def test_parse_raise_parse_tag(self):
        with raises(Exception, match="Comment was not closed"):
            self.parser.parse("<!-- some comment\n<div>Next Element</div>")

        with raises(Exception, match="Expected tag .+ to be closed with symbol '>'. Was not closed."):
            self.parser.parse("<div")

        with raises(Exception, match="Closing tag .+ was not closed, maybe it is missing a '>' symbol"):
            self.parser.parse("<div>Some text </div<div>Next Element</div>")

    def test_parse_raise_parse(self):
        with raises(Exception, match="Unbalanced tags: .+ \\| .+ at .+"):
            self.parser.parse("<div>element<p>para</div></p>")

        with raises(Exception, match="The following tags where expected to be closed: .+"):
            self.parser.parse("<div><p><span>")

        with raises(Exception, match="Unbalanced tags: Tag was closed without first being opened at .+"):
            self.parser.parse("</div>")
