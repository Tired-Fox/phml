import webbrowser
from pathlib import Path

path = Path('htmlcov/index.html').resolve()
if path.is_file():
    webbrowser.open_new_tab(f"file://{path.as_posix()}")
