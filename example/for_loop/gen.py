from phml import PHML
import time

start = time.monotonic()
PHML().load("unicode.phml").write("index.html")
print(
    "Built a 10,000 unicode, 10,000+ element, webpage in",
    round(time.monotonic() - start, 2),
    "secs",
)
