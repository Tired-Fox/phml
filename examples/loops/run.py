from phml import HypertextManager

if __name__ == "__main__":
    print("Generating src/simple.html")
    HypertextManager().load("sample.phml").write("src/sample.html")

    print("Generating src/unicode.html, this may take some time")
    HypertextManager().load("unicode.phml").write("src/unicode.html")
