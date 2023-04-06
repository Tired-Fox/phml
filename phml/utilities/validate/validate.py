from re import match, split, sub
from typing import Any

from phml.nodes import Element, Literal, Node, Parent

__all__ = [
    "validate",
    "generated",
    "is_heading",
    "is_css_link",
    "is_css_style",
    "is_javascript",
    "is_element",
    "is_embedded",
    "is_interactive",
    "is_phrasing",
    "is_event_handler",
    "blank",
]


def validate(node: Node) -> bool:
    """Validate a node based on attributes and type."""

    if isinstance(node, Parent) and not all(isinstance(child, Node) for child in node):
        raise AssertionError("Children must be a node type")

    if isinstance(node, Element):
        if not all(isinstance(node[prop], (bool, str)) for prop in node.attributes):
            raise AssertionError("Element 'attributes' must be of type 'bool' or 'str'")

    if isinstance(node, Literal) and not isinstance(node.content, str):
        raise AssertionError("Literal 'content' must be of type 'str'")

    return True


def generated(node: Node) -> bool:
    """Checks if a node has been generated. A node is concidered
    generated if it does not have a position.

    Args:
        node (Node): Node to check for position with.

    Returns:
        bool: Whether a node has a position or not.
    """
    return node.position is None


def is_heading(node: Element) -> bool:
    """Check if an element is a heading."""

    if node.type == "element":
        if match(r"h[1-6]", node.tag) is not None:
            return True
        return False
    raise TypeError("Node must be an element.")


def is_css_link(node: Element) -> bool:
    """Check if an element is a `link` to a css file.

    Returns `true` if `node` is a `<link>` element with a `rel` list that
    contains `'stylesheet'` and has no `type`, an empty `type`, or `'text/css'`
    as its `type`
    """

    return (
        # Verify it is a element with a `link` tag
        is_element(node, "link")
        # Must have a rel list with stylesheet
        and "rel" in node
        and "stylesheet" in split(r" ", sub(r" +", " ", node["rel"]))
        and (
            # Can have a `type` of `text/css` or empty or no `type`
            "type" not in node
            or ("type" in node and (node["type"] in ["text/css", ""]))
        )
    )


def is_css_style(node: Element) -> bool:
    """Check if an element is a css `style` element.

    Returns `true` if `node` is a `<style>` element that
    has no `type`, an empty `type`, or `'text/css'` as its `type`.
    """

    return is_element(node, "style") and (
        "type" not in node or ("type" in node and (node["type"] in ["", "text/css"]))
    )


def is_javascript(node: Element) -> bool:
    """Check if an element is a javascript `script` element.

    Returns `true` if `node` is a `<script>` element that has a valid JavaScript `type`, has no
    `type` and a valid JavaScript `language`, or has neither.
    """
    return is_element(node, "script") and (
        (
            "type" in node
            and node["type"] in ["text/ecmascript", "text/javascript"]
            and "language" not in node
        )
        or (
            "language" in node
            and node["language"] in ["ecmascript", "javascript"]
            and "type" not in node
        )
        or ("type" not in node and "language" not in node)
    )


def is_element(node: Node, *conditions: str | list) -> bool:
    """Checks if the given node is a certain element.

    When providing a str it will check that the elements tag matches.
    If a list is provided it checks that one of the conditions in the list
    passes.
    """

    if isinstance(node, Element):
        if len(conditions) > 0:
            return any(
                bool(
                    (isinstance(condition, str) and node.tag == condition)
                    or (
                        isinstance(condition, list)
                        and any(node.tag == nested for nested in condition)
                    ),
                )
                for condition in conditions
            )
        else:
            return True
    return False


def is_event_handler(attribute: str) -> bool:
    """Takes a attribute name and returns true if
    it starts with `on` and its length is `5` or more.
    """
    return attribute.startswith("on") and len(attribute) >= 5


