# Python Hypertext Markup Language (phml)

<!-- Header Badges -->

<div align="center">
  
![version](assets/badges/version.svg)
[![Release](https://img.shields.io/github/v/release/tired-fox/phml.svg?style=flat-square&color=9cf)](https://github.com/Tired-Fox/phml/releases)
[![License](assets/badges/license.svg)](https://github.com/Tired-Fox/phml/blob/main/LICENSE)
![Maintained](assets/badges/maintained.svg)

![testing](assets/badges/tests.svg)
![test coverage](assets/badges/coverage.svg)

</div>

<!-- End Badges -->

## Overview

The idea behind the creation of Python in Hypertext Markup Language (phml), is to allow for web page generation with direct access to python. This language takes inspiration directly from frameworks like Vue.js, Astro.js, Solid.js, and SvelteKit. There is conditional rendering, components, python elements, inline/embedded python blocks, and slot, named slots, and much more. Now let's dive into more the language.

### Python Element

Let's start with the new `python` element. Python is a whitespace language. As such, phml
has the challenge of maintaining the indentation in an appropriate way as to preserve the intended whitespace. The key focus is the indended whitespace. While this can be tricky the first line with content serves as a reference. The amount of indentation for the first line is removed from each line and the remaining whitespace is left alone. For example if there is a python block that looks like this.

```html
<python> message = "hello world" if "hello" in message: print(message) </python>
```

The resulting python code would look like this.

```python
message = "hello world"
if "hello" in message:
  print(message)
```

So now we can write python code, now what? You can define functions and variables
how you normally would and they are now available to the scope of the entire file. Consider the following example; You can define function called `URL` in the `python` element and it can be accessed in any other part of the file. So the code would look like this:

```html
<python>
  def URL(link: str) -> str: links = { "youtube": "https://youtube.com" } if
  link in links: return links[link] else: return ""
</python>

...

<a href="{URL('youtube')}">Youtube</a>
```

phml combines all `python` elements and treats them as one python file. This is of the likes of the `script` or `style` tags. With the fact that you can write any code in the python element and used it anywhere else in the file you of the full power of the python programming language at your desposal.

### Inline Python and Python Attributes

Next up is inline python blocks. These are represented with `{{}}` in text elements. Any text in-between the brackets will be processed as python. This is mostly useful when you want to inject a value from python. Assume that there is a variable defined in the `python` element called `message`
and it contains `Hello World!`. Now this variable can be used like this, `<p>{{ message }}</p>`,
which renders to, `<p>Hello World!</p>`.

> Note: Inline python blocks are only rendered in a Text element or inside an html attribute.

Conditional rendering with `@if`, `@elif`, and `@else` is an extremely helpful tool in phml.
`@if` can be used alone and the python inside it's value must be truthy for the element to be rendered. `@elif` requires an element with a `@if` or `@elif` attribute immediately before it, and it's condition is rendered the same as `@if` but only rendered if a `@if` or `@elif` first fails. `@else` requires there to be either a `@if` or a `@else` immediately before it. It only renders if the previous element's condition fails. If `@elif` or `@else` is on an element, but the previous element isn't a `@if` or `@elif` then an exception will occur. Most importantly, the first element in a chain of conditions must be a `@if`.

Other than conditions, there is also a built in for loop element. The format looks something like `<For :each="item in collection>"` and it duplicates it's children at the node position of the `For` element. The `For` element requires there to be an `each` attribute for it to be rendered. You can consider the value of this element as pythons equivelent to `for item in collection:` as this is what the `each` attribute expands out to. The attributes defined in the `each` element, `item` from the previous example, is exposed to the children of the for loop. The attributes from the iteration are scoped recursively through the children. All conditionals work for the the `For` element. An added feature is when a `For` iteration has an error or iterates zero times, the `@elif` or `@else` following the `For` is used instead. This means that a `For` failing or generating zero is like a failed `@if` and can be treated as such. Below is an example of how a `For` element could be used.

```html
<ul
  <For :each="i in range(3)">
    <li>{i}</li>
  </For>
  <li @else>No items in range</li>
</ul>
```

The compiled html will be:

```html
<ul>
  <li>1</li>
  <li>2</li>
  <li>3</li>
</ul>
```

Python attributes are shortcuts for using inline python blocks in html attributes. Normally, in phml, you would inject python logic into an attribute similar to this `src="{url('youtube')}"`. If you would like to make the whole attribute value a python expression you may prefix any attribute with a `:`. This keeps the attribute name the same after the prefix, but tells the parser that the entire value should be processed as python. So the previous example with `URL` can also be expressed as `<a :href="URL('youtube')>Youtube</a>"`.

### Components

PHML includes a powerful component system. The components are partial phml files and are added to the core compiler. After adding the component whenever an element with the same name as the component is found, it is replaced. Components have scoped `python` elements, while all `style` and `script` elements are global to the file they are injected into. Components require that there is only one element, that isn't a `python`, `script`, or `style` tag, to be present. A sample component can look something like the example below.

```html
<!-- Component.phml -->
<div># content goes here</div>

<python> # python code goes here </python>
<style>
  /* styles go here */
</style>
<script>
  // js goes here
</script>
```

Components can be added to the compiler by using `HypertextManager.add('path/to/component.phml')`. You can define a components name when adding it to the compiler like this `HypertextManager.add(('Component', 'path/to/component.phml'))`, or you can just let the compiler figure it out for you. Each directory in the path given along with the file name are combine to create the components name. So if you pass a component path that is `path/to/component.phml` it will create a components name of `Path.To.Component` which is then used as `<Path.To.Component />`. The compiler will try to parse and understand the component name and make it Pascal case. So if you have a file name of `CoMP_onEnt.phml` it will result in `CoMPOnEnt`. It uses `_` as a seperator between words along with capital letters. It will also recognize an all caps word bordering a new word with a capital letter.

Great now you have components. But what if you have a few components that are siblings and you don't want them to be nested in a parent element. PHML provides a `<>` element which is a placeholder element. All children are treated as they are at the root of the component.

```html
<!-- file.phml -->
...
<body>
  <Component />
</body>
...
<!-- Component.phml -->
<>
<p>Hello</p>
<p>World</p>
<>
```

will result in the following rendered html

```html
<!-- file.html -->
...
<body>
  <p>Hello</p>
  <p>World</p>
</body>
...
```

Now how do you pass information to component to use in rendering? That is where the `Props` variable comes in. The `Props` variable is a dictionary defined in the components `python` element. This defines what attributes on the component are props along with their default values.

```html
<!-- component.phml -->
<python> Props = { message: "" } </python>

<p>{{ message }}</p>

<!-- file.phml -->
...
<Component message="Hello World!" />
...
```

Both normal attribute values and python attributes can be used for props. The above example really only works for self closing components. What if you want to pass children to the component? That is where slots come in.

```html
<python> Props = { message: "" } </python>

<div class="callout">
  <p @if="message is not None">{{ message }}</p>
  <slot />
</div>
```

The `Slot` element must be capitalized. When a `Slot` element is present any children inside of a component are inserted in place of it. If no children exist then the slot is just removed. What about having multiple slots and having certain components go to certain slot. PHML covers this with the `slot` and `name` attribute. The slot attribute holds the name of the slot that the child element should be placed in. The name attribute goes on the `Slot` element itself giving it it's name. There may only be one `Slot` of every name including the default `Slot` with no name attribute. An example of this will look something like this.

```html
<!-- component.phml -->
<div>
  <slot name="top" />
  <slot />
  <slot name="bottom" />
</div>

<!-- file.phml -->
...
<Component>
  <p slot="bottom">Bottom</p>
  <p slot="top">Top</p>
  Middle
</Component>
...

<!-- file.html -->
...
<p slot="top">Top</p>
Middle
<p slot="bottom">Bottom</p>
...
```

### Markdown (Optional)

PHML also has very basic markdown support. The `Markdown` element can be used to render markdown in place of the element itself. The markdown component is an optional feature of phml. To enable the feature you can run `pip3 install phml[markdown]` or `pip3 install markdown`, then use the component in a phml file. The markdown component can only reference/render a markdown file. To do so, use the `:src`/`src` attribute to specify the path to the markdown file, relative to the current file. If phml is rendering from a parsed dict or str, then the current working directory is used.

The markdown component uses a few default extensions while parsing. First it uses `codehilite` and `fenced_code` for highlighting code blocks, this also requires a css file generated with `pygmentize`. Lastly, it will use `tables` to add the ability to parse markdown tables. This makes the markdown close to a github flavor. 

Users may need to add additional markdown extension or to configure them. That is where the `:extras`/`extras` and `:configs` attributes come in. The `:extras` attribute is a list of string names of the markdown extensions to add. The `extras` attribute, also `:extras`, is a space seperated string of the extension names. To configure the extensions the python attribute `:configs` is used. The attribute must be a dict of the format `{ '<extension>': { `<option>`: <value> } }`. The options and available values are found in the `markdown` modules [documentation](https://python-markdown.github.io/extensions/).
  
When the markdown is compiled, the resulting html elements are nested in an `article` element. All attributes that are not `src`, `extras`, or `:config` on the markdown component are added to the parent `article` element and are left unprocessed. This means that python attributes other than `:config` or `:extras` on the markdown component are left "as is".

```html
<!-- file.phml -->
<Markdown
  src="../markdown/file.md"
  extras="smarty footnotes"
  :configs="{
     "footnotes": {
       "BACKLINK_TEXT": "$"           
     }
  }"
>
```
___
  
> :warning: This language is in early development stages. Everything is currently subject to change. All forms of feedback are encouraged.

<br>
For more information, check out the [API Docs](https://tired-fox.github.io/phml/phml.html)

## Basic Usage

The current version is able to parse phml using an html parser. This creates a phml ast which then can be converted back to phml or to json.

**Use**

First import the core parser and compiler, `from phml import HypertextManager`. Then you can do the following:

```python
phml = HypertextManager().load("path/to/file.phml")
print(phml.render())
```

There is method chaining so most if not all methods can be chained. The obvious exception being any method that returns a value.

By default `HypertextManager.render()` will return the `html` string. If you want to get a `json` string you may pass `Formats.JSON`. `HypertextManager.render(file_type=Formats.JSON)`.

If you want to write to a file you can call `phml.write("path/to/output/file.phml")`. Same with `render` it defaults to html. You can change this the same way as `render`. `core.write("path/to/otuput/file.json", file_type=Formats.JSON)`.

For both `render` and `write` you will first need to call `phml.load("path/to/source/file.phml")`. This parses the source file and stores the ast in the parser. `render` and `write` then use that ast to create the desired output. Optionally if you already have a phml or html string or a properly formatted dict you can call `core.parse(data)` which will parse that information similar to `load`.

Every time `phml.parse` or `phml.load` is called it will overwrite the stored ast variable.

There are many more features such as globally exposed variables, components, slots, exposing python files to be used in phml files, etc...

For more information check out the [API Docs](https://tired-fox.github.io/phml/phml.html)

<!-- Footer Badges -->

<br>
<div align="center">
  
![Made with Python](assets/badges/made_with_python.svg)
![Built with love](assets/badges/built_with_love.svg)

</div>

<!-- End Badges -->
