from phml.core.nodes import Element

peach = Element("div", {":each": "hello"})
each = Element("div", {"each": "world"})


def isMatch(node, match: dict):
    return bool(
        isinstance(node, Element)
        and any(
            (hasattr(node, key) and value == getattr(node, key))
            or (
                hasattr(node, "properties")
                and key in node.properties
                and (value is True or value == node[key])
            )
            for key, value in match.items()
        )
    )

print(isMatch(peach, {":each": True, "each": True}))
print(isMatch(each, {"each": "worlD", ":each": True}))
