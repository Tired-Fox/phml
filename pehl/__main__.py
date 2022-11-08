from parser import parse

if __name__ == "__main__":
    with open("sample.pehl.html", "r", encoding="utf-8") as sample_file:
        parse(sample_file.read(), "sample.pehl.html")
