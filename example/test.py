from phml import Parser, PHML, JSON, Element, Root, test

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
    el = Element("div", {}, parent)
    parent.children.append(el)
