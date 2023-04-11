def get_title(page: str) -> str:
    """Tags a page id/slug and returns it's associated title."""

    if page == "context":
        return "Context Manager Compilation"
    
    if page == "manual":
        return "Manual Compilation"

    return "{Unkown Page}"
