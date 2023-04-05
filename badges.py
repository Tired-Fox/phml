from __future__ import annotations
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Literal, TypeAlias, TypedDict
import requests
import posixpath
import math

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
]

LiteralAlias: TypeAlias = type(Literal[""])
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
