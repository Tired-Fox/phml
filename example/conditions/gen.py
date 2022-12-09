from phml import PHMLCore, filename_from_path
from pathlib import Path

if __name__ == "__main__":
    core = PHMLCore()
    Path("site/").mkdir(parents=True, exist_ok=True)

    for file in Path("./").glob("**/*.phml"):
        core.load(file)
        if file.name == "if.phml":
            core.write("site/index.html")
        else:
            core.write("site/" + filename_from_path(file) + ".html")