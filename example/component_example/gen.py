from pathlib import Path
from phml import PHMLCore
from phml.utils import filename_from_path


cdir = "components"
pdir = "pages"
sdir = "site"

if __name__ == "__main__":
    core = PHMLCore()

    for cfile in Path(cdir).glob("**/*.phml"):
        core.add(cfile)

    Path(sdir).mkdir(parents=True, exist_ok=True)

    for pfile in Path(pdir).glob("**/*.phml"):
        (
            core.load(pfile).write(
                Path(sdir).joinpath(filename_from_path(pfile) + ".html").as_posix()
            )
        )
