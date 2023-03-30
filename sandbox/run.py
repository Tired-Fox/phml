from phml.core import PHML 
from phml.nodes import inspect

if __name__ == "__main__":
    # core = PHMCore()
    # input(core.load("sandbox/sample.phml").render())

    with PHML.open("sample.phml", "index.html") as phml:
        phml.add("Nav.phml", ignore="sandbox")
        phml.add_module("test", imports=["print_hello"])
        print(phml.parse().render(True))
        # print(inspect(phml.ast, color=True, text=True))
