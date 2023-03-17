from time import sleep
from phml import PHML
from watchserver import LiveServer
phml = PHML(enable={"markdown": True})

server = LiveServer()
# text = """\
# <Markdown src="
# # Code highlighting

# ```python
# print('hello world')
# ```
# " />\
# """

# print(phml.parse("<p>{{source}}</p>").render(source="Hello World!"))
phml.add("error.phml")
print(phml.load("test.phml").render())
phml.write("index.html")
server.start()
try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    server.stop()

