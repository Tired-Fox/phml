from phml import PHML
import time

if False:
    start = time.monotonic()
    PHML().load("unicode.phml").write("unicode.html")
    print(
        "Built a 10,000 unicode, 10,000+ element, webpage in",
        round(time.monotonic() - start, 2),
        "secs",
    )
else:
    PHML().load("sample1.phml").write("sample1.html")
