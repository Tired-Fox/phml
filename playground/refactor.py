from phml import PHML

phml = PHML()
phml.add("cmpt.phml")

phml.load("index.phml")
phml.write("index.html")
input(phml.render())