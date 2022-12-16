from phml import PHML

phml = PHML()
INDEX_PAGE = "index.phml"

# Load components
phml.add("alert.phml", "message.phml")

# Load page, compile and write to file, compile and print to screen
print(phml.load(INDEX_PAGE).write(INDEX_PAGE, replace_suffix=True).render())
