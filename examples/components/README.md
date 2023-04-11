# PHML Component Example

PHML components are reusable snippets of html. They are formatted similar to Vue.js. You may have any number of elements in the root directory. The `python`, `script`, and `style` elements are cached and combined and will only be added to the final page once. To pass dynamic data to a component you pass it through it's attributes. These attributes are called `props`. To define what props a component can take, define a single variable in a `python` element named `Props`. This variable must be a python type of `dict[str, Any]`. The keys are the available props that can be passed in, and the value is the default value if the prop is not passed in. Attributes that have the same name as the keys defined in the `Props` dict are collected and passed to the component's children as scoped data.

When a component is injected/replaced in a file or another component it is wrapped in div component with a data scope id. This id is of the format of `<Component Name>~<Component Hash>`. This ensures each component has a unique indentifier. This identifer is the same for each replacement of the component. This is great for targeting a specific component with styles. More importantly this allows phml to implement scoped `style` elements. When a `style` element has a `scoped` attribute, phml will automatically add a `[data-phml-cmpt-scope="<Component Identifier>"]` to each css selector. PHML hasn't implemented a css parser so it relies on a regex pattern to find and modify css selectors. If you find that scoping styles doesn't work for you, please create an issue on the projects github page.  

```html
<!-- component.phml -->
<python>
  Props = {
    "title": "No Title"
  }
</python>
<h1>{{ title }}</h1>

<!-- index.phml -->
...
<Component title="Hello World!" />
...

<!-- index.html -->
...
<div data-phml-cmpt-scope="Component~1234567">
  <h1>Hello World!</h1>
</div>
...
```

## Structure

The components that are used are in the `components/` directory and the phml files are in the `pages/`
directory. The rendered html files are placed in the `site/`.
