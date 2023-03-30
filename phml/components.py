from re import finditer
from pathlib import Path
from time import time
from typing import Any, Iterator, TypedDict

from .nodes import Element, Literal, LiteralType
from .helpers import iterate_nodes
from .parser import HypertextMarkupParser
from .embedded import Embedded

__all__ = ["ComponentType", "ComponentManager"]


class ComponentType(TypedDict):
    hash: int
    props: dict[str, Any]
    context: dict[str, Any]
    scripts: list[Element]
    styles: list[Element]
    element: Element

class ComponentCacheType(TypedDict):
    hash: int
    scripts: list[Element]
    styles: list[Element]


DEFAULT_COMPONENT: ComponentType = {
    "hash": 0,
    "props": {},
    "context": {},
    "scripts": [],
    "styles": [],
    "element": Element(""),
}


def tokenize_name(
    name: str, *, normalize: bool = True, title_case: bool = False
) -> list[str]:
    """Generates name tokens `some name tokanized` from a filename.
    Assumes filenames is one of:
    * snakecase - some_file_name
    * camel case - someFileName
    * pascal case - SomeFileName

    Args:
        name (str): File name without extension
        normalize (bool): Make all tokens fully lowercase. Defaults to True

    Returns:
        list[str]: List of word tokens.
    """
    tokens = []
    for token in finditer(
        r"(\b|[A-Z]|_|-|\.)([a-z]+)|([0-9]+)|([A-Z]+)(?=[^a-z])", name
    ):
        first, rest, nums, cap = token.groups()

        if first is not None and first.isupper():
            # First char was capitalized. Append it to full token capture
            rest = first + rest
        elif cap is not None and cap.isupper():
            # Token is all caps. Set to full capture
            rest = cap
        elif nums is not None and nums.isnumeric():
            # Token is all numbers. Set to full capture
            rest = str(nums)

        if normalize:
            rest = rest.lower()

        if title_case:
            rest = rest[0].upper() + rest[1:]

        tokens.append(rest)
    return tokens


def _parse_cmpt_name(name: str) -> str:
    tokens = tokenize_name(name.rsplit(".", 1)[0], normalize=True, title_case=True)
    return "".join(tokens)


def hash_component(cmpt: ComponentType):
    """Hash a component for applying unique scope identifier"""
    return (
        hash(cmpt["element"])
        + sum(hash(style) for style in cmpt["styles"])
        + sum(hash(script) for script in cmpt["scripts"])
        + sum(hash(name) for name in cmpt["element"].attributes)
        - int(str(time())[-5:])
    )


