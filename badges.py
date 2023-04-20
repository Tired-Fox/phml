from __future__ import annotations

import math
import posixpath
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Literal, TypeAlias, TypedDict

import requests

__all__ = [
    "STYLES",
    "Color",
    "Name",
    "Url",
    "Create",
    "sheild_io_link",
    "badge",
    "Badges",
    "collect_and_write",
    "Parameters",
    "PRESETS"
]

LiteralAlias: TypeAlias = type(Literal[""])

PRESETS = {
    "made_with_python": """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="189.75"
    height="28" role="img" aria-label="MADE WITH: PYTHON">
    <title>MADE WITH: PYTHON</title>
    <g shape-rendering="crispEdges">
        <rect width="88.25" height="28" fill="#ef4041" />
        <rect x="88.25" width="102.5" height="28" fill="#c1282d" />
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
        text-rendering="geometricPrecision" font-size="100">

        <text transform="scale(.1)" x="434.25" y="175" textLength="712.5" fill="#fff">MADE WITH</text>
        <text transform="scale(.1)" x="1260" y="175" textLength="535" fill="#fff" font-weight="bold">
            PYTHON </text>
        <image xmlns="http://www.w3.org/2000/svg" x="164" y="7" width="14" height="14" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="data:image/svg+xml;base64,PHN2ZyBmaWxsPSJ3aGl0ZSIgcm9sZT0iaW1nIiB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHRpdGxlPlB5dGhvbjwvdGl0bGU+PHBhdGggZD0iTTE0LjI1LjE4bC45LjIuNzMuMjYuNTkuMy40NS4zMi4zNC4zNC4yNS4zNC4xNi4zMy4xLjMuMDQuMjYuMDIuMi0uMDEuMTNWOC41bC0uMDUuNjMtLjEzLjU1LS4yMS40Ni0uMjYuMzgtLjMuMzEtLjMzLjI1LS4zNS4xOS0uMzUuMTQtLjMzLjEtLjMuMDctLjI2LjA0LS4yMS4wMkg4Ljc3bC0uNjkuMDUtLjU5LjE0LS41LjIyLS40MS4yNy0uMzMuMzItLjI3LjM1LS4yLjM2LS4xNS4zNy0uMS4zNS0uMDcuMzItLjA0LjI3LS4wMi4yMXYzLjA2SDMuMTdsLS4yMS0uMDMtLjI4LS4wNy0uMzItLjEyLS4zNS0uMTgtLjM2LS4yNi0uMzYtLjM2LS4zNS0uNDYtLjMyLS41OS0uMjgtLjczLS4yMS0uODgtLjE0LTEuMDUtLjA1LTEuMjMuMDYtMS4yMi4xNi0xLjA0LjI0LS44Ny4zMi0uNzEuMzYtLjU3LjQtLjQ0LjQyLS4zMy40Mi0uMjQuNC0uMTYuMzYtLjEuMzItLjA1LjI0LS4wMWguMTZsLjA2LjAxaDguMTZ2LS44M0g2LjE4bC0uMDEtMi43NS0uMDItLjM3LjA1LS4zNC4xMS0uMzEuMTctLjI4LjI1LS4yNi4zMS0uMjMuMzgtLjIuNDQtLjE4LjUxLS4xNS41OC0uMTIuNjQtLjEuNzEtLjA2Ljc3LS4wNC44NC0uMDIgMS4yNy4wNXptLTYuMyAxLjk4bC0uMjMuMzMtLjA4LjQxLjA4LjQxLjIzLjM0LjMzLjIyLjQxLjA5LjQxLS4wOS4zMy0uMjIuMjMtLjM0LjA4LS40MS0uMDgtLjQxLS4yMy0uMzMtLjMzLS4yMi0uNDEtLjA5LS40MS4wOXptMTMuMDkgMy45NWwuMjguMDYuMzIuMTIuMzUuMTguMzYuMjcuMzYuMzUuMzUuNDcuMzIuNTkuMjguNzMuMjEuODguMTQgMS4wNC4wNSAxLjIzLS4wNiAxLjIzLS4xNiAxLjA0LS4yNC44Ni0uMzIuNzEtLjM2LjU3LS40LjQ1LS40Mi4zMy0uNDIuMjQtLjQuMTYtLjM2LjA5LS4zMi4wNS0uMjQuMDItLjE2LS4wMWgtOC4yMnYuODJoNS44NGwuMDEgMi43Ni4wMi4zNi0uMDUuMzQtLjExLjMxLS4xNy4yOS0uMjUuMjUtLjMxLjI0LS4zOC4yLS40NC4xNy0uNTEuMTUtLjU4LjEzLS42NC4wOS0uNzEuMDctLjc3LjA0LS44NC4wMS0xLjI3LS4wNC0xLjA3LS4xNC0uOS0uMi0uNzMtLjI1LS41OS0uMy0uNDUtLjMzLS4zNC0uMzQtLjI1LS4zNC0uMTYtLjMzLS4xLS4zLS4wNC0uMjUtLjAyLS4yLjAxLS4xM3YtNS4zNGwuMDUtLjY0LjEzLS41NC4yMS0uNDYuMjYtLjM4LjMtLjMyLjMzLS4yNC4zNS0uMi4zNS0uMTQuMzMtLjEuMy0uMDYuMjYtLjA0LjIxLS4wMi4xMy0uMDFoNS44NGwuNjktLjA1LjU5LS4xNC41LS4yMS40MS0uMjguMzMtLjMyLjI3LS4zNS4yLS4zNi4xNS0uMzYuMS0uMzUuMDctLjMyLjA0LS4yOC4wMi0uMjFWNi4wN2gyLjA5bC4xNC4wMXptLTYuNDcgMTQuMjVsLS4yMy4zMy0uMDguNDEuMDguNDEuMjMuMzMuMzMuMjMuNDEuMDguNDEtLjA4LjMzLS4yMy4yMy0uMzMuMDgtLjQxLS4wOC0uNDEtLjIzLS4zMy0uMzMtLjIzLS40MS0uMDgtLjQxLjA4eiIvPjwvc3ZnPg=="/>
    </g>
</svg>\
""",
    "made_with_rust": """\
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="163.75"
    height="28" role="img" aria-label="MADE WITH: PYTHON">
    <title>MADE WITH: PYTHON</title>
    <g shape-rendering="crispEdges">
        <rect width="88.25" height="28" fill="#ef4041" />
        <rect x="88.25" width="75.5" height="28" fill="#c1282d" />
    </g>
    <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif"
        text-rendering="geometricPrecision" font-size="100">

        <text transform="scale(.1)" x="434.25" y="175" textLength="712.5" fill="#fff">MADE WITH</text>
        <text transform="scale(.1)" x="1150" y="175" textLength="350" fill="#fff" font-weight="bold">
            RUST </text>
        <image xmlns="http://www.w3.org/2000/svg" x="140" y="7" width="14" height="14" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="data:image/svg+xml;base64,PHN2ZyBmaWxsPSJ3aGl0ZSIgcm9sZT0iaW1nIiB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHRpdGxlPlJ1c3Q8L3RpdGxlPjxwYXRoIGQ9Ik0yMy44MzQ2IDExLjcwMzNsLTEuMDA3My0uNjIzNmExMy43MjY4IDEzLjcyNjggMCAwMC0uMDI4My0uMjkzNmwuODY1Ni0uODA2OWEuMzQ4My4zNDgzIDAgMDAtLjExNTQtLjU3OGwtMS4xMDY2LS40MTRhOC40OTU4IDguNDk1OCAwIDAwLS4wODctLjI4NTZsLjY5MDQtLjk1ODdhLjM0NjIuMzQ2MiAwIDAwLS4yMjU3LS41NDQ2bC0xLjE2NjMtLjE4OTRhOS4zNTc0IDkuMzU3NCAwIDAwLS4xNDA3LS4yNjIybC40OS0xLjA3NjFhLjM0MzcuMzQzNyAwIDAwLS4wMjc0LS4zMzYxLjM0ODYuMzQ4NiAwIDAwLS4zMDA2LS4xNTRsLTEuMTg0NS4wNDE2YTYuNzQ0NCA2Ljc0NDQgMCAwMC0uMTg3My0uMjI2OGwuMjcyMy0xLjE1M2EuMzQ3Mi4zNDcyIDAgMDAtLjQxNy0uNDE3MmwtMS4xNTMyLjI3MjRhMTQuMDE4MyAxNC4wMTgzIDAgMDAtLjIyNzgtLjE4NzNsLjA0MTUtMS4xODQ1YS4zNDQyLjM0NDIgMCAwMC0uNDktLjMyOGwtMS4wNzYuNDkxYy0uMDg3Mi0uMDQ3Ni0uMTc0Mi0uMDk1Mi0uMjYyMy0uMTQwN2wtLjE5MDMtMS4xNjczQS4zNDgzLjM0ODMgMCAwMDE2LjI1Ni45NTVsLS45NTk3LjY5MDVhOC40ODY3IDguNDg2NyAwIDAwLS4yODU1LS4wODZsLS40MTQtMS4xMDY2YS4zNDgzLjM0ODMgMCAwMC0uNTc4MS0uMTE1NGwtLjgwNjkuODY2NmE5LjI5MzYgOS4yOTM2IDAgMDAtLjI5MzYtLjAyODRMMTIuMjk0Ni4xNjgzYS4zNDYyLjM0NjIgMCAwMC0uNTg5MiAwbC0uNjIzNiAxLjAwNzNhMTMuNzM4MyAxMy43MzgzIDAgMDAtLjI5MzYuMDI4NEw5Ljk4MDMuMzM3NGEuMzQ2Mi4zNDYyIDAgMDAtLjU3OC4xMTU0bC0uNDE0MSAxLjEwNjVjLS4wOTYyLjAyNzQtLjE5MDMuMDU2Ny0uMjg1NS4wODZMNy43NDQuOTU1YS4zNDgzLjM0ODMgMCAwMC0uNTQ0Ny4yMjU4TDcuMDA5IDIuMzQ4YTkuMzU3NCA5LjM1NzQgMCAwMC0uMjYyMi4xNDA3bC0xLjA3NjItLjQ5MWEuMzQ2Mi4zNDYyIDAgMDAtLjQ5LjMyOGwuMDQxNiAxLjE4NDVhNy45ODI2IDcuOTgyNiAwIDAwLS4yMjc4LjE4NzNMMy44NDEzIDMuNDI1YS4zNDcyLjM0NzIgMCAwMC0uNDE3MS40MTcxbC4yNzEzIDEuMTUzMWMtLjA2MjguMDc1LS4xMjU1LjE1MDktLjE4NjMuMjI2OGwtMS4xODQ1LS4wNDE1YS4zNDYyLjM0NjIgMCAwMC0uMzI4LjQ5bC40OTEgMS4wNzYxYTkuMTY3IDkuMTY3IDAgMDAtLjE0MDcuMjYyMmwtMS4xNjYyLjE4OTRhLjM0ODMuMzQ4MyAwIDAwLS4yMjU4LjU0NDZsLjY5MDQuOTU4N2ExMy4zMDMgMTMuMzAzIDAgMDAtLjA4Ny4yODU1bC0xLjEwNjUuNDE0YS4zNDgzLjM0ODMgMCAwMC0uMTE1NS41NzgxbC44NjU2LjgwN2E5LjI5MzYgOS4yOTM2IDAgMDAtLjAyODMuMjkzNWwtMS4wMDczLjYyMzZhLjM0NDIuMzQ0MiAwIDAwMCAuNTg5MmwxLjAwNzMuNjIzNmMuMDA4LjA5ODIuMDE4Mi4xOTY0LjAyODMuMjkzNmwtLjg2NTYuODA3OWEuMzQ2Mi4zNDYyIDAgMDAuMTE1NS41NzhsMS4xMDY1LjQxNDFjLjAyNzMuMDk2Mi4wNTY3LjE5MTQuMDg3LjI4NTVsLS42OTA0Ljk1ODdhLjM0NTIuMzQ1MiAwIDAwLjIyNjguNTQ0N2wxLjE2NjIuMTg5M2MuMDQ1Ni4wODguMDkyMi4xNzUxLjE0MDguMjYyMmwtLjQ5MSAxLjA3NjJhLjM0NjIuMzQ2MiAwIDAwLjMyOC40OWwxLjE4MzQtLjA0MTVjLjA2MTguMDc2OS4xMjM1LjE1MjguMTg3My4yMjc3bC0uMjcxMyAxLjE1NDFhLjM0NjIuMzQ2MiAwIDAwLjQxNzEuNDE2MWwxLjE1My0uMjcxM2MuMDc1LjA2MzguMTUxLjEyNTUuMjI3OS4xODYzbC0uMDQxNSAxLjE4NDVhLjM0NDIuMzQ0MiAwIDAwLjQ5LjMyN2wxLjA3NjEtLjQ5Yy4wODcuMDQ4Ni4xNzQxLjA5NTEuMjYyMi4xNDA3bC4xOTAzIDEuMTY2MmEuMzQ4My4zNDgzIDAgMDAuNTQ0Ny4yMjY4bC45NTg3LS42OTA0YTkuMjk5IDkuMjk5IDAgMDAuMjg1NS4wODdsLjQxNCAxLjEwNjZhLjM0NTIuMzQ1MiAwIDAwLjU3ODEuMTE1NGwuODA3OS0uODY1NmMuMDk3Mi4wMTExLjE5NTQuMDIwMy4yOTM2LjAyOTRsLjYyMzYgMS4wMDczYS4zNDcyLjM0NzIgMCAwMC41ODkyIDBsLjYyMzYtMS4wMDczYy4wOTgyLS4wMDkxLjE5NjQtLjAxODMuMjkzNi0uMDI5NGwuODA2OS44NjU2YS4zNDgzLjM0ODMgMCAwMC41NzgtLjExNTRsLjQxNDEtMS4xMDY2YTguNDYyNiA4LjQ2MjYgMCAwMC4yODU1LS4wODdsLjk1ODcuNjkwNGEuMzQ1Mi4zNDUyIDAgMDAuNTQ0Ny0uMjI2OGwuMTkwMy0xLjE2NjJjLjA4OC0uMDQ1Ni4xNzUxLS4wOTMxLjI2MjItLjE0MDdsMS4wNzYyLjQ5YS4zNDcyLjM0NzIgMCAwMC40OS0uMzI3bC0uMDQxNS0xLjE4NDVhNi43MjY3IDYuNzI2NyAwIDAwLjIyNjctLjE4NjNsMS4xNTMxLjI3MTNhLjM0NzIuMzQ3MiAwIDAwLjQxNzEtLjQxNmwtLjI3MTMtMS4xNTQyYy4wNjI4LS4wNzQ5LjEyNTUtLjE1MDguMTg2My0uMjI3OGwxLjE4NDUuMDQxNWEuMzQ0Mi4zNDQyIDAgMDAuMzI4LS40OWwtLjQ5LTEuMDc2Yy4wNDc1LS4wODcyLjA5NTEtLjE3NDIuMTQwNy0uMjYyM2wxLjE2NjItLjE4OTNhLjM0ODMuMzQ4MyAwIDAwLjIyNTgtLjU0NDdsLS42OTA0LS45NTg3LjA4Ny0uMjg1NSAxLjEwNjYtLjQxNGEuMzQ2Mi4zNDYyIDAgMDAuMTE1NC0uNTc4MWwtLjg2NTYtLjgwNzljLjAxMDEtLjA5NzIuMDIwMi0uMTk1NC4wMjgzLS4yOTM2bDEuMDA3My0uNjIzNmEuMzQ0Mi4zNDQyIDAgMDAwLS41ODkyem0tNi43NDEzIDguMzU1MWEuNzEzOC43MTM4IDAgMDEuMjk4Ni0xLjM5Ni43MTQuNzE0IDAgMTEtLjI5OTcgMS4zOTZ6bS0uMzQyMi0yLjMxNDJhLjY0OS42NDkgMCAwMC0uNzcxNS41bC0uMzU3MyAxLjY2ODVjLTEuMTAzNS41MDEtMi4zMjg1Ljc3OTUtMy42MTkzLjc3OTVhOC43MzY4IDguNzM2OCAwIDAxLTMuNjk1MS0uODE0bC0uMzU3NC0xLjY2ODRhLjY0OC42NDggMCAwMC0uNzcxNC0uNDk5bC0xLjQ3My4zMTU4YTguNzIxNiA4LjcyMTYgMCAwMS0uNzYxMy0uODk4aDcuMTY3NmMuMDgxIDAgLjEzNTYtLjAxNDEuMTM1Ni0uMDg4di0yLjUzNmMwLS4wNzQtLjA1MzYtLjA4ODEtLjEzNTYtLjA4ODFoLTIuMDk2NnYtMS42MDc3aDIuMjY3N2MuMjA2NSAwIDEuMTA2NS4wNTg3IDEuMzk0IDEuMjA4OC4wOTAxLjM1MzMuMjg3NSAxLjUwNDQuNDIzMiAxLjg3MjkuMTM0Ni40MTMuNjgzMyAxLjIzODEgMS4yNjg1IDEuMjM4MWgzLjU3MTZhLjc0OTIuNzQ5MiAwIDAwLjEyOTYtLjAxMzEgOC43ODc0IDguNzg3NCAwIDAxLS44MTE5Ljk1MjZ6TTYuODM2OSAyMC4wMjRhLjcxNC43MTQgMCAxMS0uMjk5Ny0xLjM5Ni43MTQuNzE0IDAgMDEuMjk5NyAxLjM5NnpNNC4xMTc3IDguOTk3MmEuNzEzNy43MTM3IDAgMTEtMS4zMDQuNTc5MS43MTM3LjcxMzcgMCAwMTEuMzA0LS41Nzl6bS0uODM1MiAxLjk4MTNsMS41MzQ3LS42ODI0YS42NS42NSAwIDAwLjMzLS44NTg1bC0uMzE1OC0uNzE0N2gxLjI0MzJ2NS42MDI1SDMuNTY2OWE4Ljc3NTMgOC43NzUzIDAgMDEtLjI4MzQtMy4zNDh6bTYuNzM0My0uNTQzN1Y4Ljc4MzZoMi45NjAxYy4xNTMgMCAxLjA3OTIuMTc3MiAxLjA3OTIuODY5NyAwIC41NzUtLjcxMDcuNzgxNS0xLjI5NDguNzgxNXptMTAuNzU3NCAxLjQ4NjJjMCAuMjE4Ny0uMDA4LjQzNjMtLjAyNDMuNjUxaC0uOWMtLjA5IDAtLjEyNjUuMDU4Ni0uMTI2NS4xNDc3di40MTNjMCAuOTczLS41NDg3IDEuMTg0Ni0xLjAyOTYgMS4yMzgyLS40NTc2LjA1MTctLjk2NDgtLjE5MTMtMS4wMjc1LS40NzE3LS4yNzA0LTEuNTE4Ni0uNzE5OC0xLjg0MzYtMS40MzA1LTIuNDAzNC44ODE3LS41NTk5IDEuNzk5LTEuMzg2IDEuNzk5LTIuNDkxNSAwLTEuMTkzNi0uODE5LTEuOTQ1OC0xLjM3NjktMi4zMTUzLS43ODI1LS41MTYzLTEuNjQ5MS0uNjE5NS0xLjg4My0uNjE5NUg1LjQ2ODJhOC43NjUxIDguNzY1MSAwIDAxNC45MDctMi43Njk5bDEuMDk3NCAxLjE1MWEuNjQ4LjY0OCAwIDAwLjkxODIuMDIxM2wxLjIyNy0xLjE3NDNhOC43NzUzIDguNzc1MyAwIDAxNi4wMDQ0IDQuMjc2MmwtLjg0MDMgMS44OTgyYS42NTIuNjUyIDAgMDAuMzMuODU4NWwxLjYxNzguNzE4OGMuMDI4My4yODc1LjA0MjUuNTc3LjA0MjUuODcxN3ptLTkuMzAwNi05LjU5OTNhLjcxMjguNzEyOCAwIDExLjk4NCAxLjAzMTYuNzEzNy43MTM3IDAgMDEtLjk4NC0xLjAzMTZ6bTguMzM4OSA2LjcxYS43MTA3LjcxMDcgMCAwMS45Mzk1LS4zNjI1LjcxMzcuNzEzNyAwIDExLS45NDA1LjM2MzV6Ii8+PC9zdmc+"/>
    </g>
</svg>\
"""
}

