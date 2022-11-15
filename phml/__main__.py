from parser import Parser

if __name__ == "__main__":
    parser = Parser().parse("../tests/sample.phml")
    parser.ast.to_html()