def is_embedded(node: Element) -> bool:
    """Check to see if an element is an embedded element.

    Embedded Elements:

    * audio
    * canvas
    * embed
    * iframe
    * img
    * MathML math
    * object
    * picture
    * SVG svg
    * video

    Returns:
        True if emedded
    """
    # audio,canvas,embed,iframe,img,MathML math,object,picture,SVG svg,video

    return is_element(
        node,
        "audio",
        "canvas",
        "embed",
        "iframe",
        "img",
        "math",
        "object",
        "picture",
        "svg",
        "video",
    )


def is_interactive(node: Element) -> bool:
    """Check if the element is intended for user interaction.

    Conditions:

    * a (if the href attribute is present)
    * audio (if the controls attribute is present)
    * button, details, embed, iframe, img (if the usemap attribute is present)
    * input (if the type attribute is not in the Hidden state)
    * label, select, text, area, video (if the controls attribute is present)

    Returns:
        True if element is interactive
    """

    if is_element(node, "a"):
        return "href" in node

    if is_element(node, "input"):
        return "type" in node and str(node["type"]).lower() != "hidden"

    if is_element(node, "img"):
        return "usemap" in node and node["usemap"] is True

    if is_element(node, "video"):
        return "controls" in node

    if is_element(
        node, "button", "details", "embed", "iframe", "label", "select", "textarea"
    ):
        return True

    return False


def is_phrasing(node: Element) -> bool:
    """Check if a node is phrasing text according to
    https://html.spec.whatwg.org/#phrasing-content-2.

    Phrasing content is the text of the document, as well as elements that mark up that text at the
    intra-paragraph level. Runs of phrasing content form paragraphs.

    * area (if it is a descendant of a map element)
    * link (if it is allowed in the body)
    * meta (if the itemprop attribute is present)
    * map, mark, math, audio, b, bdi, bdo, br, button, canvas, cite, code, data, datalist, del, dfn,
     em, embed, i, iframe, img, input, ins, kbd, label, a, abbr, meter, noscript, object, output,
     picture, progress, q, ruby, s, samp, script, select, slot, small, span, strong, sub, sup, svg,
     template, textarea, time, u, var, video, wbr, text (true)

    Returns:
        True if the element is phrasing text
    """

    if Literal.is_text(node):
        return True

    if is_element(node, "area"):
        return node.parent is not None and is_element(node.parent, "map")

    if is_element(node, "meta"):
        return "itemprop" in node

    if is_element(node, "link"):
        body_ok = [
            "dns-prefetch",
            "modulepreload",
            "pingback",
            "preconnect",
            "prefetch",
            "preload",
            "prerender",
            "stylesheet",
        ]

        return bool(
            "itemprop" in node
            or (
                "rel" in node
                and all(
                    token in body_ok for token in str(node["rel"]).split(" ")
                    if token.strip() != ""
                )
            ),
        )

    if is_element(
        node,
        "node",
        "map",
        "mark",
        "math",
        "audio",
        "b",
        "bdi",
        "bdo",
        "br",
        "button",
        "canvas",
        "cite",
        "code",
        "data",
        "datalist",
        "del",
        "dfn",
        "em",
        "embed",
        "i",
        "iframe",
        "img",
        "input",
        "ins",
        "kbd",
        "label",
        "a",
        "abbr",
        "meter",
        "noscript",
        "object",
        "output",
        "picture",
        "progress",
        "q",
        "ruby",
        "s",
        "samp",
        "script",
        "select",
        "slot",
        "small",
        "span",
        "strong",
        "sub",
        "sup",
        "svg",
        "template",
        "textarea",
        "time",
        "u",
        "var",
        "video",
        "wbr",
    ):
        return True

    return False


def blank(value: Any) -> bool:
    """Takes any value type and returns whether it is blank/None.
    For strings if the value is stripped and is equal to '' then it is blank.
    Otherwise if len > 0 and is not None then not blank.

    Args:
        value (Any): The value to check if it is blank.

    Returns:
        bool: True if value is blank
    """

    if value is None or not hasattr(value, "__len__"):
        return True

    if isinstance(value, str):
        value = value.strip()

    return len(value) == 0
