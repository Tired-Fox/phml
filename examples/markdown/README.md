# PHML Markdown Support

PHML's markdown support is optional. If you wish to use the `Markdown` element you will need to install the `markdown` feature with `pip3 install phml[markdown]` or with `pip3 install markdown Pygments`. The `markdown` library is for parsing the markdown itself while `Pygments` is a way of generating a code highlighting stylesheet for the `codehilite` extension. PHML defaults to using the `codehilite` and `fenced_code` extensions for markdown code highlighting, and `tables` for basic markdown tables. I recommend referring to the [`markdown` docs](https://python-markdown.github.io/reference/) to see how certain extensions work.

PHML allows for additional built-in extensions to be added through the component with the `:extras`/`extras` attribute. This can either be a python list of extension names, with `:extras`, or a space seperate list of extensions as a string, with `:extras` or `extras`. To configure the extensions, again reference the docs, use the `:config` attribute which is a python dict of keys that are extension names and values that are dicts that hold config keys to config values.

```python
from typing import Any

Extension = str
Option = str
Value = Any

Config = dict[Extension, dict[Option, Value]]
```

The `Markdown` element can only render a markdown file. This means the element is self closing. To use the element you pass a file path string relative to the current file location, or the cwd if you did not parse phml from a file. The path is passed to the `:src` or `src` attribute. As mentioned above, the `:extras`/`extras` and `:config` attributes can also be used. When the rendered markdown replaces the `Markdown` component it is wrapped in an `article` element. Any addition attributes that aren't the ones mentioned above are automatically transfered to the `article` element. The attributes are left unprocessed, so python attributes are not valid on the `Markdown` element.

```
<!-- src/markdown.md -->
# Sample Markdown

Some text goes here
```

```html
<!-- scr/index.phml -->
...
<Markdown
  class="pros"
  src="markdown.md"
  extras="footnotes"
  :config"{
    "footnotes": {
      "BACKLINK_TEXT": "$"           
    }
  }"
>
...

<!-- src/index.html -->
...
<article class="pros">
  <h1>Sample Markdown</h1>
  <p>Some text goes here</p>
</article>
...
```
