from pathlib import Path
from flask import Flask, url_for
from phml import PHML


app = Flask(__name__,
            static_folder="../site/static")

phml = PHML()
    
phml.expose(url_for=url_for)

prefix = "pages/"

def construct_components():
    for file in Path("components").glob("**/*.phml"):
        phml.add(file)
        
construct_components()

class Errors:
    def __init__(self) -> None:
        self.messages = {
            "404": "oops, it looks like the page you are trying to reach doesn't exist.",
        }
        self.traceback = list()
        self.type = "error"
    
ERROR = Errors()
