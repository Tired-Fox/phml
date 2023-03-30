"""
.. include:: ../README.md
"""
from dataclasses import dataclass
from .core import PHML, Formats
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
    Minor: int = 2
    Alpha: int = 3

    def __str__(self) -> str:
        return f"{self.Major}.{self.Beta}.{self.Alpha}"

__version__ = str(Version)