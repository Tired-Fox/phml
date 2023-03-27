from collections.abc import Callable
from copy import deepcopy
from functools import wraps
from inspect import getfullargspec
import re
from typing import Any
from embedded import Embedded
from nodes import (
    LiteralType,
    Literal,
    Element,
    Parent,
)
from components import ComponentManager
from utils import iterate_nodes
from compile_steps import (
   compile_for_tags 
)


class HypertextMarkupCompiler:
    def _get_python_elements(self, node: Parent) -> list[Element]:
        result = []
        if node.children is not None:
            for child in node:
                if isinstance(child, Element):
                    if child.tag == "python":
                        result.append(child)
                        idx = node.children.index(child)
                        del node.children[idx]
                    else:
                        result.extend(self._get_python_elements(child))

        return result

    def _process_scope(
        self,
        node: Parent,
        components: ComponentManager,
        context: dict,
    ):
        """Process steps for a given scope/parent node."""
        core_steps: list[Callable] = [
            compile_for_tags # TODO: Loop element fallback
            # TODO: Steps:
            # - conditional elements
            # - python attributes / python blocks in text
            # - components (with caching)
            # - markdown
        ]
        
        # PERF: Pre core compile step

        # Core compile steps
        for step in core_steps:
            step(node, components, context)

        # PERF: Post core compile steps

        # Recurse steps for each scope
        if node.children is not None:
            for child in node:
                if isinstance(child, Element):
                    self._process_scope(child, components, context)

    def compile(self, node: Parent, _components: ComponentManager, **context: Any) -> Parent:
        # get all python elements and process them
        p_elems = self._get_python_elements(node)
        embedded = Embedded("")
        for p_elem in p_elems:
            embedded += Embedded(p_elem)

        # Recursively process scopes
        self._process_scope(node, _components, context)

        return node

    def _render_attribute(self, key: str, value: str | bool) -> str:
        if isinstance(value, str):
            return f'{key}="{value}"'
        else:
            return str(key) if value else ""

    def _render_element(
        self, element: Element, components: ComponentManager, indent: int = 0, compress: str = "\n"
    ) -> str:
        attr_idt = 2
        attrs = ""
        if element.in_pre:
            attrs = " " + " ".join(
                self._render_attribute(key, value)
                for key, value in element.attributes.items()
                if value != False
            )
        elif len(element.attributes) > 1:
            idt = indent + attr_idt if compress == "\n" else 1
            attrs = (
                f"{compress}"
                + " " * (idt)
                + f'{compress}{" "*(idt)}'.join(
                    self._render_attribute(key, value)
                    for key, value in element.attributes.items()
                    if value != False
                )
                + f"{compress}{' '*(indent)}"
            )
        elif len(element.attributes) == 1:
            key, value = list(element.attributes.items())[0]
            attrs = " " + self._render_attribute(key, value) + " "

        result = f"{' '*indent if not element.in_pre else ''}<{element.tag}{attrs}{'/' if element.children is None else ''}>"
        if element.children is None:
            return result

        if (
            compress != "\n"
            or element.in_pre
            or (
                len(element.children) == 1
                and isinstance(element.children[0], Literal)
                and element.children[0].name == LiteralType.Text
                and "\n" not in result
            )
        ):
            children = self.render(element, components, _compress=compress)
            result += children + f"</{element.tag}>"
        else:
            children = self.render(element, components, indent + 2, _compress=compress)
            result += compress + children
            result += f"{compress}{' '*indent}</{element.tag}>"

        return result

    def _render_literal(
        self, literal: Literal, indent: int = 0, compress: str = "\n"
    ) -> str:
        if literal.in_pre:
            offset = ""
            compress = ""
            content = literal.content
        else:
            content = literal.content.strip()
            lines = content.split("\n")
            offset = " " * indent
            f"{compress}{offset}".join(lines)

        if literal.name == LiteralType.Text:
            return offset + content
        elif literal.name == LiteralType.Comment:
            return f"{offset}<!--" + content + "-->"
        return ""

    def render(
        self,
        node: Parent,
        _components: ComponentManager,
        indent: int = 0,
        _compress: str = "\n",
        **context: Any
    ) -> str:
        node = self.compile(node, _components, **context)

        result = []
        for child in node:
            if isinstance(child, Element):
                if child.tag == "doctype":
                    result.append(f"<!DOCTYPE html>")
                else:
                    result.append(self._render_element(child, _components, indent, _compress))
            elif isinstance(child, Literal):
                result.append(self._render_literal(child, indent, _compress))

        return _compress.join(result)
