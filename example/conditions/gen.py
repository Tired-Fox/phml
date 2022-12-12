from phml import PHML, filename_from_path
from pathlib import Path

if __name__ == "__main__":
    phml = PHML()
    Path("site/").mkdir(parents=True, exist_ok=True)

    for file in Path("./").glob("**/*.phml"):
        phml.load(file)
        if file.name == "if.phml":
            phml.write(
                "site/index.html", escaped=" <,>, and & are automatically escaped for security."
            )
        else:
            phml.write(
                "site/" + filename_from_path(file) + ".html",
                escaped=" <,>, and & are automatically escaped for security.",
            )
