from pathlib import Path

from flask import abort

from .main import app, phml, construct_components, prefix
from .debug import debug
from phml import query, Compiler, inspect
from phml.builder import p

compiler = Compiler()


@app.route("/")
def home():
    with debug():
        return phml.load(prefix + "index.phml").render()


@app.route("/<path:subpath>")
def page(subpath):
    def custom_file(source):
        ast = phml.load(source).ast
        head_node = query(ast, "head")
        head_node.append(p("meta", {"http-equiv": "refresh", "content": "7"}))
        return compiler.compile(
            ast, scopes=phml._scopes, components=phml._compiler.components, **phml._exposable
        )

    with debug():
        construct_components()

        directory = Path(prefix).joinpath(Path(subpath))
        index_file = Path(prefix).joinpath(Path(subpath), "index.phml")
        named_file = [
            subdir for subdir in Path(subpath).as_posix().split("/") if subdir.strip() != ""
        ]
        named_file = Path(prefix).joinpath(
            Path("/".join(named_file[:-1])), named_file[-1] + ".phml"
        )

        if directory.is_dir() and index_file.is_file():
            return phml.load(index_file).render()
            # return custom_file(index_file)
        elif named_file.is_file():
            return phml.load(named_file).render()
            # return custom_file(named_file)

    abort(404)


@app.route("/debug")
@app.route("/debug/")
@app.route("/debug/<path:subpath>")
def test(subpath=None):
    with debug():
        raise Exception("Something")
