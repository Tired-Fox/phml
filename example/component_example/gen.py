from pathlib import Path
from phml import PHMLCore
from phml.builder import p
from phml.utils import tag_from_file, filename_from_path

components = {"message": p("h1", "{message or 'Hello World!'}", p("slot", {}))}
# <div>
#   <h1>message or 'hello world!'</h1>
#   <slot />
# </div>

doc = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Component Example</title>
    </head>
    <body>
        <message message="This is a custom message!" >
            <p>And all the aliens too!</p>
            <p>{message}</p>
        </message>
        <p>Normal element and text</p>
        <message />
    </body>
</html>\
"""

cdir = "components"
pdir = "pages"
sdir = "site"

if __name__ == "__main__":
    core = PHMLCore()
    cmps = {}
    for cfile in Path(cdir).glob("**/*.phml"):
        cmp_name = tag_from_file(filename_from_path(cfile))
        core.load(cfile)
        cmps.update({cmp_name: core.ast.children[0]})

    core.add(cmps)
    Path(sdir).mkdir(parents=True, exist_ok=True)

    for pfile in Path(pdir).glob("**/*.phml"):
        core.load(pfile)
        core.write(Path(sdir).joinpath(filename_from_path(pfile)+".html").as_posix())
