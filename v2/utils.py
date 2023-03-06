def normalize_indent(content: str, indent: int = 0) -> str:
    """Normalize the indent between all lines.

    Args:
        content (str): The content to normalize the indent for
        indent (bool): The amount of offset to add to each line after normalization.

    Returns:
        str: The normalized string
    """
    from phml.core.formats.parse import strip_blank_lines  # pylint: disable=import-outside-toplevel
    from phml.utilities.misc import offset as spaces  # pylint: disable=import-outside-toplevel

    content = str(content).split("\n")
    offset = len(content[0]) - len(content[0].lstrip())
    lines = []
    for line in content:
        if len(line) > 0 and spaces(line) >= offset:
            lines.append(" " * indent + line[offset:])
        else:
            lines.append(line)
    return "\n".join(strip_blank_lines(lines))

