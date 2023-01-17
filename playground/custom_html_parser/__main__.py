from phml import PHML

phml = PHML()

phml.parse("""\
<>
    <div>
        Hello World!
    </div>
    <p>Component</p>
</>\
""")

phml.add(("Component", phml.ast))

phml.parse("""\
<!DOCTYPE html>
<html lang="en">
    <!-- Comment -->
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>

    <body>
        <Header />
        <PHML>
            Some Data <
        </PHML>
        <div 
            @if="True"
            :id='the_id'
        >
            Example
        </div>
        <input type=text />
        <Component />
    </body>

</html>\
""")



print(phml.render(the_id="some-id"))