STYLES: LiteralAlias = Literal[
    "plastic", "flat", "flat-square", "for-the-badge", "social"
]


class Parameters(TypedDict, total=False):
    style: STYLES
    """Customize the button with the following styles:
    - plastic
    - flat
    - flat-square
    - for-the-badge
    - social

    Example: `?style=flat-square`
    """

    label: str
    """Override the default left-hand-side text (URL-Encoding needed for spaces or special characters!)

    Example: `?label=healthinesses`

    URL-Encoding: https://developer.mozilla.org/en-US/docs/Glossary/percent-encoding
    """

    logo: str
    """Insert one of the named logos from (bitcoin, dependabot, gitlab, npm, paypal, serverfault,
    stackexchange, superuser, telegram, travis) or simple-icons. Simple-icons are referenced using icon
    slugs which can be found on the simple-icons site or in the slugs.md file in the simple-icons repository.

    Example: `?logo=appveyor`

    Simple-icons: https://simpleicons.org/
    slugs.md: https://github.com/simple-icons/simple-icons/blob/develop/slugs.md
    """

    logoData: str
    """Insert custom logo image (≥ 14px high). There is a limit on the total size of request headers
    we can accept (8192 bytes). From a practical perspective, this means the base64-encoded image text
    is limited to somewhere slightly under 8192 bytes depending on the rest of the request header.

    Example: `?logo=data:image/png;base64,...`
    """

    logoColor: str
    """Set the color of the logo (hex, rgb, rgba, hsl, hsla and css named colors supported).
    Supported for named logos and Shields logos but not for custom logos. For multicolor Shields
    logos, the corresponding named logo will be used and colored.

    Example: `?logoColor=violet`
    """

    logoWidth: int
    """Set the horizontal space to give to the logo

    Example: `?logoWidth=40`
    """

    link: str
    """Specify what clicking on the left/right of a badge should do. Note that this only works
    when integrating your badge in an `<object>` HTML tag, but not an `<img>` tag or a markup
    language.

    Example: `?link=http://left&link=http://right`
    """

    labelColor: str
    """Set background of the left part (hex, rgb, rgba, hsl, hsla and css named colors supported).
    The legacy name "colorA" is also supported.

    Example: `?labelColor=abcdef`
    """

    color: str
    """Set background of the right part (hex, rgb, rgba, hsl, hsla and css named colors supported).
    The legacy name "colorB" is also supported.

    Example: `?color=fedcba`
    """

    cacheSeconds: int
    """Set the HTTP cache lifetime (rules are applied to infer a default value on a per-badge basis,
    any values specified below the default will be ignored). The legacy name "maxAge" is also supported.

    Example: `?cacheSeconds=3600`
    """


