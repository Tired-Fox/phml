import os
from pathlib import Path
from re import finditer
from time import time
from typing import Any, Iterator, TypedDict, overload

from .embedded import Embedded
from .helpers import iterate_nodes
from .nodes import Element, Literal
from .parser import HypertextMarkupParser

__all__ = ["ComponentType", "ComponentManager", "tokenize_name", "parse_cmpt_name"]


class ComponentType(TypedDict):
    hash: str
    props: dict[str, Any]
    context: dict[str, Any]
    scripts: list[Element]
    styles: list[Element]
    elements: list[Element | Literal]


class ComponentCacheType(TypedDict):
    hash: str
    scripts: list[Element]
    styles: list[Element]


def DEFAULT_COMPONENT() -> ComponentType:
    return {
        "hash": "",
        "props": {},
        "context": {},
        "scripts": [],
        "styles": [],
        "elements": [],
    }


def tokenize_name(
    name: str,
    *,
    normalize: bool = False,
    title_case: bool = False,
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
        r"([A-Z])?([a-z]+)|([0-9]+)|([A-Z]+)(?=[^a-z])",
        name.strip(),
    ):
        first, rest, nums, cap = token.groups()

        result = ""
        if rest is not None:
            result = (first or "") + rest
        elif cap is not None:
            # Token is all caps. Set to full capture
            result = cap
        elif nums is not None:
            # Token is all numbers. Set to full capture
            result = str(nums)

        if normalize:
            result = result.lower()

        if len(result) > 0:
            if title_case:
                result = result[0].upper() + result[1:]
            tokens.append(result)
    return tokens


def parse_cmpt_name(name: str) -> str:
    tokens = tokenize_name(name.rsplit(".", 1)[0], normalize=True, title_case=True)
    return "".join(tokens)


def hash_component(cmpt: ComponentType):
    """Hash a component for applying unique scope identifier"""
    return (
        sum(hash(element) for element in cmpt["elements"])
        + sum(hash(style) for style in cmpt["styles"])
        + sum(hash(script) for script in cmpt["scripts"])
        - int(time() % 1000)
    )


class ComponentManager:
    components: dict[str, ComponentType]

    def __init__(self) -> None:
        self.components = {}
        self._parser = HypertextMarkupParser()
        self._cache: dict[str, ComponentCacheType] = {}

    @staticmethod
    def generate_name(path: str, ignore: str = "") -> str:
        """Generate a component name based on it's path. Optionally strip part of the path
        from the beginning.
        """

        path = Path(os.path.relpath(path, ignore)).as_posix()
        parts = path.split("/")

        return ".".join(
            [
                *[part[0].upper() + part[1:].lower() for part in parts[:-1]],
                parse_cmpt_name(parts[-1]),
            ],
        )

    def get_cache(self) -> dict[str, ComponentCacheType]:
        """Get the current cache of component scripts and styles"""
        return self._cache

    def clear_cache(self):
        """Clear the cached component data."""
        self._cache = {}

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

        component: ComponentType = DEFAULT_COMPONENT()
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
                elif (
                    node.tag == "style" and len(node) == 1 and Literal.is_text(node[0])
                ):
                    component["styles"].append(node)
                else:
                    component["elements"].append(node)
            elif isinstance(node, Literal):
                component["elements"].append(node)

        component["props"] = context.context.pop("Props", {})
        component["context"] = context.context
        if len(component["elements"]) == 0:
            raise ValueError("Must have at least one root element in component")
        component["hash"] = f"~{hash_component(component)}"

        return component

    @overload
    def add(self, file: str | Path, *, name: str|None = None, ignore: str = ""):
        """Add a component to the component manager with a file path. Also, componetes can be added to
        the component manager with a name and str or an already parsed component dict.

        Args:
            file (str): The file path to the component.
            ignore (str): The path prefix to remove before creating the comopnent name.
            name (str): The name of the component. This is the index/key in the component manager.
                This is also the name of the element in phml. Ex: `Some.Component` == `<Some.Component />`
            data (str | ComponentType): This is the data that is assigned in the manager. It can be a string
                representation of the component, or an already parsed component type dict.
        """
        ...

    @overload
    def add(self, *, name: str, data: str | ComponentType):
        """Add a component to the component manager with a file path. Also, componetes can be added to
        the component manager with a name and str or an already parsed component dict.

        Args:
            file (str): The file path to the component.
            ignore (str): The path prefix to remove before creating the comopnent name.
            name (str): The name of the component. This is the index/key in the component manager.
                This is also the name of the element in phml. Ex: `Some.Component` == `<Some.Component />`
            data (str | ComponentType): This is the data that is assigned in the manager. It can be a string
                representation of the component, or an already parsed component type dict.
        """
        ...

    def add(
        self,
        file: str | Path | None = None,
        *,
        name: str | None = None,
        data: str | ComponentType | None = None,
        ignore: str = "",
    ):
        """Add a component to the component manager with a file path. Also, componetes can be added to
        the component manager with a name and str or an already parsed component dict.

        Args:
            file (str): The file path to the component.
            ignore (str): The path prefix to remove before creating the comopnent name.
            name (str): The name of the component. This is the index/key in the component manager.
                This is also the name of the element in phml. Ex: `Some.Component` == `<Some.Component />`
            data (str | ComponentType): This is the data that is assigned in the manager. It can be a string
                representation of the component, or an already parsed component type dict.
        """
        content: ComponentType = DEFAULT_COMPONENT()
        if file is None:
            if name is None:
                raise ValueError(
                    "Expected both 'name' and 'data' kwargs to be used together",
                )
            if isinstance(data, str):
                if data == "":
                    raise ValueError(
                        "Expected component data to be a string of length longer that 0",
                    )
                content.update(self.parse(data, "_cmpt_"))
            elif isinstance(data, dict):
                content.update(data)
            else:
                raise ValueError(
                    "Expected component data to be a string or a ComponentType dict",
                )
        else:
            file = Path(file)
            with file.open("r", encoding="utf-8") as c_file:
                name = name or self.generate_name(file.as_posix(), ignore)
                content.update(self.parse(c_file.read(), file.as_posix()))

        self.validate(content)
        content["hash"] = name + content["hash"]
        self.components[name] = content

    def __iter__(self) -> Iterator[tuple[str, ComponentType]]:
        yield from self.components.items()

    def keys(self):
        return self.components.keys()

    def values(self):
        return self.components.values()

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
                "Expected ComponentType 'props' that is a dict of str to any value",
            )

        if "context" not in data or not isinstance(data["context"], dict):
            raise ValueError(
                "Expected ComponentType 'context' that is a dict of str to any value",
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
                "Expected ComponentType 'script' that is alist of phml elements with a tag of 'script'",
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
                "Expected ComponentType 'styles' that is a list of phml elements with a tag of 'style'",
            )

        if (
            "elements" not in data
            or not isinstance(data["elements"], list)
            or len(data["elements"]) == 0
            or not all(
                isinstance(element, (Element, Literal)) for element in data["elements"]
            )
        ):
            raise ValueError(
                "Expected ComponentType 'elements' to be a list of at least one Element or Literal",
            )
