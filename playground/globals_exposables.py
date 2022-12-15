from phml import PHML

phml = PHML()

expr = """\
<html>
    <head></head>
    <python>
        from information import info
        alert='Weather Alert'
    </python>
    <body>
        <h1>{message}</h1>
        <p>{alert}</p>
        <ul>
            <li @for="item in info">{item}</li>
        </ul>
    </body>
</html>\
"""

phml.expose(message="Hello World!")
phml.expand("data")

print(phml.parse(expr).render())

phml.redact("message")


print(phml.parse(expr).render(message="Girl meets world"))
