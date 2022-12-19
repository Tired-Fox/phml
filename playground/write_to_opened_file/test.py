from phml import PHML

phml = PHML()

phml.parse("<html><head><title>test</title></head><body>Hello World</body></html>")

with open("test.html", "+w", encoding="utf-8") as file:
    phml.write(file)