def _validate_parameters(parameters: Parameters):
    if "style" in parameters and parameters["style"] not in STYLES.__args__:
        raise ValueError(
            f"Unkown badge style {parameters['style']!r}. Expected one of: {', '.join(STYLES.__args__)}"
        )


@dataclass
class Color:
    RED = "FF0000"
    RED_ORANGE = "FF5300"
    ORANGE = "FFA700"
    ORANGE_YELLOW = "FFD200"
    YELLOW = "FFF400"
    YELLOW_LIGHT_GREEN = "D1FF00"
    LIGHT_GREEN = "A3FF00"
    LIGHT_GREEN_GREEN = "52C000"
    GREEN = "2CBA00"

    All = [
        RED,
        RED_ORANGE,
        ORANGE,
        ORANGE_YELLOW,
        YELLOW,
        YELLOW_LIGHT_GREEN,
        LIGHT_GREEN,
        LIGHT_GREEN_GREEN,
        GREEN,
    ]

    @staticmethod
    def percentage(score: float) -> str:
        idx = math.ceil((len(Color.All) - 1) * score)
        return Color.All[idx]


Name = str
Url = str


def badge(*cargs: Any, **ckwargs: Any):
    """Create a badge method. Mainly for the Badges class to allow for data to be passed
    to the method when it is called by the class. This is not needed if the method doesn't
    need to take arguments/data.

    Args:
        *cargs (Any): Positional arguments used when calling the badge method
        **ckwargs (Any): Keyword arguments used when calling the badge method

    Example:
        import sample

        @badge(project="sample") # <- This data is used later when the badge is called
        def get_version_link(project: str) -> list[tuple[str, str]]:
            return [
                (
                    "version",
                    create_link(
                        create_label(f"version", sample.__version__, "white"),
                        logo="aiohttp"
                    )
                ),
                (
                    "project_name",
                    create_link(
                        create_label(f"project", project, "white"),
                    )
                )
            ]
    """

    def badge_wrapper(func: Callable[..., list[tuple[Name, Url]]]):
        @wraps(func)
        def badge_caller() -> list[tuple[Name, Url]]:
            return func(*cargs, **ckwargs)

        return badge_caller

    return badge_wrapper


