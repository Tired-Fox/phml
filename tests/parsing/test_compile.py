from data import asts, strings, dicts
from phml import PHMLCore, Compiler, file_types


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
            for line in self.compiler.compile(asts["phml"], file_types.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

        compare = [
            line
            for line in self.core.render(file_types.PHML).split("\n")
            if line not in strings["phml"].split("\n")
        ]
        assert len(compare) == 0

    def test_compile_to_json_str(self):
        """Test the compiled json strings from both
        phml.core.Compiler and phml.PHMLCOre.
        """

        from json import loads

        self.core.ast = asts["phml"]

        assert loads(self.compiler.compile(asts["phml"], file_types.JSON)) == dicts
        assert loads(self.core.render(file_types.JSON)) == dicts

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
        self.core.write(file, file_type=file_types.PHML)

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

    def test_compile_to_json_file(self, tmp_path):
        """Test the compiled json file written by phml.PHMLCore."""
        from json import loads

        self.core.ast = asts["phml"]

        file = tmp_path / "temp.txt"
        self.core.write(file, file_type=file_types.JSON, title="sample title")

        assert loads(file.read_text()) == dicts
