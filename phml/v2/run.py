from phml.v2.core import PHML 
from phml.v2.nodes import inspect

if __name__ == "__main__":
    # core = PHMCore()
    # input(core.load("sandbox/sample.phml").render())

    with PHML.open("sandbox/sample.phml", "sandbox/index.html") as phml:
        phml.add("sandbox/Nav.phml", ignore="sandbox")
        phml.add_module("..sandbox.test", imports=["print_hello"])
        print(phml.parse().render())
        print(inspect(phml.ast, color=True, text=True))
