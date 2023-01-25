from phml import PHML

phml = PHML()

phml.add("cmpt.phml")

print(phml.load("index.phml").render())