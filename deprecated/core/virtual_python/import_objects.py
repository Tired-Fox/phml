"""Dataclasses to hold information about python imports."""
from __future__ import annotations


class PythonImport:  # pylint: disable=too-few-public-methods
    """Base class defining required methods of import dataclasses."""

    def __init__(self):
        ...


class Import(PythonImport):
    """Helper object that stringifies the python ast Import.
    This is mainly to locally import things dynamically.
    """

    def __init__(self, modules: list[str]):
        super().__init__()
        self.modules = modules

    @classmethod
    def from_node(cls, imp) -> Import:
        """Generates a new import object from a python ast Import.

        Args:
            imp (ast.Import): Python ast object

        Returns:
            Import: A new import object.
        """
        return Import([alias.name for alias in imp.names])

    def __repr__(self) -> str:
        return f"Import(modules=[{', '.join(self.modules)}])"

    def __str__(self) -> str:
        return f"import {', '.join(self.modules)}"


class ImportFrom(PythonImport):
    """Helper object that stringifies the python ast ImportFrom.
    This is mainly to locally import things dynamically.
    """

    def __init__(self, module: str, names: list[str]):
        super().__init__()
        self.module = module
        self.names = names

    @classmethod
    def from_node(cls, imp) -> Import:
        """Generates a new import object from a python ast Import.

        Args:
            imp (ast.Import): Python ast object

        Returns:
            Import: A new import object.
        """
        return ImportFrom(imp.module, [alias.name for alias in imp.names])

    def __repr__(self) -> str:
        return f"ImportFrom(module='{self.module}', names=[{', '.join(self.names)}])"

    def __str__(self) -> str:
        return f"from {self.module} import {', '.join(self.names)}"
