import ast
import re
for_loop = 'for idx, x, y in enumerate(zip(xaxis, yaxis))'
print(
    re.sub(
        r"\s+",
        " ",
        re.match(r"for(,?\s+(.*))in", for_loop).group(1),
    )
    .strip()
    .split(", ")
)
