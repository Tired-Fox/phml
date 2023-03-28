from phml.v2.core import Manager

if __name__ == "__main__":
    # core = PHMCore()
    # input(core.load("sandbox/sample.phml").render())

    with Manager.open("sandbox/sample.phml", "sandbox/index.html") as phml:
        phml.add("sandbox/Nav.phml", ignore="sandbox")
        print(phml.parse().render())
        # print(phml.ast.pretty())
