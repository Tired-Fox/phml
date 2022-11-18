from phml import Parser

from phml.file_types import (
    PHML,
    JSON,
    HTML
)

if __name__ == "__main__":
    parser = Parser()
    
    parser.load("output/out1_as_json.json").write("output/from_json.html")

    parser.load("phml/sample1.phml")\
        .write("output/out1_as_phml.phml", PHML)\
        .write("output/out1_as_json.json", JSON)\
        .write("output/out1_as_html.html", HTML)

    parser.load("phml/sample2.phml")\
        .write("output/out2_as_phml.phml", PHML)\
        .write("output/out2_as_json.json", JSON)\
        .write("output/out2_as_html.html", HTML)

    print(parser.load("phml/sample.phml").write("output/sample.pehl").write("output/sample.json", JSON).ast.inspect())
