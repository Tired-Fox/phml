from data import asts, strings, dicts
from phml import PHMLCore, Parser


class TestParse:
    parser = Parser()
    core = PHMLCore()

    def test_load_phml_file(self):
        """Test the parsed ast of a phml file."""
        
        self.parser.load("tests/sample.phml")
        self.core.load("tests/sample.phml")
        
        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_load_json_file(self):
        """Test the parsed ast of a json file."""
        
        self.parser.load("tests/sample.json")
        self.core.load("tests/sample.json")

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_load_html_file(self):
        """Test the parsed ast of a html file."""
        
        self.parser.load("tests/sample.html")
        self.core.load("tests/sample.html")

        assert self.parser.ast == asts["html"]
        assert self.core.ast == asts["html"]

    def test_parse_phml_str(self):
        """Test the parsed ast of a phml str."""
        
        self.parser.parse(strings["phml"])
        self.core.parse(strings["phml"])

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_parse_html_str(self):
        """Test the parsed ast of a html str."""
        
        self.parser.parse(strings["html"])
        self.core.parse(strings["html"])

        assert self.parser.ast == asts["html"]
        assert self.core.ast == asts["html"]

    def test_parse_dict(self):
        """Test the parsed ast of a dict object."""
        
        self.parser.parse(dicts)
        self.core.parse(dicts)

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]