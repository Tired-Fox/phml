# Imports used for assert
import time
from re import match, sub
from time import sleep

from pytest import raises

from phml.embedded import *


class TestEmbeddedImports:
    def test_module(self):
        d_time = EmbeddedImport("time").data
        i_time = Module("time").collect()
        
        assert "time" in d_time
        assert d_time["time"] == time
        assert i_time == time

    def test_from_module_str(self):
        EmbeddedImport("re", "match, sub as substitute").data
        d_re = EmbeddedImport("re", "match, sub as substitute").data
        i_match, i_sub = Module("re", imports=["match", "substitute"]).collect()

        assert "match" in d_re
        assert "substitute" in d_re

        assert "match" in d_re
        assert d_re["match"] == match
        assert "substitute" in d_re
        assert d_re["substitute"] == sub 

        assert i_match == match
        assert i_sub == sub

    def test_from_module_list(self):
        
        d_sub_time = EmbeddedImport("time", ["sleep"]).data
        i_sleep = Module("time", imports=["sleep"]).collect()

        assert "sleep" in d_sub_time
        assert d_sub_time["sleep"] == sleep 
        assert i_sleep == sleep

class TestEmbedded:
    def test_context_splitting(self):
        code = """\
from time import sleep

message=True

def get_value():
    return message
"""
    
        embedded = Embedded(code)
        assert len(embedded.imports) == 1 and embedded.imports[0].data == {"sleep": sleep}
        assert "message" in embedded and embedded["message"]
        assert "get_value" in embedded and embedded["get_value"]()

    def test_exec(self):
        early_return = """\
message = True
return message
message = False
"""
        final_assignment = """\
False
message = True
"""

        assert exec_embedded(early_return)
        assert exec_embedded(final_assignment)

    def test_blocks(self):
        bracket_in_block = """{{ {'result': True} }}"""
        assert exec_embedded_blocks(bracket_in_block) == "{'result': True}"


    def test_embedded_exception(self):
        with raises(EmbeddedPythonException):
            Embedded("raise Exception('Test')")

        try:
            Embedded("raise Exception('Test')")
        except EmbeddedPythonException as epe:
            assert len(str(epe)) > 0

