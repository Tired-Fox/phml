import re


style = """

/* Comment */

:is(
    .style-1,
    .style-2
),
.style-3 {
    color: black;
}

div
 span > p
 [data-scope] {
    box-shadow: 0px 5px 10px rgba(0, 0, 0, .25);
}
"""

expect = """

/* Comment */

[data-phml-cmpt-scope="~1234"] .style-1,
[data-phml-cmpt-scope="~1234"] .style-2,
[data-phml-cmpt-scope="~1234"] .style-3 {
    color: black;
}
"""

# TODO: retain multiline selectors and add scope to comma seperated selectors.
# This retains specificity of the selectors.
# - Find matching line to `<selector> {`
# - look at previous lines until line == '' or contains both `/*` and `*/`
# - Combine selectors to one line, then add [data-phml-cmpt-scope="~1234"] to each selector seperated by a `,`

re_selector = re.compile(r"(\n|\}| *)([^}@/]+)(\s*{)")
re_comment = re.compile(r"(\/\*(?:.\s)*\*\/)")

def lstrip(value: str) -> tuple[str, str]:
    offset = len(value) - len(value.lstrip())
    return value[:offset], value[offset:]

def scope_style(style: str, scope: str) -> str:
    """Takes a styles string and adds a scope to the selectors."""

    next_style = re_selector.search(style)
    result = ""

    while next_style is not None:
        start, end = next_style.start(), next_style.start() + len(next_style.group(0))
        leading, selector, trail = next_style.groups()
        if start > 0:
            result += style[:start]
        result += leading

        parts = [""]
        balance = 0
        for char in selector:
            if char == "," and balance == 0:
                parts.append("")
                continue
            elif char == "(":
                balance += 1
            elif char == ")":
                balance = min(0, balance - 1)
            parts[-1] += char

        for i, part in enumerate(parts):
            w, s = lstrip(part)
            parts[i] = w + f"{scope} {s}"
        result += ",".join(parts) + trail 

        style = style[end:]
        next_style = re_selector.search(style)


    if len(style) > 0:
        result+=style

    return result

if __name__ == "__main__":
    print(scope_style(style, '[data-phml-cmpt-scope="~1234"]'))