class ComponentManager:
    components: dict[str, ComponentType]

    def __init__(self) -> None:
        self.components = {}
        self._parser = HypertextMarkupParser()
        self._cache: dict[str, ComponentCacheType] = {}

    def generate_name(self, path: str, ignore: str = "") -> str:
        """Generate a component name based on it's path. Optionally strip part of the path
        from the beginning.
        """

        path = Path(path).as_posix().lstrip(Path(ignore).as_posix()).lstrip("/")
        parts = path.split("/")

        return ".".join(
            [
                *[part[0].upper() + part[1:].lower() for part in parts[:-1]],
                _parse_cmpt_name(parts[-1]),
            ]
        )

    def get_cache(self) -> dict[str, ComponentCacheType]:
        """Get the current cache of component scripts and styles"""
        return self._cache

    def cache(self, key: str, value: ComponentType):
        """Add a cache for a specific component. Will only add the cache if
        the component is new and unique.
        """
        if key not in self._cache:
            self._cache[key] = {
                "hash": value["hash"],
                "scripts": value["scripts"],
                "styles": value["styles"],
            }

    def parse(self, content: str, path: str = "") -> ComponentType:
        ast = self._parser.parse(content)

        component: ComponentType = {**DEFAULT_COMPONENT}
        element = None
        context = Embedded("", path)

        for node in iterate_nodes(ast):
            if isinstance(node, Element) and node.tag == "python":
                context += Embedded(node, path)
                if node.parent is not None:
                    node.parent.remove(node)

        for node in ast:
            if isinstance(node, Element):
                if node.tag == "script" and len(node) == 1 and Literal.is_text(node[0]):
                    component["scripts"].append(node)
                elif node.tag == "style" and len(node) == 1 and Literal.is_text(node[0]):
                    component["styles"].append(node)
                else:
                    if element is not None:
                        raise ValueError(
                            "Can not have more than one root element in components"
                        )

                    if node.tag == "For":
                        raise ValueError(
                            "Can not use 'For' tag for root component element"
                        )
                    element = node

        component["props"] = context.context.pop("Props", {})
        component["context"] = context.context
        if element is None:
            raise ValueError("Must have one root element in component")
        component["element"] = element
        component["hash"] = hash_component(component)

        return component

    def add(
        self,
        file: str | None = None,
        *,
        cmpt: tuple[str, str] | None = None,
        data: tuple[str, ComponentType] | None = None,
        ignore: str = "",
    ):
        """Add a component to the component manager.

        Args:
            file (str | None): Path to the component to be added. Pair with `ignore`
                to ignore part of the parent path.

        Optional Kwargs:
            cmpt (tuple[str, str]): Tuple of the component name and component str to parse.
                The first str is kept as is for the name and the seconds str is parsed as a
                component.
            data (tuple[str, ComponentType]): Tuple of the component name and the already parsed
                components. The str is kept as is for the name and the ComponentType, dict, is kept
                as is for the component data.
        """

        content: ComponentType = {**DEFAULT_COMPONENT}
        if file is None:
            if cmpt is not None and cmpt != "":
                if (
                    not isinstance(cmpt, tuple)
                    or len(cmpt) != 2
                    or not isinstance(cmpt[0], str)
                    or not isinstance(cmpt[1], str)
                ):
                    raise TypeError("Expected component tuple (<name:str>, <cmpt:str>)")
                name = cmpt[0]
                content.update(self.parse(cmpt[1], "_cmpt_"))
            elif data is not None:
                if (
                    not isinstance(data, tuple)
                    or len(data) != 2
                    or not isinstance(data[0], str)
                    or not isinstance(data[1], dict)
                ):
                    raise TypeError(
                        "Expected data tuple (<name:str>, <data:ComponentType>)"
                    )

                name = data[0]
                content.update(data[1])
            else:
                raise ValueError(
                    "Expected a string, file path, or a pre parsed component"
                )
        else:
            with Path(file).open("r", encoding="utf-8") as c_file:
                name = self.generate_name(file, ignore)
                content.update(self.parse(c_file.read(), file))

        self.validate(content)
        self.components[name] = content

    def __iter__(self) -> Iterator[tuple[str, ComponentType]]:
        yield from self.components.items()

    def keys(self) -> Iterator[str]:
        yield from self.components.keys()

    def values(self) -> Iterator[ComponentType]:
        yield from self.components.values()

    def __contains__(self, key: str) -> bool:
        return key in self.components

    def __getitem__(self, key: str) -> ComponentType:
        return self.components[key]

    def __setitem__(self, key: str, value: ComponentType):
        # TODO: Custom error
        raise Exception("Cannot set components from slice assignment")

    def remove(self, key: str):
        """Remove a comopnent from the manager with a specific tag/name."""
        if key not in self.components:
            raise KeyError(f"{key} is not a known component")
        del self.components[key]

    def validate(self, data: ComponentType):
        if "props" not in data or not isinstance(data["props"], dict):
            raise ValueError(
                "Expected ComponentType 'props' that is a dict of str to any value"
            )

        if "context" not in data or not isinstance(data["context"], dict):
            raise ValueError(
                "Expected ComponentType 'context' that is a dict of str to any value"
            )

        if (
            "scripts" not in data
            or not isinstance(data["scripts"], list)
            or not all(
                isinstance(script, Element) and script.tag == "script"
                for script in data["scripts"]
            )
        ):
            raise ValueError(
                "Expected ComponentType 'script' that is alist of phml elements with a tag of 'script'"
            )

        if (
            "styles" not in data
            or not isinstance(data["styles"], list)
            or not all(
                isinstance(style, Element) and style.tag == "style"
                for style in data["styles"]
            )
        ):
            raise ValueError(
                "Expected ComponentType 'styles' that is a list of phml elements with a tag of 'style'"
            )

        if "element" not in data or not isinstance(data["element"], Element):
            raise ValueError(
                "Expected ComponentType 'element' that is single phml element"
            )

