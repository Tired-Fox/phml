from phml import PHML

phml = PHML()

page = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Test</title>
    </head>
    
    <body>
        <cmpt/>
        <cmpt-2/>
    </body>
</html>\
"""

phml.add("cmpt.phml")
phml.add("cmpt2.phml")

print(phml.parse(page).write("test.html"))
