from phml.core import PHML 
from phml.nodes import inspect

if __name__ == "__main__":
    # core = PHMCore()
    # input(core.load("sandbox/sample.phml").render())

    if True:
        with PHML.open("sample.phml", "index.html") as phml:
            phml.add("Nav.phml", ignore="sandbox")
            phml.add_module("util", imports=["print_hello"])
            print(phml.parse().render())
            # print(inspect(phml.ast, color=True, text=True))
    else:
        PHML().format(file="index.html", compress=False)
