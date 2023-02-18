from phml import PHML

phml = PHML()

print(phml.load("markdown.phml").render(dynamic_html="""<h1>Hello World</h1>"""))