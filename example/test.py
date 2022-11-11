from phml import (
    Parser,
    PHML,
    JSON,
    Element,
    Root,
    Position,
    Point,
    DocType,
    Comment,
    Text,
    AST,
)

if __name__ == "__main__":
    parser = Parser()

    parser.parse("phml/sample1.phml").write("output/out1_as_phml.phml", PHML).write(
        "output/out1_as_json.json", JSON
    )

    print(parser.ast.inspect())

    parser.parse("phml/sample2.phml").write("output/out2_as_phml.phml", PHML).write(
        "output/out2_as_json.json", JSON
    )

    parent = Root()
    el_1 = Element("div", {}, parent)
    el_2 = Element("a", {}, parent)
    parent.children.extend([el_1, el_2])

    print(parser.parse("phml/sample.phml").write("output/sample.pehl").write("output/sample.json", JSON).ast.inspect())
