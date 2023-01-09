# pylint: disable=line-too-long
"""Python Hypertext Markup Language (phml)

![version](assets/badges/version.svg) [![License](https://img.shields.io/badge/License-MIT-9cf)](https://github.com/Tired-Fox/phml/blob/main/LICENSE) [![tired-fox - phml](https://img.shields.io/static/v1?label=tired-fox&message=phml&color=9cf&logo=github)](https://github.com/tired-fox/phml "Go to GitHub repo")
[![stars - phml](https://img.shields.io/github/stars/tired-fox/phml?style=social)](https://github.com/tired-fox/phml)
[![forks - phml](https://img.shields.io/github/forks/tired-fox/phml?style=social)](https://github.com/tired-fox/phml)

# Python Hypertext Markup Language (phml)

[![Deploy Docs](https://github.com/Tired-Fox/phml/actions/workflows/deploy_docs.yml/badge.svg)](https://github.com/Tired-Fox/phml/actions/workflows/deploy_docs.yml) [![GitHub release](https://img.shields.io/github/release/tired-fox/phml?include_prereleases=&sort=semver&color=brightgreen)](https://github.com/tired-fox/phml/releases/) 
[![issues - phml](https://img.shields.io/github/issues/tired-fox/phml)](https://github.com/tired-fox/phml/issues) ![quality](assets/badges/quality.svg) ![testing](assets/badges/testing.svg) ![test coverage](assets/badges/test_cov.svg)

**TOC**
- [Python Hypertext Markup Language (phml)](#python-hypertext-markup-language-phml)
  - [Overview](#overview)
  - [How to use](#how-to-use)


<div align="center">

[![view - Documentation](https://img.shields.io/badge/view-Documentation-blue?style=for-the-badge)](https://tired-fox.github.io/phml/phml.html "Go to project documentation")

</div>

## Overview

The idea behind the creation of Python in Hypertext Markup Language (phml), is to allow for web page generation with direct access to python. This language pulls directly from frameworks like VueJS. There is conditional rendering, components, python elements, inline/embedded python blocks, and much more. Now let's dive into more about this language.

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

or

<a :href="URL('youtube')">Youtube</a>
```

phml combines all `python` elements and treats them as a python file. All local variables and imports are parsed and stored so that they may be accessed later. With that in mind that means you have the full power of the python programming language.

Next up is inline python blocks. These are represented with `{}`. Any text in-between the brackets will be processed as python. This is mostly useful when you want to inject a value from python. Assume that there is a variable defined in the `python` element called `message`
and it contains `Hello World!`. Now this variable can be used like this, `<p>{ message }</p>`,
which renders to, `<p>Hello World!</p>`.

> Note:  Inline python blocks are only rendered in a Text element or inside an html attribute.

Multiline blocks are a lot like inline python blocks, but they also have some differences.
You can do whatever you like inside this block, however if you expect a value to come from the block you must have at least one local variable. The last local variable defined in this block is used at the result/value.

Conditional rendering with `py-if`, `py-elif`, and `py-else` is an extremely helpful tool in phml.
`py-if` can be used alone and that the python inside it's value must be truthy for the element to be rendered. `py-elif` requires an element with a `py-if` or `py-elif` attribute immediately before it, and it's condition is rendered the same as `py-if` but only rendered if a `py-if` or `py-elif` first
fails. `py-else` requires there to be either a `py-if` or a `py-else` immediately before it. It only
renders if the previous element's condition fails. If `py-elif` or `py-else` is on an element, but
the previous element isn't a `py-if` or `py-elif` then an exception will occur. Most importantly, the first element in a chain of conditions must be a `py-if`. For ease of use, instead of writing `py-if`, `py-elif`, or `py-else` can be written as `@if`, `@elif`, or `@else` respectively.

Other than conditions, there is also a built in `py-for` attribute. Any element with py-for will take a python for-loop expression that will be applied to that element. So if you did something like this:

```html
<ul>
    <li @for='i in range(3)'>
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
the parser that the entire value should be processed as python. So the previous example can also be expressed as `py-src="URL('youtube')"` or `:src="URL('youtube')"`.

This language also has the ability to convert back to html and json with converting to html having more features. Converting to json is just a json representation of a phml ast. However, converting to html is where the magic happens. The compiler executes python blocks, substitutes components, and processes conditions to create a final html string that is dynamic to its original ast. A user may pass additional kwargs to the compiler to expose additional data to the execution of python blocks. If you wish to compile to a non supported language the compiler can take a callable that returns the final string. It passes all the data; components, kwargs, ast, etc… So if a user wishes to extend the language thay may.

> :warning: This language is in early planning and development stages. All forms of feedback are encouraged.
"""
# pylint: enable=line-too-long

from pathlib import Path
from typing import Callable, Optional

from .core import (
    AST,
    PHML,
    All_Nodes,
    Compiler,
    Format,
    Formats,
    Parser,
    replace_components,
    substitute_component
)
from .utilities import *

__version__ = "1.3.0"