def sheild_io_link(base: str, params: Parameters | None = None) -> str:
    """Create link using shields.io

    Args:
        base (str): Base url for the sheild.io badge that you want that goes after the
            `https://img.shields.io/`. Ex. 'badge/<label>-<message>-<color>'
        params (Parameters): The extra defining paramegers to pass into the url
    """

    extras = ""
    if params is not None and len(params) > 0:
        _validate_parameters(params)
        extras = "?" + "&".join(f"{key}={value}" for key, value in params.items())
    return f"https://img.shields.io/{posixpath.normpath(base).strip('/')}{extras}"


def collect_and_write(out_dir: str, links: list[tuple[Name, Url]]):
    path = Path(out_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"No directory {path.as_posix()!r} found")

    for link in links:
        with (path / link[0]).with_suffix(".svg").open("wb") as output:
            print("Generating badge:", (path / link[0]).with_suffix(".svg"))
            data = requests.get(link[1]).content
            output.write(data)


class Create:
    @staticmethod
    def badge(label: str, message: str, color: str):
        return f"badge/{label.replace(' ', '_')}-{message.replace(' ', '_')}-{color}"


class Badges:
    def __init__(
        self,
        *badges: Callable[..., list[tuple[Name, Url]] | tuple[Name, Url]],
    ):
        self.badges: list[
            Callable[..., list[tuple[Name, Url]] | tuple[Name, Url]]
        ] = list(badges)

    def callback(
        self, *badge_callbacks: Callable[..., list[tuple[Name, Url]] | tuple[Name, Url]]
    ):
        """Add a badge callback to the manager.

        Args:
            badge_callbacks (Callable[..., list[tuple[Name, Url]]]): A callback that creates tuples
                of name to url relations. Signatures look like (...) -> list[tuple[str, str]] and each
                item in the returned list has a name, the name of the output file, and a url, the
                constructed sheilds.io url. These callbacks need to be decorated with
                `@badge(<...arg>, <...key=arg>)` if you want to pass data to the callback.
        """
        self.badges.extend(badge_callbacks)

    def badge(self, name: str, base: str, params: Parameters | None = None):
        """Create a new badge and add it to the callbacks."""

        def new_badge() -> tuple[Name, Url]:
            return (
                name,
                sheild_io_link(
                    base,
                    params,
                ),
            )

        self.badges.append(new_badge)
        return self

    def collect(self, _path: str):
        """Collect the name and urls for each badge, generate the svg, and write it to a file.

        Args:
            path (str): Path to the base directory where each badge should be written to.
        """
        if _path is None:
            raise ValueError("Must provide an output directory for the badge svg files")

        path = Path(_path)
        if not path.is_dir():
            raise FileNotFoundError(f"No directory {path.as_posix()!r} found")

        for badge in self.badges:
            result = badge()
            if isinstance(result, list):
                for link in result:
                    with (path / link[0]).with_suffix(".svg").open("wb") as output:
                        print("Generating badge:", (path / link[0]).with_suffix(".svg"))
                        data = requests.get(link[1]).content
                        output.write(data)
            else:
                with (path / result[0]).with_suffix(".svg").open("wb") as output:
                    print("Generating badge:", (path / result[0]).with_suffix(".svg"))
                    data = requests.get(result[1]).content
                    output.write(data)
