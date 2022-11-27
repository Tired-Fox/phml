from phml import PHMLCore
from phml.builder import p

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

if __name__ == "__main__":
    core = PHMLCore(components).parse(doc)
    print(core.render())
