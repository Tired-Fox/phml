"""Python Hypertext Markup Language (phml)

The idea behind the creation of Python in Hypertext Markup Language (phml), is to allow for web page generation with direct access to python. This language pulls directly from frameworks like VueJS. There is conditional rendering, components, python elements, inline/embedded python blocks, and much more. Now let’s dive into more about this language.

Let's start with the new `python` element. Python is a whitespace language. As such phml
has the challenge of maintaining the indentation in an appropriate way. With phml, I have made the decision to allow you to have as much leading whitespace as you want as long as the indentation is consistent. This means that indentation is based on the first lines offset. Take this phml example:

```python
<python>
    if True:
        print("Hello World")
</python>
```

This phml python block will adjust the offset so that the python is executed as seen below:

```python
if True:
    print("Hello World")
```

So now we can write python code, now what? You can define functions and variables
how you normally would and they are now available to the scope of the entire file.
Take, for instance, the example from above, the one with `py-src="urls('youtube')"`.
You can define the `URL` function in the `python` element and it can be accessed in an element. So the code would look like this:

```html
<python>
def URL(link: str) -> str:
    links = {
        "youtube": "https://youtube.com"
    }
    if link in links:
        return links[link]
    else:
        return ""
</python>

...

<a href="{URL('youtube')}">Youtube</a>
```

phml combines all `python` elements and treats them as a python file. All local variables and imports are parsed and stored so that they may be accessed later. With that in mind that means you have the full power of the python programming language.

Next up is inline python blocks. These are represented with `{}`. Any text in-between the brackets will be processed as python. This is mostly useful when you want to inject a value from python. Assume that there is a variable defined in the `python` element called `message`
and it contains `Hello World!`. Now this variable can be used like this, `<p>{ message }</p>`,
which renders to, `<p>Hello World!</p>`.

> Note:  Inline python blocks are only rendered in a Text element or inside an html attribute.

Multiline blocks are a lot like inline python blocks, but they also have some differences.
You can do whatever you like inside this block, however if you expect a value to come from the block you must have at least one local variable. The last local variable defined in this block is used at the result/value.

Conditional Rendering with `py-if`, `py-elif`, and `py-else` is an extremely helpful tool in phml.
`py-if` can be used alone and that the python inside it's value must be truthy for the element to be rendered. `py-elif` requires an element with a `py-if` or `py-elif` attribute immediately before it, and it's condition is rendered the same as `py-if` but only rendered if a `py-if` or `py-elif` first
fails. `py-else` requires there to be either a `py-if` or a `py-else` immediately before it. It only
renders if the previous element's condition fails. If `py-elif` or `py-else` is on an element, but
the previous element isn't a `py-if` or `py-elif` then an exception will occur. Most importantly, the first element in a chain of conditions must be a `py-if`. For ease of use, instead of writing `py-if`, `py-elif`, or `py-else` can be written as `@if`, `@elif`, or `@else` respectively.

Other than conditions, there is also a built in `py-for` attribute. Any element with py-for will take a python for-loop expression that will be applied to that element. So if you did something like this:

```html
<ul>
    <li py-for='i in range(3)'>
        <p>{i}</p>
    </li>
</ul>
```

The compiled html will be:

```html
<ul>
    <li>
        <p>1</p>
    </li>
    <li>
        <p>2</p>
    </li>
    <li>
        <p>3</p>
    </li>
</ul>
```

The `for` and `:` in the for loops condition are optional. So you can combine `for`, `i in range(10)`, and `:` or leave out `for` and `:` at your discretion. `py-for` can also be written as `@for`.

Python attributes are shortcuts for using inline python blocks in html attributes. Normally, in
phml, you would inject python logic into an attribute similar to this: `src="{url('youtube')}"`. If you would like to make the whole attribute value a python expression you may prefix any attribute with a `py-` or `:`. This keeps the attribute name the same after the prefix, but tells
the parser that the entire value should be processed as python. So the previous example can also be expressed as `py-src="URL('youtube')"` or `:src=”URL('youtube')”`.

This language also has the ability to convert back to html and json with converting to html having more features. Converting to json is just a json representation of a phml ast. However, converting to html is where the magic happens. The compiler executes python blocks, substitutes components, and processes conditions to create a final html string that is dynamic to its original ast. A user may pass additional kwargs to the compiler to expose additional data to the execution of python blocks. If you wish to compile to a non supported language the compiler can take a callable that returns the final string. It passes all the data; components, kwargs, ast, etc… So if a user wishes to extend the language thay may.

> :warning: This language is in early planning and development stages. All forms of feedback are encouraged.

"""

