from data import asts, strings, dicts
from phml import PHMLCore, Compiler, file_types


class TestCompile:
    compiler = Compiler()
    core = PHMLCore()

    def test_compile_to_phml(self):
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

    def test_compile_to_json(self):
        from json import loads

        self.core.ast = asts["phml"]


        assert loads(self.compiler.compile(asts["phml"], file_types.JSON)) == dicts["phml"]
        assert loads(self.core.render(file_types.JSON)) == dicts["phml"]
        
    def test_compile_to_html(self):
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
