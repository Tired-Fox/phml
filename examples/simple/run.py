"""
This example uses the `HypertextManager` context manager `open()` to
open an input and output file. When render is called it automatically writes
to the defined output file. The context manager also automatically parses the input file.
On the other hand the manual loading and writing/rendering to a file is just as simple. Both
methods are virtually equivelant, but are focused toward different preferences/styles of programming.
"""
from phml import HypertextManager


if __name__ == "__main__":
    context_message = "This phml is compiled with the phml context manager"
    manual_message = "This phml is compiled with manual phml manager calls"

    with HypertextManager.open("src/index.phml", "src/context/context.html") as phml:
        phml.add_module("utils.py", imports=["get_title"])
        phml.render(id="context", message=context_message)
    
        phml.write("src/context/template-1.html", id="context", message="Template 1")
        phml.write("src/context/template-2.html", id="context", message="Template 2")
    
    phml = HypertextManager()
    phml.add_module("utils.py", imports=["get_title"])
    phml.load("src/index.phml")
    phml.write("src/manual/manual.html", id="manual", message=manual_message)

    # The manual loading and writing can also be chained. Most methods return a reference to
    # the manager to allow for method chaining
    #
    # phml = HypertextManager().add_module("utils.py", imports=["get_title"])
    # phml.load("src/index.phml").write("src/manual.phml", id="manual", message=manual_message)

