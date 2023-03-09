from phml import PHML

phml = PHML(enable={"markdown": True})

# text = """\
# <Markdown src="
# # Code highlighting

# ```python
# print('hello world')
# ```
# " />\
# """

# print(phml.parse("<p>{{source}}</p>").render(source="Hello World!"))
phml.add("Data.phml")
print(phml.load("test.phml").render())
