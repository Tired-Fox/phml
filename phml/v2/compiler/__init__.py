from collections.abc import Callable
from typing import Any

from phml.v2.embedded import Embedded
from phml.v2.utils import normalize_indent
from phml.v2.nodes import (
    LiteralType,
    Literal,
    Element,
    Parent,
)
from phml.v2.components import ComponentManager

from .steps import (
   step_expand_loop_tags,
   step_execute_conditions,
   step_substitute_components,
   step_execute_embedded_python,
    step_add_cached_component_elements,
    step_ensure_doctype,
)

__all__ = [
    "SETUP_STEPS",
    "STEPS",
    "POST_STEPS",
    "HypertextMarkupCompiler",
]

SETUP_STEPS: list[Callable] = []

STEPS: list[Callable] = [
    step_expand_loop_tags,
    step_execute_conditions,
    step_execute_embedded_python,
    step_substitute_components,
    # TODO: Steps:
    # - markdown
]
POST_STEPS: list[Callable] = [
    step_add_cached_component_elements,
    step_ensure_doctype,
]

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

    def _process_scope_(
        self,
        node: Parent,
        components: ComponentManager,
        context: dict,
    ):
        """Process steps for a given scope/parent node."""
        
        # Core compile steps
        for _step in STEPS:
            _step(node, components, context)
        
        # Recurse steps for each scope
        if node.children is not None:
            for child in node:
                if isinstance(child, Element) and child.children is not None:
                    self._process_scope_(child, components, context)

    def compile(self, node: Parent, _components: ComponentManager, **context: Any) -> Parent:
        # get all python elements and process them
        p_elems = self._get_python_elements(node)
        embedded = Embedded("")
        for p_elem in p_elems:
            embedded += Embedded(p_elem)

        # Setup steps to collect data before comiling at different scopes
        for step in SETUP_STEPS:
            step(node, _components, context)

        # Recursively process scopes
        context.update(embedded.context)
        self._process_scope_(node, _components, context)

        # Post compiling steps to finalize the ast
        for step in POST_STEPS:
            step(node, _components, context)

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
                element.tag not in ["script", "style"]
                and len(element.children) == 1
                and isinstance(element.children[0], Literal)
                and element.children[0].name == LiteralType.Text
                and "\n" not in result
            )
        ):
            children = self._render_tree_(element, components, _compress=compress)
            result += children + f"</{element.tag}>"
        else:
            children = self._render_tree_(element, components, indent + 2, _compress=compress)
            result += compress + children
            result += f"{compress}{' '*indent}</{element.tag}>"

        return result

    def _render_literal(
        self, literal: Literal, indent: int = 0, compress: str = "\n"
    ) -> str:
        offset = " " * indent
        if literal.in_pre:
            offset = ""
            compress = ""
            content = literal.content
        else:
            content = literal.content.strip()
            if compress == "\n":
                content = normalize_indent(literal.content, indent)
                content = content.strip()
            else:
                lines = content.split("\n")
                content = f"{compress}{offset}".join(lines)

        if literal.name == LiteralType.Text:
            return offset + content

        if literal.name == LiteralType.Comment:
            return f"{offset}<!--" + content + "-->"
        return ""

    def _render_tree_(
        self,
        node: Parent,
        _components: ComponentManager,
        indent: int = 0,
        _compress: str = "\n",
    ):
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


    def render(
        self,
        node: Parent,
        _components: ComponentManager,
        indent: int = 0,
        _compress: str = "\n",
        **context: Any
    ) -> str:
        node = self.compile(node, _components, **context)
        return self._render_tree_(node, _components, indent, _compress)
