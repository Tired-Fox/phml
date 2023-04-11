"""
.. include:: ../README.md
"""
from dataclasses import dataclass

from .builder import p
from .core import HypertextManager


@dataclass
class Version:
    """Version object for phml.

    {Major}.{Minor}.{Alpha}

    Alpha:
        Includes all bugfixes and small feature changes that go into the
        iterations of a task.

    Minor:
        All alpha changes pulled together into a task version release.

    Major:
        All minor changes pulled together into a collection of tasks into a
        milestone/goal release.
    """

    Major: int = 0
    Minor: int = 3
    Alpha: int = 0

    def __str__(self) -> str:
        return f"{self.Major}.{self.Minor}.{self.Alpha}"


__version__ = str(Version())
