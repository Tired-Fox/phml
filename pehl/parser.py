class Element:
    def __init__(self, data: str, is_open: bool = False):
        self.tag = ""
        self.attributes = {}
        self.children = []
        self.open = is_open
        self.closing = False

        self.__parse_data(data)

    def __parse_data(self, data: str):
        import re

        tokens = [token for token in data.split(" ") if token not in ["", " ", None]]

        if data.endswith("/"):
            data = data[:-1]
            self.closing = True

        if re.match(r"^[a-zA-Z]+|!DOCTYPE$", tokens[0]) is not None:
            self.tag = tokens[0]
            for token in tokens[1:]:
                if "=" in token:
                    name, value = token.split("=", 1)
                    self.attributes[name] = value
                else:
                    self.attributes[token] = True
        else:
            for token in tokens:
                if "=" in token:
                    name, value = token.split("=", 1)
                    self.attributes[name] = value
                else:
                    self.attributes[token] = True

    def __repr__(self) -> str:
        tag = self.tag if self.tag not in ["", None] else "~"
        is_open = "open" if self.open else "close"
        is_open = is_open if not self.closing else "Self Closing"
        attrs = ", ".join(
            [f'{key}="{value}"' for key, value in self.attributes.items()]
        )
        return f"{tag.upper()}(type: {is_open}, attributes: [{attrs}])"


def parse(file: str, file_name: str):
    pass
