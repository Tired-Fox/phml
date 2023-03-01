from phml import PHML

phml = PHML()

text = """\
<Markdown src="
# Code highlighting

```python
print('hello world')
```
" />\
"""

print(phml.parse(text).render())