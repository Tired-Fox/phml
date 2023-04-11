# Simple PHML Example

PHML can be really quick and easy to get up and going for simple tasks. The `HypertextManager` can be used as a context manager to automatically read from a file and write to an html file when parse and render are called. However if you don't want to use the context manager, you can use all the methods manually to get the same result. For example below is a snippet of how the context manager can be used, versus how it can be done manually.

```python
from phml import HypertextManager

with HypertextManager.open("src/index.phml") as phml:
  phml.parse() # This will parse the file specified in `open()`

  # The context manager will automatically write to a html file with the same
  # path and name as the input file. This can be overridden with a second parameter to `open()` 

  phml.render(message="Hello World!") # This will compile the phml to html and render the string

  # `write()` can also be used and acts like render, but automatically writes the result to a specified
  # file. It is not affected by the context manager so this is a great way to use the input file as a template
  # and output multiple files based on the passed in data 

  phml.write("src/some-page.html", message="First page", title="Temlate Page")
  phml.write("src/some-other-page.html", message="Second page", title="Another temlate Page")
```

The above example can all be done manually as well. Neither way proves to have more features, it is more a matter of preference. Below is the example of doing it all manually.

```python
from phml import HypertextManager

phml = HypertextManager()
phml.parse("<div>Hello World</div>") # This will parse the passed in string 

phml.load("src/index.phml") # Alternatively the load method will automatically read in and parse a file

# `render()` returns the resulting string regardless if a context manager is used
html_string = phml.render(message="Hello World!")

# `write()` works the same was as in a context manager
phml.write("src/some-page.html", message="First page", title="Temlate Page")
phml.write("src/some-other-page.html", message="Second page", title="Another temlate Page")
```

Notice how the input phml str or data is only parsed once. Each time compile is called a copy of the parsed
phml AST is converted to html based on the data passed in. Every time `parse()` or `load()` or `open()` is called, a new phml AST is parsed and cached in the `HypertextManager`. This AST is used until a new phml object is parsed.

Also shown in the above examples, is keyword arguments to `render()` and `write()`. These keyword arguments are `"variables"` that are exposed to the phml AST during compilation. These variables can be referenced in phml via python attributes, attributes prefixed with `:`, or in inline python blocks,  text surrounded with `{{ }}`.

Another key point for simple/basic phml use is importing other python modules. PHML allows for a user to define and import python modules that are cached and can be used in phml. This can be a path to a python module, or a relative path to a module in the current working directory, similar to pythons existing import syntax, or an import of a built-in library. Built in libraries can be imported and used inside phml without using PHML's special import feature. Below is an example of using the import feature, then using the import in phml.

```python
# utils.py
def get_hello() -> str:
  return "Hello World!"

# run.py | The file running phml
phml = HypertextManager()
phml.add_module("utils.py", imports=["get_hello"])
phml.load("src/index.phml").write("src/index.html")
```

```html
<!-- index.phml -->
<!DOCTYPE html>
<html lan="en">

  <head>
    ...
    <python>
      # The modules added through the manager can be brought into scope with
      # a normal python import. All modules imported from the phml import system
      # will have a name that is prefixed with a single `.`.

      from .utils import get_hello

    </python>
  </head>

  <body>
    <h1>{{ get_hello() }}</h1>
  </body>

</html>
```

That is all for the simple example/basics. Feel free to explore and try out different combinations with these features.
