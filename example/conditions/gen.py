from phml import PHML 
from phml.utilities import filename_from_path
from pathlib import Path

out = "site/"

if __name__ == "__main__":
    phml = PHML()
    Path(out).mkdir(parents=True, exist_ok=True)

    for file in Path("./").glob("**/*.phml"):
        phml.load(file)
        if file.name == "if.phml":
            phml.write(
                out + "index.html", escaped=" <,>, and & are automatically escaped for security."
            )
        else:
            phml.write(
                out + filename_from_path(file) + ".html",
                escaped=" <,>, and & are automatically escaped for security.",
            )
