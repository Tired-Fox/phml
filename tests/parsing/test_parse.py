from data import asts, strings, dicts
from phml import PHMLCore, Parser


class TestParse:
    parser = Parser()
    core = PHMLCore()

    def test_load_phml_file(self):
        self.parser.load("sample.phml")
        self.core.load("sample.phml")

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_load_json_file(self):
        self.parser.load("sample.json")
        self.core.load("sample.json")

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_load_html_file(self):
        self.parser.load("sample.html")
        self.core.load("sample.html")

        assert self.parser.ast == asts["html"]
        assert self.core.ast == asts["html"]

    def test_parse_phml_str(self):
        self.parser.parse(strings["phml"])
        self.core.parse(strings["phml"])

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]

    def test_parse_html_str(self):
        self.parser.parse(strings["html"])
        self.core.parse(strings["html"])

        assert self.parser.ast == asts["html"]
        assert self.core.ast == asts["html"]

    def test_parse_dict(self):
        self.parser.parse(dicts["phml"])
        self.core.parse(dicts["phml"])

        assert self.parser.ast == asts["phml"]
        assert self.core.ast == asts["phml"]
