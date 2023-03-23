from core import PHMCore
if __name__ == "__main__":
    # core = PHMCore()
    # input(core.load("sandbox/sample.phml").render())

    with PHMCore.open("sandbox/sample.phml", "sandbox/index.html") as phml:
        print(phml.parse().render())
        # print(phml.ast.pretty())
