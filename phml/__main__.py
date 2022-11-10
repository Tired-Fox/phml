from .parser import PHML

if __name__ == "__main__":
    parser = PHML()
    parser.parse("../sample.phml").write("../output.phml")
