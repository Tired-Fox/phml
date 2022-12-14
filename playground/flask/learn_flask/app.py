from collections import OrderedDict
import datetime
from pathlib import Path
from flask import Flask, url_for, abort
from werkzeug import exceptions
from phml import PHML, cmpt_name_from_path
import re

app = Flask(__name__)

phml = PHML()

errors = {"404": "oops, it looks like the page you are trying to reach doesn't exist."}


def construct_days(year: int, month: int) -> dict:
    return OrderedDict(
        sorted(
            {
                int(
                    path.name.replace(path.suffix, "")
                ): f"/blog/{year}/{month}/{int(path.name.replace(path.suffix, ''))}"
                for path in Path(f"./blog/{year}/{month}").glob("./*.phml")
                if path.is_file()
            }.items()
        )
    )


def construct_months(year: int) -> dict:
    return OrderedDict(
        sorted(
            {
                int(path.name): construct_days(year, int(path.name))
                for path in Path(f"./blog/{year}").glob("./*")
                if path.is_dir()
            }.items()
        )
    )


def construct_years() -> dict:
    return OrderedDict(
        sorted(
            {
                int(path.name): construct_months(int(path.name))
                for path in Path("./blog/").glob("./*")
                if path.is_dir() and path.name.isdigit() and len(path.name) == 4
            }.items()
        )
    )


def month_num_to_name(month: int, long: bool = True) -> str:
    obj = datetime.datetime.strptime(str(month), "%m")
    if long:
        return obj.strftime("%B")

    return obj.strftime("%b")


def get_components(phml: PHML):
    for path in Path("components/").glob("./**/*.phml"):
        phml.add((cmpt_name_from_path(Path(path.as_posix().replace("components/", ""))), Path(path)))


get_components(phml)

global_vals = {
    "url_for": url_for,
    "month_name": month_num_to_name,
}


@app.route("/")
def home():
    get_components(phml)
    return phml.load("home.phml").render(
        message="Welcome to my test of using phml with flask!", **global_vals
    )


@app.errorhandler(exceptions.NotFound)
def page_not_found(error):
    return (
        phml.load("error.phml").render(
            error=error.code, name=error.name, message=errors[str(error.code)], url_for=url_for
        ),
        404,
    )


blog_day = re.compile(r"blog\/\d{4}\/\d{1,2}\/\d{1,2}$")
blog_month = re.compile(r"blog\/\d{4}\/\d{1,2}$")
blog_year = re.compile(r"blog\/\d{4}$")


@app.route("/blog/<int:year>/<int:month>/<int:day>")
@app.route("/blog/<int:year>/<int:month>")
@app.route("/blog/<int:year>")
@app.route("/blog")
def blog(year=None, month=None, day=None):
    get_components(phml)
    path = Path("blog")
    if year is not None:
        path = path.joinpath(str(year))
        if month is not None:
            path = path.joinpath(str(month))
            if day is not None:
                path = path.joinpath(str(day))

    if path.as_posix() == "blog":
        return phml.load("blog/index.phml").render(years=construct_years(), **global_vals)
    elif blog_year.match(path.as_posix()) is not None:
        if not path.is_dir():
            abort(404)

        return phml.load("blog/year.phml").render(
            months=construct_months(year),
            year=year,
            breadcrumbs=[("blog", url_for('blog')), year],
            **global_vals,
        )
    elif blog_month.match(path.as_posix()) is not None:
        if not path.is_dir():
            abort(404)

        return phml.load("blog/month.phml").render(
            year=year,
            month=month,
            breadcrumbs=[
                ("blog", url_for('blog')),
                ("year", url_for('blog', year=year)),
                month_num_to_name(month),
            ],
            days=construct_days(year, month),
            **global_vals,
        )
    elif blog_day.match(path.as_posix()) is not None:
        if not path.with_suffix(".phml").is_file():
            abort(404)

        return phml.load(path.with_suffix(".phml")).render(
            date=f"{day}/{month}/{year}",
            **global_vals,
            breadcrumbs=[
                ("blog", url_for('blog')),
                (year, url_for('blog', year=year)),
                (month_num_to_name(month), url_for('blog', year=year, month=month)),
                day,
            ],
        )

    abort(404)
