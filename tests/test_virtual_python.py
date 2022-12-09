# VirtualPython
# get_vp_result
# process_vp_blocks

from phml.virtual_python.import_objects import ImportFrom, Import
from phml.virtual_python import VirtualPython, get_vp_result, process_vp_blocks


def test_import_objects():
    imp = Import(["pprint, phml"])
    assert repr(imp) == "Import(modules=[pprint, phml])"

    imp = ImportFrom("phml", ["inspect", "classnames"])
    assert repr(imp) == "ImportFrom(module='phml', names=[inspect, classnames])"


def test_virtual_python():
    vp = VirtualPython("import phml\nmessage='dog'")
    assert repr(vp) == "VP(imports: 1, locals: 2)"


def test_get_vp_result():
    result = get_vp_result("message='2'\nresult=message")
    assert result == "2"
    result = get_vp_result(
        """\
message = ['2', 3]
(void, invalid) = (None, "RED ALERT")
results=message\
"""
    )
    assert result == ['2', 3]

    assert get_vp_result("cow") is None
    assert get_vp_result("cow\nresult=dog") is None


def test_process_vp_blocks():
    vp = VirtualPython()
    result = process_vp_blocks("The {thing} has a {desc}.", vp, thing="cat", desc="big heart")
    assert result == "The cat has a big heart."
    result = process_vp_blocks("The {thing} has a {desc}.", vp, thing="cat", desc="big heart")
    assert result == "The cat has a big heart."


if __name__ == "__main__":
    test_process_vp_blocks()
