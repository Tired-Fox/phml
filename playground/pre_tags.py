from phml import HypertextManager
from phml.nodes import inspect

code = """
<h1>Some header</h1>
<pre>Code <span>goes</span> here
whitespace preservation
example</pre>
"""

print(inspect(HypertextManager().parse(code).compile(), text=True, color=True))
print(HypertextManager().parse(code).render())
