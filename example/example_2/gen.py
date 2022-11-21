from phml import PHMLCore
import time

start = time.monotonic()
PHMLCore().load("unicode.phml").write("UNICODE.html")
print(
    "Built a 10,000 unicode, 10,000+ element, webpage in",
    round(time.monotonic() - start, 2),
    "secs",
)
