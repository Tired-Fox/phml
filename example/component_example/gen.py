from phml import PHML 
from phml.utilities import filename_from_path
from pathlib import Path


cdir = "components"
pdir = "pages"
sdir = "site"

if __name__ == "__main__":
    phml = PHML()

    for cfile in Path(cdir).glob("**/*.phml"):
        phml.add(cfile, strip=cdir)

    Path(sdir).mkdir(parents=True, exist_ok=True)

    for pfile in Path(pdir).glob("**/*.phml"):
        (
            phml.load(pfile).write(
                Path(sdir).joinpath(filename_from_path(pfile) + ".html").as_posix()
            )
        )
