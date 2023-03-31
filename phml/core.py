from __future__ import annotations
from collections.abc import Iterator
from importlib import import_module
from itertools import compress
import os
from pathlib import Path
from contextlib import contextmanager
import re
import sys
from typing import Any

from .parser import HypertextMarkupParser
from .compiler import HypertextMarkupCompiler
from .nodes import NodeType, Parent, AST, Node
from .embedded import Module, __IMPORTS__, __FROM_IMPORTS__
from .helpers import PHMLTryCatch
from .components import ComponentManager, ComponentType

class PHML:
    parser: HypertextMarkupParser
    """PHML parser."""
    compiler: HypertextMarkupCompiler
    """PHML compiler to HTML."""
    components: ComponentManager
    """PHML component parser and manager."""
    context: dict[str, Any]
    """PHML global variables to expose to each phml file compiled with this instance.
    This is the highest scope and is overridden by more specific scoped variables.
    """

    def __init__(self) -> None:
        self.parser = HypertextMarkupParser()
        self.compiler = HypertextMarkupCompiler()
        self.components = ComponentManager()
        self.context = {
            "Module": Module
        }
        self._ast: AST|None = None
        self._from_path = None
        self._from_file = None
        self._to_file = None

    @staticmethod
    @contextmanager
    def open(_from: str, _to: str | None = None) -> Iterator[PHML]:
        with PHMLTryCatch():
            core = PHML()
            core._from_file = Path(_from).open("r", encoding="utf-8")
            core._from_path = _from
            if _to is not None:
                core._to_file = Path(_to).open("+w", encoding="utf-8")
            yield core
            core._from_file.close()
            if core._to_file is not None:
                core._to_file.close()

    def add_module(self, module: str, *, name: str | None = None, imports: list[str] | None = None):
        """Pass and imported a python file as a module. The modules are imported and added
        to phml's cached imports. These modules are **ONLY** exposed to the python elements.
        To use them in the python elements or the other scopes in the files you must use the python
        import syntax `import <module>` or `from <module> import <...objects>`. PHML will parse
        the imports first and remove them from the python elements. It then checks it's cache of
        python modules that have been imported and adds those imported modules to the local context
        for each embedded python execution.

        Note:
            - All imports will have a `.` prefixed to the module name. For example `current/file.py` gets the module
            name `.current.file`. This helps seperate and indicate what imports are injected with this method.
            Module import syntax will retain it's value, For example suppose the module `..module.name.here`
            is added. It is in directory `module/` which is in a sibling directory to `current/`. The path
            would look like `parent/ -> module/ -> name/ -> here.py` and the module would keep the name of
            `..module.name.here`.

            - All paths are resolved with the cwd in mind.
        
        Args:
            module (str): Absolute or relative path to a module, or module syntax reference to a module.
            name (str): Optional name for the module after it is imported.
            imports (list[str]): Optional list of objects to import from the module. Turns the import to
                `from <module> import <...objects>` from `import <module>`.
        """
    
        if module.startswith("~"):
            module = module.replace("~", str(Path.home()))

        mod = None
        file = Path(module)
        cwd = os.getcwd()

        if file.is_file():
            current = Path(cwd).as_posix()
            path = file.resolve().as_posix()
            
            cwd_p = current.split("/")
            path_p = path.split("/")
            index = 0
            for cp, pp in zip(cwd_p, path_p):
                if cp != pp:
                    break
                index += 1

            name = re.sub(r"^(/?\.\./?)*", "", module).rsplit(".", 1)[0].replace("/", ".")
            path = "/".join(path_p[:index])

            # Make the path that is imported form the only path in sys.path
            # this will prevent module conflicts and garuntees the correct module is imported
            sys_path = list(sys.path)
            sys.path = [path]
            mod = import_module(name)
            sys.path = sys_path

            name = f".{name}"
            
        else:
            if module.startswith(".."):
                current = Path(os.getcwd()).as_posix()
                cwd_p = current.split("/")
                
                path = "/".join(cwd_p[:-1])

                sys_path = list(sys.path)
                sys.path = [path]
                mod = import_module(module.lstrip(".."))
                sys.path = sys_path
            else:
                mod = import_module(module)
            name = f".{module.lstrip('..')}"

        if mod is None:
            raise ValueError(f"Failed to import module {name}")

        # Add imported module or module objects to appropriate collection
        if imports is not None and len(imports) > 0:
            for _import in imports:
                __FROM_IMPORTS__.update({name: {_import: getattr(mod, _import)}})
        else:
            __IMPORTS__[name] = mod

        return self

    def remove_module(self, module: str, imports: list[str] | None = None):
        if module in __IMPORTS__:
            __IMPORTS__.pop(module, None)
        if module in __FROM_IMPORTS__:
            if imports is not None and len(imports) > 0:
                for _import in imports:
                    __FROM_IMPORTS__[module].pop(_import, None)
                if len(__FROM_IMPORTS__[module]) == 0:
                    __FROM_IMPORTS__.pop(module, None)
            else:
                __FROM_IMPORTS__.pop(module, None)

        return self

    @property
    def ast(self) -> AST:
        """The current ast that has been parsed. Defaults to None."""
        return self._ast or AST()

    def load(self, path: str|Path):
        """Loads the contents of a file and sets the core objects ast
        to the results after parsing.
        """
        with PHMLTryCatch(), Path(path).open("r", encoding="utf-8") as file:
            self._from_path = path
            self._ast = self.parser.parse(file.read())
        return self

    def parse(self, data: str|dict|None = None):
        """Parse a given phml string or dict into a phml ast.
        
        Returns:
            Instance of the core object for method chaining.
        """

        if data is None and self._from_file is None:
            raise ValueError("Must either provide a phml str/dict to parse or use parse in the open context manager")

        with PHMLTryCatch(self._from_path, "phml:__parse__"):
            if isinstance(data, dict):
                ast = Node.from_dict(data)
                if not isinstance(ast, AST) and ast is not None:
                    ast = AST([ast])
                self._ast = ast
            elif data is not None:
                self._from_path = None
                self._ast = self.parser.parse(data)
            elif self._from_file is not None:
                self._ast = self.parser.parse(self._from_file.read())

        return self

    def format(self, *, code: str = "", file: str|None=None, compress: bool = False) -> str|None:
        """Format a phml str or file.

        Args:
            code (str, optional): The phml str to format.

        Kwargs:
            file (str, optional): Path to a phml file. Can be used instead of
                `code` to parse and format a phml file.
            compress (bool, optional): Flag to compress the file and remove new lines. Defaults to False.

        Note:
            If both `code` and `file` are passed in then both will be formatted with the formatted `code`
            bing returned as a string and the formatted `file` being written to the files original location.

        Returns:
            str: When a phml str is passed in
            None: When a file path is passed in. Instead the resulting formatted string is written back to the file.
        """

        result = None
        if code != "":
            self.parse(code)
            result = self.compiler.render(
                self._ast,
                _components=self.components,
                _compress=compress
            )

        if file is not None:
            self.load(file)
            with Path(file).open('+w', encoding="utf-8") as phml_file:
                phml_file.write(self.compiler.render(
                    self._ast,
                    self.components,
                    _compress="\n" if not compress else ""
                ))

        return result

    def compile(self, **context: Any) -> Parent:
        """Compile the python blocks, python attributes, and phml components and return the resulting ast.
        The resulting ast replaces the core objects ast.
        """
        context = {**self.context, **context}
        if self._ast is not None:
            with PHMLTryCatch(self._from_path, "phml:__compile__"):
                ast = self.compiler.compile(self._ast, self.components, **context)
            self._from_path = ""
            return ast
        raise ValueError("Must first parse a phml file before compiling to an AST")

    def render(self, _compress: bool = False, **context: Any) -> str | None:
        """Renders the phml ast into an html string. If currently in a context manager
        the resulting string will also be output to an associated file.
        """
        context = {**self.context, **context}
        if self._ast is not None:
            with PHMLTryCatch(self._from_path, "phml:__render"):
                result = self.compiler.render(
                    self.compile(**context),
                    _components=self.components,
                    _compress="" if _compress else "\n",
                )
                if self._to_file is not None:
                    self._to_file.write(result)
                elif self._from_file is not None and self._from_path is not None:
                    self._to_file = Path(self._from_path).with_suffix(".html").open("+w", encoding="utf-8")
                    self._to_file.write(result)
            self._from_path = ""
            return result
        raise ValueError("Must first parse a phml file before rendering a phml AST")

    def add(
        self,
        file: str | None = None,
        *,
        cmpt: tuple[str, str] | None = None,
        data: tuple[str, ComponentType] | None = None,
        ignore: str = "",
    ):
        """Add a component to the component manager. The components are used by the compiler
        when generating html files from phml.
        """
        self.components.add(file, cmpt=cmpt, data=data, ignore=ignore)

    def remove(self, key: str):
        """Remove a component from the component manager based on the components name/tag.
        """
        self.components.remove(key)

    def expose(self, _context: dict[str, Any] | None = None, **context: Any):
        """Expose global variables to each phml file compiled with this instance.
        This data is the highest scope and will be overridden by more specific
        scoped variables with equivelant names.
        """
        self.context.update(_context or {})
        self.context.update(context)

    def redact(self, key: str):
        """Remove global variable from this instance."""
        del self.context[key]
