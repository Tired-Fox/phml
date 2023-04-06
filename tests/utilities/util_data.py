from phml import p
from phml.nodes import AST

__all__ = [
    "ast",
    "container",
    "first",
    "para",
    "text",
    "middle",
    "last"
]

first = p("div", {"class": "sample", "id": "sample-1"})
last = p("div", {"class": "sample", "id": "sample-3"})
text = p("text", "test text")
para = p("p", {"hidden": True}, text)
middle = p("div", {"class": "sample", "id": "sample-2"}) 

container = p("div",
    {"id": "container"},
    first,
    para,
    middle,
    last 
)

ast: AST = p(
    p("html",
        p("head",
            p("title", "test")
        ),
        p("body",
            p("h1", "hello world!"),
            container
        )
    )
)