from typing import Optional
from pathlib import Path

from . import builder, core, nodes, utils, virtual_python
from .core import Compiler, Parser, file_types
from .nodes import AST, All_Nodes

__version__ = "0.1.0"
__all__ = [
    "Compiler",
    "Parser",
    "file_types",
    "AST",
    "core",
    "nodes",
    "utils",
    "virtual_python",
    "file_types",
    "builder",
]


class PHMLCore:
    """A helper class that bundles the functionality
    of the parser and compiler together. Allows for loading source files,
    parsing strings and dicts, rendering to a different format, and finally
    writing the results of a render to a file.
    """

    parser: Parser
    """Instance of a [Parser][phml.parser.Parser]."""
    compiler: Compiler
    """Instance of a [Compiler][phml.compile.Compiler]."""

    @property
    def ast(self) -> AST:
        return self.parser.ast

    @ast.setter
    def ast(self, _ast: AST):
        self.parser.ast = _ast

    def __init__(
        self,
        components: Optional[dict[str, dict[str, list | All_Nodes]]] = None,
    ):
        self.parser = Parser()
        self.compiler = Compiler(components=components)

    def add(
        self,
        *components: dict[str, dict[str, list | All_Nodes] | AST]
        | tuple[str, dict[str, list | All_Nodes] | AST]
        | Path,
    ):
        """Add a component to the element replacement list.

        Components passed in can be of a few types. The first type it can be is a
        pathlib.Path type. This will allow for automatic parsing of the file at the
        path and then the filename and parsed ast are passed to the compiler. It can
        also be a dictionary of str being the name of the element to be replaced.
        The name can be snake case, camel case, or pascal cased. The value can either
        be the parsed result of the component from phml.utils.parse_component() or the
        parsed ast of the component. Lastely, the component can be a tuple. The first
        value is the name of the element to be replaced; with the second value being
        either the parsed result of the component or the component's ast.

        Note:
            Any duplicate components will be replaced.

        Args:
            components: Any number values indicating
            name of the component and the the component. The name is used
            to replace a element with the tag==name.
        """
        from phml.utils import filename_from_path

        for component in components:
            if isinstance(component, Path):
                self.parser.load(component)
                self.compiler.add((filename_from_path(component), self.parser.ast))
            else:
                self.compiler.add(component)
        return self

    def remove(self, *components: str | All_Nodes):
        """Remove an element from the list of element replacements.

        Takes any number of strings or node objects. If a string is passed
        it is used as the key that will be removed. If a node object is passed
        it will attempt to find a matching node and remove it.
        """
        self.compiler.remove(*components)
        return self

    def load(self, path: str | Path):
        """Load a source files data and parse it to phml.

        Args:
            path (str | Path): The path to the source file.
        """
        self.parser.load(path)
        return self

    def parse(self, data: str | dict):
        """Parse a str or dict object into phml.

        Args:
            data (str | dict): Object to parse to phml
        """
        self.parser.parse(data)
        return self

    def render(
        self, file_type: str = file_types.HTML, indent: Optional[int] = None, **kwargs
    ) -> str:
        """Render the parsed ast to a different format. Defaults to rendering to html.

        Args:
            file_type (str): The format to render to. Currently support html, phml, and json.
            indent (Optional[int], optional): The number of spaces per indent. By default it will
            use the standard for the given format. HTML has 4 spaces, phml has 4 spaces, and json
            has 2 spaces.

        Returns:
            str: The rendered content in the appropriate format.
        """
        return self.compiler.compile(self.parser.ast, file_type=file_type, indent=indent, **kwargs)

    def write(
        self,
        dest: str | Path,
        file_type: str = file_types.HTML,
        indent: Optional[int] = None,
        **kwargs,
    ):
        """Renders the parsed ast to a different format, then writes
        it to a given file. Defaults to rendering and writing out as html.

        Args:
            dest (str | Path): The path to the file to be written to.
            file_type (str): The format to render the ast as.
            indent (Optional[int], optional): The number of spaces per indent. By default it will
            use the standard for the given format. HTML has 4 spaces, phml has 4 spaces, and json
            has 2 spaces.
            kwargs: Any additional data to pass to the compiler that will be exposed to the
            phml files.
        """
        with open(dest, "+w", encoding="utf-8") as dest_file:
            dest_file.write(self.render(file_type=file_type, indent=indent, **kwargs))
        return self
