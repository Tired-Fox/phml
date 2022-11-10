from phml import Parser, PHML, JSON

if __name__ == "__main__":
    parser = Parser()

    parser.parse("phml/sample1.phml")\
        .write("output/out1_as_phml.phml", PHML)\
        .write("output/out1_as_json.json", JSON)

    parser.parse("phml/sample2.phml")\
        .write("output/out2_as_phml.phml", PHML)\
        .write("output/out2_as_json.json", JSON)
