from data import asts, strings, dicts
from phml import PHML, Parser
from phml.builder import p
from phml.utilities import parse_component
from phml.core.nodes import AST
from pathlib import Path
from pytest import raises
import re


class TestParse:
    parser = Parser()
    phml = PHML()

    def test_load_phml_file(self):
        """Test the parsed ast of a phml file."""

        self.parser.load("tests/sample.phml")
        self.phml.load("tests/sample.phml")

        assert self.parser.ast == asts["phml"]
        assert self.phml.ast == asts["phml"]

        with raises(
            Exception,
            match=re.escape(
                "'tests/invalid.phml': Unbalanced tags in source file 'tests/invalid.phml' at [3:4]"
            ),
        ):
            self.phml.load("tests/invalid.phml")

        def handler(src) -> AST:
            return AST(p(p("h1", "Hello World!")))

        self.phml.load("tests/sample.phml", handler)
        assert self.phml.ast == AST(p(p("h1", "Hello World!")))

    def test_load_json_file(self):
        """Test the parsed ast of a json file."""

        self.parser.load("tests/sample.json")
        self.phml.load("tests/sample.json")

        assert self.parser.ast == asts["phml"]
        assert self.phml.ast == asts["phml"]

    def test_load_html_file(self):
        """Test the parsed ast of a html file."""

        self.parser.load("tests/sample.html")
        self.phml.load("tests/sample.html")

        assert self.parser.ast == asts["html"]
        assert self.phml.ast == asts["html"]

    def test_parse_phml_str(self):
        """Test the parsed ast of a phml str."""

        self.parser.parse(strings["phml"])
        self.phml.parse(strings["phml"])

        assert self.parser.ast == asts["phml"]
        assert self.phml.ast == asts["phml"]

        with raises(Exception, match=re.escape("<!DOCT...: Unbalanced tags in source at [3:4]")):
            self.phml.parse(
                """\
<!DOCTYPE html>
<html>
    <div>\
"""
            )

        with raises(Exception, match=re.escape("<html>...: <!doctype> must be in the root!")):
            self.phml.parse(
                """\
<html>
    <meta>
    <!DOCTYPE html>
    <div>
    </div>
</html>\
"""
            )

        with raises(Exception, match=r"<html>\.\.\.: Mismatched tags <.+> and </.+> at .+"):
            self.phml.parse(
                """\
<html>
    <meta>
    <!-- multiline
        comment -->
    <span>
        <div>
    </span>
        </div>
</html>\
"""
            )

        def handler(src) -> AST:
            return AST(p(p("h1", "Hello World!")))

        self.phml.parse("tests/sample.phml", handler)
        assert self.phml.ast == AST(p(p("h1", "Hello World!")))

    def test_parse_html_str(self):
        """Test the parsed ast of a html str."""

        self.parser.parse(strings["html"])
        self.phml.parse(strings["html"])

        assert self.parser.ast == asts["html"]
        assert self.phml.ast == asts["html"]

    def test_parse_dict(self):
        """Test the parsed ast of a dict object."""

        self.parser.parse(dicts)
        self.phml.parse(dicts)

        assert self.parser.ast == asts["phml"]
        assert self.phml.ast == asts["phml"]
        
        valid = {
            "type": "element",
            "position": {
                "start": {"line": 1, "column": 1, "offset": None},
                "end": {"line": 1, "column": 1, "offset": None},
                "indent": None,
            },
            "properties": {},
            "tag": "title",
            "startend": False,
            "locals": {},
            "children": [],
        }
        
        invalid_type = {"type": "invalid"}
        no_type = {}
        
        self.phml.parse(valid)
        
        with raises(Exception, match=r"Unkown node type <.+>"):
            self.phml.parse(invalid_type)

        with raises(Exception, match="Invalid json for phml\\. Every node must have a type\\. Nodes may only have the types; root, element, doctype, text, or comment"):
            self.phml.parse(no_type)

    def test_add_components(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.phml.add({"test-cmpt": parse_component(cmpt)})
        assert "test-cmpt" in self.phml.compiler.components
        assert self.phml.compiler.components["test-cmpt"] == {
            "python": [],
            "script": [],
            "style": [],
            "component": p("div", "Hello World!"),
        }

        self.phml.add(Path("tests/component.phml"))
        assert "component" in self.phml.compiler.components

    def test_remove_components(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.phml.add({"test-cmpt": parse_component(cmpt)})
        self.phml.remove("test-cmpt")

        assert "test-cmpt" not in self.phml.compiler.components

    def test_core_init(self):
        cmpt = AST(p(p("div", "Hello World!")))
        self.phml = PHML(["../dir/"], {"test-cmpt": parse_component(cmpt)})
        assert self.phml.scopes == ["../dir/"]
        assert "test-cmpt" in self.phml.compiler.components
        
    def test_imports(self):
        self.phml.ast = AST(p(p("python", "import pprint\nfrom time import time")))
        assert self.phml.render() == "<!DOCTYPE html>"
