'''Virtual Python

This module serves to solve the problem of processing python
in scopes and to evaluate python expressions.

These expressions and scopes are python "blocks" that are injected
into html which then creates my language phml.

Here are examples of the python blocks:

1. Python element. This is treated as python files similarly to how
`<script>` elements are treated as javascript files.

```html
<python>
    from datetime import datetime
    
    current_time = datetime.now().strftime('%H:%M:%S')
</python>
```

2. Inline python block. Mainly used for retreiving values 
or creating conditions. The local variables in the blocks are given
from the python elements and from kwargs passed to the parser

```html
<p>{current_time}</p>
```

3. Multiline python blocks. Same as inline python blocks just that they
take up multiple lines. You can write more logic in these blocks, but
there local variables are not retained. By default phml will return the last
local variable similar to how Jupyter or the python in cli works.

```html
<p>
    Hello, everyone my name is {firstname}. I
    am a {work_position}.
<p>
<p>Here is a list of people and what they like</p>
<p>
    {
        result = []
        for i, person, like in enumerate(zip(people, likes)):
            result.append(f"{i}. {person} likes {like}")
        result = "\\n".join(result)
    }
</p>
```
'''

from .ImportObjects import Import, ImportFrom
from .vp import VirtualPython, get_vp_result, process_vp_blocks

__all__ = ["VirtualPython", "get_vp_result", "process_vp_blocks", "Import", "ImportFrom"]
