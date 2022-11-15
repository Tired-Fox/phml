from phml import (
    Parser,
    AST,
)

from phml.file_types import (
    PHML,
    JSON,
    HTML
)

from phml.nodes import (
    Element,
    Root,
    Position,
    Point,
    DocType,
    Comment,
    Text,
)

if __name__ == "__main__":
    parser = Parser()

    parser.parse("phml/sample1.phml")\
        .write("output/out1_as_phml.phml", PHML)\
        .write("output/out1_as_json.json", JSON)\
        .write("output/out1_as_html.html", HTML)

    parser.parse("phml/sample2.phml")\
        .write("output/out2_as_phml.phml", PHML)\
        .write("output/out2_as_json.json", JSON)\
        .write("output/out2_as_html.html", HTML)

    print(parser.parse("phml/sample.phml").write("output/sample.pehl").write("output/sample.json", JSON).ast.inspect())
