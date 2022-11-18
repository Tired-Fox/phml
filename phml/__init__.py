"""Python Hypertext Markup Language (phml)

The idea behind phml is to replicate the functionality of some javascript
frameworks like ReactJS, VueJS, AstroJS, etc... All of these frameworks
allow the user to inject javascript in some way. Most of the time you can
inject javascript data into html using brackets. A lot of the frameworks also
have custom attributes on elements for conditional rendering.

phml strives to do similar things, However, the nuance here
is that phml uses python. There is a new html element that is reserved for phml.
This element is the `<python>` element. It means to replicate the purpose of the
`<script>` element. On top of this there are smaller blocks that use brackets
that expect the expression to return some sort of value. Finally, there are custom
attributes. `py-if`, `py-elif`, and `py-else` are reserved for conditional rendering.
All attributes prefixed with `py-` will have their value evaluated as python. More details
on each of these topics is described below.

Let's start with the new `python` element. Python is a whitespace language. As such phml
has the challenge of maintaining the indentation in a appropriate way. With this in phml,
you can have as much leading whitespace as you want as long as the indentation is consistent.
This means that indentation is based of the first lines offset. Take this phml example:

```python
<python>
    if True:
        print("Hello World")
</python>
```

This phml python block will adjust the offset so that the python is processed as this:

```python
if True:
    print("Hello World")
```

So now we can write python code, now what? You can define functions and variables
how you normally would and they are now available to the scope of the entire file.
Take, for instance, the example from above, the one with `py-src="urls('youtube')"`.
You can define the URLs function in the `python` element and it can be accessed in the `py-src`
attribute. So the code would look like this:

```html
<python>
def urls(link: str) -> str:
    links = {
        "youtube": "https://youtube.com"
    }
    if link in links:
        return links[link]
    else:
        return ""
</python>

...

<a py-href="urls('youtube')">Youtube</a>
```

phml treats `python` elements as their own python files. This is meant literally.
phml creates a temporary python file with a unique name and imports everything from that file.
With that in mind that means you have the full power of whatever version of python you are using.
The phml parser has functionality to permanently write these python files out if you so desire.

Next up is inline python blocks. These are represented with `{}`. Any text with this block or
normal html attribute with the value containing it will process the text in-between the brackets as
python. This is mostly useful when you want to inject some python processed or stored value
into html. Assume that there is a variable defined in the `python` element called `message`
and it contains `Hello World!`. Now this variable can be used like this, `<p>{ message }</p>`,
which renders to, `<p>Hello World!</p>`. Inline python blocks are only rendered in inside a Text
element or inside an html attribute.

Now multiline blocks are a lot like inline python blocks, but they also have soem differences.
They are not one line single python expressions, but full multiline python source code.
You can do whatever you like inside this block, however if you expect a value to come from
a multiline block it comes from the last local. So if you have a variable or function as the
last local; it will be used as the compiled result that replaces the python block.

Conditional Rendering with `py-if`, `py-elif`, and `py-else` is an extremely helpful tool in phml.
`py-if` can be used alone and that the python inside it's value must be truthy for the element to be
rendered. `py-elif` requires an element with a `py-if` or `py-elif` attribute immediately before it,
and it's condition is rendered the same as `py-if` but only rendered if a `py-if` or `py-elif` first
fails. `py-else` requires there to be either a `py-if` or a `py-else` immediately before it. It only
renders if the previous elements condition fails. If `py-elif` or `py-else` is on an element, but
the previous element isn't a `py-if` or `py-elif` then it will be rendered as normal without the
condition. Most importantly, the first element in a chain of conditions must be a `py-if`.

Other than conditions, there is also a built it py-for attribute. Techinally you can do a multiline
python block or use a python element to create a html string based on a list. However, for ease
of use phml provides phml. Any element with py-for will take a python for-loop expression that
will be applied to that element. So if you did something like this:
```html
<ul>
    <li py-for='for i in range(3)'>
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

Python attributes are shortcuts for using inline python blocks in html attributes. Normally, in
phml, you would inject python logic into an attribute similar to this: `src="{url('youtube')}"`.
As a way to simplify the value and to make it obvious that the attribute is using python you can
prefix any attribute with `py-`. This keeps the attribute name the same after the prefix, but tells
the parser that the entire value should be processed as python. So the previous example can also be
expressed as `py-src="url('youtube')"`.

PHML as a language is in early planning stages, but hopes to have a easy to use and well featured
parser. With this the hope is that anyone using the parser will have full control over the generated
phml ast. This also means that users may write extensions to add features to to manipulate the ast
to fit their needs. On top of all that the parser will also have a render/convert functionality
where the user may pass extensions, and additional kwargs. These kwargs are exposed while rendering
the file to html. This means that the user can generate some other content from some other source
and inject it into their document. A good example of this is using the `markdown` python library
to render markdown to html, then to inject that into the renderer by passing it in as a kwarg.
"""

__version__ = "0.1.0"

from .file_types import HTML, PHML, JSON
from .parser import Parser
from .utils import *
from .AST import AST
