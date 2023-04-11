from pathlib import Path

from phml import HypertextManager

out = "src/site/"

if __name__ == "__main__":
    message = " <,>, and & are automatically escaped for security."
    phml = HypertextManager()

    # Path.glob() is used here to show how phml can be used with more dynamic code
    for file in Path("./").glob("**/*.phml"):
        phml.load(file)
        if file.name == "if.phml":
            phml.write(out + "index.html", escaped=message)
        else:
            # The suffix is automatically changed to `.html`
            phml.write(out + file.name, escaped=message)
