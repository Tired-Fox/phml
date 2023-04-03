from phml.nodes import inspect, Node
from phml import p, HypertextManager 

if __name__ == "__main__":
    if False:
        with HypertextManager.open("sample.phml", "index.html") as phml:
            phml.add("Nav.phml", ignore="sandbox")
            phml.add_module("util", imports=["print_hello"])
            # print(phml.parse().render())
    else:
        data = p(
            p("html",
              p("head", p("title", "Example")),
              p("body", p("h1", "Hello World"))
            )
        ).as_dict()
        alt = p("html",
              p("head", p("title", "Example")),
              p("body", p("h1", "Hello World"))
        ).as_dict()
        print(HypertextManager().parse(alt).render())
        print(inspect(Node.from_dict(data), color=True))
        # HypertextManager().format(file="index.html", compress=False)
