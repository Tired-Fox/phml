"""phml.core.formats

A collection of Formats which represent supported file formats. Each format can
parse data, either string or dict, into a phml.core.nodes.AST along with compiling
a phml.core.nodes.ast into it's corresponding file formats string representation.
"""
from __future__ import annotations

from dataclasses import dataclass

from .format import Format
from .html_format import HTMLFormat
from .json_format import JSONFormat
from .phml_format import PHMLFormat
from .xml_format import XMLFormat


@dataclass
class Formats:
    """Collection of all built-in file formats."""

    PHML: Format = PHMLFormat  # pylint: disable=invalid-name
    HTML: Format = HTMLFormat  # pylint: disable=invalid-name
    JSON: Format = JSONFormat  # pylint: disable=invalid-name
    XML: Format = XMLFormat  # pylint: disable=invalid-name

    def __iter__(self):
        return iter(vars(self).values())
