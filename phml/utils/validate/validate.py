# pylint: disable=missing-module-docstring
from re import match, split, sub

from phml.nodes import All_Nodes, Comment, Element, Literal, Parent, Root, Text

__all__ = [
    "validate",
    "parent",
    "literal",
    "generated",
    "has_property",
    "is_heading",
    "is_css_link",
    "is_css_style",
    "is_javascript",
    "is_element",
    "is_event_handler",
]


def validate(node: All_Nodes) -> bool:
    """Validate a node based on attributes and type."""

    if hasattr(node, "children"):
        if not hasattr(node, "type"):
            raise AssertionError("Node should have a type")

        if node.type not in ["root", "element"]:
            raise AssertionError(
                "Node should have a type of 'root' or 'element' to contain the 'children' attribute"
            )

        if not all(isinstance(child, All_Nodes) for child in node.children):
            raise AssertionError("Children must be a node type")

    if hasattr(node, "properties"):
        if hasattr(node, "type") and node.type != "element":
            raise AssertionError("Node must be of type 'element' to contain 'properties'")

        if not all(isinstance(node[prop], (int, str)) for prop in node.properties):
            raise AssertionError("Node 'properties' must be of type 'int' or 'str'")

    if hasattr(node, "value") and not isinstance(node.value, str):
        raise AssertionError("Node 'value' must be of type 'str'")

    return True


def parent(node: Root | Element) -> bool:
    """Validate a parent node based on attributes and type."""
    if not issubclass(type(node), Parent):
        raise AssertionError(
            "Node must inherit from 'Parent'. 'Root' and 'Element' are most common."
        )

    if not hasattr(node, "children") or node.children is None:
        raise AssertionError("Parent nodes should have the 'children' attribute")

    if node.type == "element" and (not hasattr(node, "properties") or node.properties is None):
        raise AssertionError("Parent element node shoudl have the 'properties' element.")


def literal(node: Text | Comment) -> bool:
    """Validate a literal node based on attributes."""

    if not issubclass(type(node), Literal):
        raise AssertionError(
            "Node must inherit from 'Literal'. 'Text' and 'Comment' are most common."
        )

    if not hasattr(node, "value") or not isinstance(node.value, str):
        raise AssertionError("Literal nodes 'value' type should be 'str'")


def generated(node: All_Nodes) -> bool:
    """Checks if a node has been generated. A node is concidered
    generated if it does not have a position.

    Args:
        node (All_Nodes): Node to check for position with.

    Returns:
        bool: Whether a node has a position or not.
    """
    return not hasattr(node, "position") or node.position is None


def is_heading(node) -> bool:
    """Check if an element is a heading."""

    if node.type == "element":
        if match(r"h[1-6]", node.tag) is not None:
            return True
        return False
    raise TypeError("Node must be an element.")


def is_css_link(node) -> bool:
    """Check if an element is a `link` to a css file.

    Returns `true` if `node` is a `<link>` element with a `rel` list that
    contains `'stylesheet'` and has no `type`, an empty `type`, or `'text/css'`
    as its `type`
    """

    return (
        # Verify it is a element with a `link` tag
        is_element(node, "link")
        # Must have a rel list with stylesheet
        and has_property(node, "rel")
        and "stylesheet" in split(r" ", sub(r" +", " ", node["rel"]))
        and (
            # Can have a `type` of `text/css` or empty or no `type`
            not has_property(node, "type")
            or (has_property(node, "type") and (node["type"] == "text/css" or node["type"] == ""))
        )
    )


def is_css_style(node) -> bool:
    """Check if an element is a css `style` element.

    Returns `true` if `node` is a `<style>` element that
    has no `type`, an empty `type`, or `'text/css'` as its `type`.
    """

    return is_element(node, "style") and (
        not has_property(node, "type")
        or (has_property(node, "type") and (node["type"] == "" or node["type"] == "text/css"))
    )


def is_javascript(node) -> bool:
    """Check if an element is a javascript `script` element.

    Returns `true` if `node` is a `<script>` element that has a valid JavaScript `type`, has no
    `type` and a valid JavaScript `language`, or has neither.
    """
    return is_element(node, "script") and (
        (
            has_property(node, "type")
            and node["type"] in ["text/ecmascript", "text/javascript"]
            and not has_property(node, "language")
        )
        or (
            has_property(node, "language")
            and node["language"] in ["ecmascript", "javascript"]
            and not has_property(node, "type")
        )
        or (not has_property(node, "type") and not has_property(node, "language"))
    )


def is_element(node, *conditions: str | list) -> bool:
    """Checks if the given node is a certain element.

    When providing a str it will check that the elements tag matches.
    If a list is provided it checks that one of the conditions in the list
    passes.
    """

    return bool(
        node.type == "element"
        and any(
            bool(
                (isinstance(condition, str) and node.tag == condition)
                or (isinstance(condition, list) and any(node.tag == nested for nested in condition))
            )
            for condition in conditions
        )
    )


def is_event_handler(attribute: str) -> bool:
    """Takes a attribute name and returns true if
    it starts with `on` and its length is `5` or more.
    """
    return attribute.startswith("on") and len(attribute) >= 5


def has_property(node, attribute: str) -> bool:
    """Check to see if an element has a certain property in properties."""
    if node.type == "element":
        if attribute in node.properties:
            return True
        return False
    raise TypeError("Node must be an element.")


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
        return has_property(node, "href")

    if is_element(node, "input"):
        return has_property(node, "type") and node["type"].lower() != "hidden"

    if is_element(node, "button", "details", "embed", "iframe", "img"):
        return has_property(node, "usemap")

    if is_element(node, "audio", "label", "select", "text", "area", "video"):
        return has_property(node, "controls")

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

    if isinstance(node, Text):
        return True

    if is_element(node, "area"):
        return node.parent is not None and is_element(node.parent, "map")

    if is_element(node, "meta"):
        return has_property(node, "itemprop")

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
            has_property(node, "itemprop")
            or (
                has_property(node, "rel")
                and all(token.strip() in body_ok for token in node["rel"].split(" "))
            )
        )

    if is_element(
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
