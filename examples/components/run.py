from phml import HypertextManager 
from pathlib import Path


root = Path("src")

cdir = Path("components") # Component directory
pdir = Path("pages") # Pages directory
sdir = Path("site") # Site output directory

if __name__ == "__main__":
    phml = HypertextManager()

    for cfile in (root / cdir).glob("**/*.phml"):
        phml.add(cfile, ignore=(root / cdir).as_posix())

    for pfile in (root / pdir).glob("**/*.phml"):
        phml.load(pfile).write(
            (root / sdir / pfile.name).with_suffix(".html").as_posix()
        )
