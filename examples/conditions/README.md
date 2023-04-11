# PHML Conditional Elements

To help with dynamic data being passed into the temlates phml includes conditional elements. To make an element conditional add a conditional attribute: `@if`, `@elif`, or `@else`. These conditional attributes work the same as pythons `if`, `elif`, and `else`. Conditional elements that are branching, i.e. `if` to `elif` to `else` are required to be direct siblings of each other. 

Both `@if` and `@elif` require a value that is python code that resolves to a boolean. `@else` is a final default state to the conditional branch so it does not have a value. The first element with a `True` condition in the branch will be rendered, the rest of the elements in the branch are discarded.

When experssions/variables are used but not provided in the scope the value is defaulted to None. Along with this, phml automatically exposes a `blank()` method that can check if something is `None` or `"empty"`. Combine the two together and you can create safe conditional branches based on dynamic data.

```html
<div @if="False">
  @IF
</div>

<div @elif="None is not None">
  @ELIF 1
</div>

<div @elif="not blank('data')"> <!-- This one is rendered -->
  @ELIF 2
</div>

<div @else>
  @ELSE
</div>
```

The example that can be run here is a multipage site that gives some generic information. Feel free to change things and experiment with conditional elements!
