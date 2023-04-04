from pathlib import Path
from typing import Any

from pytest import raises
from phml.components import *
from phml.nodes import MISSING, Element, Literal, AST, Missing


def test_tokenize_name():
    # Test args and the corresponding outputs
    assert tokenize_name("AWS_com") == ["AWS", "com"]
    assert tokenize_name("AWS_com", normalize=True) == ["aws", "com"]
    assert tokenize_name("AWS_com", title_case=True) == ["AWS", "Com"]
    assert tokenize_name("AWS_com", normalize=True, title_case=True) == ["Aws", "Com"]

    # Test the regex for finding tokens
    # (\b|[A-Z]|_|-|\.)([a-z]+)|([0-9]+)|([A-Z]+)(?=[^a-z])
    # [space, caps, digits, _, -, .] are seperators
    # All caps and all digits are blocks.
    # _-. and ' ' next to eachother combine to one seperator
    assert tokenize_name("today -_is_going-to.beA10OUTOf10", normalize=True) == [
        "today",
        "is",
        "going",
        "to",
        "be",
        "a",
        "10",
        "out",
        "of",
        "10",
    ]

    assert tokenize_name(
        "sub/component/directory", normalize=True, title_case=True
    ) == ["Sub", "Component", "Directory"]

def test_component_manage():
    components = ComponentManager()

    components.add("tests/src/component.phml", ignore="tests/src/")
    assert "Component" in components
    component = components["Component"]
    assert len(component["styles"]) == 2
    assert len(component["scripts"]) == 1
    assert len(component["elements"]) == 1
    assert component["hash"].startswith("Component~") and len(component["hash"]) > 10
    
    components.remove("Component")
    assert "Component" not in components

    with Path("tests/src/component.phml").open("r", encoding="utf-8") as file:
        file_data = file.read()

    components.add(name="Component", data=file_data)
    assert "Component" in components
    components.remove("Component")

    parsed_cmpt = components.parse(file_data)
    components.add(name="Component", data=parsed_cmpt)
    assert "Component" in components

    components.add(name="MultiRoot", data="""\
Some root literal
<p>Element</p>
""")
    assert "MultiRoot" in components

def test_component_parse_exceptions():
    with raises(ValueError, match="Must have at least one root element in component"):
        components = ComponentManager()
        components.parse("""""")

def test_component_add_exceptions():
    components = ComponentManager()
    with raises(ValueError, match="Expected both 'name' and 'data' kwargs to be used together"):
        components.add(data="")

    with raises(ValueError, match="Expected component data to be a string of length longer that 0"):
        components.add(name="", data="")

    with raises(ValueError, match="Expected component data to be a string or a ComponentType dict"):
        components.add(name="Component", data=None)

def test_component_remove_exceptions():
    components = ComponentManager()
    # remove a component not in manager 
    with raises(KeyError, match=".+ is not a known component"):
        components.remove("invalid")

def build_cmpt(
    hash: str= "",
    props: dict[str, Any] | None | Missing = MISSING,
    context: dict[str, Any] | None | Missing = MISSING,
    scripts: list | None | Missing = MISSING,
    styles: list | None | Missing = MISSING,
    elements: list | None | Missing = MISSING
) -> ComponentType:
    return {
        "hash": "" if hash == MISSING else hash,
        "props": {} if props == MISSING else props,
        "context": {} if context == MISSING else context,
        "scripts": [] if scripts == MISSING else scripts,
        "styles": [] if styles == MISSING else styles,
        "elements": [Element("input")] if elements == MISSING else elements
    }
def test_component_validate_exceptions():
    components = ComponentManager()
    # Props not a dict
    with raises(ValueError, match="Expected ComponentType 'props' that is a dict of str to any value"):
        components.validate(build_cmpt(props=None))

    # context not a dict
    with raises(ValueError, match="Expected ComponentType 'context' that is a dict of str to any value"):
        components.validate(build_cmpt(context=None))
        
    # scripts and style must be lists cotaining elements. Elements must have corresponding tags
    #   and one child that is a text literal
    with raises(ValueError, match="Expected ComponentType 'styles' that is a list of phml elements with a tag of 'style'"):
        components.validate(build_cmpt(styles=None))
    with raises(ValueError, match="Expected ComponentType 'styles' that is a list of phml elements with a tag of 'style'"):
        components.validate(build_cmpt(styles=[Element("div")]))

    with raises(ValueError, match="Expected ComponentType 'script' that is alist of phml elements with a tag of 'script'"):
        components.validate(build_cmpt(scripts=None))
    with raises(ValueError, match="Expected ComponentType 'script' that is alist of phml elements with a tag of 'script'"):
        components.validate(build_cmpt(scripts=[Element("div")]))

    # Elements must be a list of Elements or Literals
    with raises(ValueError, match="Expected ComponentType 'elements' to be a list of at least one Element or Literal"):
        components.validate(build_cmpt(elements=None))
    with raises(ValueError, match="Expected ComponentType 'elements' to be a list of at least one Element or Literal"):
        components.validate(build_cmpt(elements=[]))
    with raises(ValueError, match="Expected ComponentType 'elements' to be a list of at least one Element or Literal"):
        components.validate(build_cmpt(elements=[AST()]))
