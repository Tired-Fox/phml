from dataclasses import dataclass


@dataclass
class Formats:
    """Valid file formates for parsing and compiling."""

    HTML: str = "html"  # pylint: disable=invalid-name
    PHML: str = "phml"  # pylint: disable=invalid-name
    JSON: str = "json"  # pylint: disable=invalid-name
    Markdown: str = "md"  # pylint: disable=invalid-name
    XML: str = "xml"  # pylint: disable=invalid-name
