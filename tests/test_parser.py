from pytest import raises
from phml.parser import HypertextMarkupParser
from phml import HypertextManager
from data import *

def test_parse():
    parser = HypertextMarkupParser()
    ast = parser.parse(phml_file)
    assert ast == phml_ast, "Invalid parsed AST"
