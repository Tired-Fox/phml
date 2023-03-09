from collections import OrderedDict
from contextlib import contextmanager
import datetime
from pathlib import Path
from typing import Any, Optional
from flask import Flask, url_for, abort, request
from werkzeug import exceptions
from phml import PHML 
from phml.utilities import cmpt_name_from_path

import re
from traceback import format_exc

app = Flask(__name__)

phml = PHML()

errors = {
    "404": "oops, it looks like the page you are trying to reach doesn't exist.",
}

internal_error_tb = list()
internal_error_type = "error"


@contextmanager
def debug(error=500):
    global internal_error_tb
    try:
        yield None
    except Exception:
        internal_error_tb = [line for line in str(format_exc()).split("\n") if line.strip() != ""]
        abort(error)


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
        phml.add(
            (cmpt_name_from_path(Path(path.as_posix().replace("components/", ""))), Path(path))
        )


def str_or_blank(var: Any, expr: str) -> str:
    return expr.format(var=var) if var is not None else ""


def build_date(year: Optional[int], month: Optional[int], day: Optional[int]) -> str:
    year = str_or_blank(year, ' {var}')
    month = str_or_blank(month_num_to_name(month) if month is not None else None, '{var}')
    day = str_or_blank(day, ' {var},')
    return f"{month}{day}{year}"


get_components(phml)

phml.expose(url_for=url_for, month_name=month_num_to_name)


@app.route("/")
def home():
    get_components(phml)
    return phml.load("home.phml").render(message="Welcome to my test of using phml with flask!")


@app.errorhandler(exceptions.NotFound)
@app.errorhandler(exceptions.HTTPException)
def page_not_found(error):
    message = errors[str(error.code)] if str(error.code) in errors else error.description
    return (
        phml.load("error.phml").render(
            error=error.code, name=error.name, message=message, url_for=url_for
        ),
        error.code,
    )


re_day = re.compile(r"[a-z]+\/\d{4}\/\d{1,2}\/\d{1,2}$")
re_month = re.compile(r"[a-z]+\/\d{4}\/\d{1,2}$")
re_year = re.compile(r"[a-z]+\/\d{4}$")


@app.route("/blog/<int:year>/<int:month>/<int:day>")
@app.route("/blog/<int:year>/<int:month>")
@app.route("/blog/<int:year>")
@app.route("/blog")
def blog(year=None, month=None, day=None):
    get_components(phml)
    path = Path("blog")

    path = Path(
        f"blog{str_or_blank(year, '/{var}')}{str_or_blank(month, '/{var}')}{str_or_blank(day, '/{var}')}"
    )

    if path.as_posix() == "blog":
        return phml.load("blog/index.phml").render(years=construct_years())
    elif re_year.match(path.as_posix()) is not None:
        if not path.is_dir():
            abort(404)

        return phml.load("blog/year.phml").render(
            months=construct_months(year),
            year=year,
            breadcrumbs=[("blog", url_for('blog')), year],
        )
    elif re_month.match(path.as_posix()) is not None:
        if not path.is_dir():
            abort(404)

        return phml.load("blog/month.phml").render(
            year=year,
            month=month,
            breadcrumbs=[
                ("blog", url_for('blog')),
                (year, url_for('blog', year=year)),
                month_num_to_name(month),
            ],
            days=construct_days(year, month),
        )
    elif re_day.match(path.as_posix()) is not None:
        if not path.with_suffix(".phml").is_file():
            abort(404)

        return phml.load(path.with_suffix(".phml")).render(
            date=f"{day}/{month}/{year}",
            breadcrumbs=[
                ("blog", url_for('blog')),
                (year, url_for('blog', year=year)),
                (month_num_to_name(month), url_for('blog', year=year, month=month)),
                day,
            ],
        )

    abort(404)


@app.route("/date", methods=["GET", "POST"])
@app.route("/date/<int:year>")
@app.route("/date/<int:year>/<int:month>")
@app.route("/date/<int:year>/<int:month>/<int:day>")
def date(year=None, month=None, day=None):
    get_components(phml)
    if request.method == "POST":
        year = request.form.get('year', None)
        month = request.form.get('month', None)
        day = request.form.get('day', None)

    return phml.load("date/index.phml").render(date=build_date(year, month, day))


@app.route("/debug")
def test():
    with debug():
        raise Exception("Test Error")
    return None


@app.errorhandler(exceptions.InternalServerError)
def internal_error(error):
    return phml.load("debug.phml").render(
        error_code=error.code,
        error_name=error.name,
        tb=internal_error_tb,
        error_type=internal_error_type,
    )
