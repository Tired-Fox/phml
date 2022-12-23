from pathlib import Path
from werkzeug import exceptions

from .main import phml, app, ERROR

error_page = """\
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/x-icon" href="/static/error.png">
        <link rel="stylesheet" href="{url_for('static', filename='style.css')}">
        <title>{error}</title>
    </head>
    <style>
        #error-code {
            color: #E94560;
        }
    </style>
    <body>
        <div class="flex flex-col items-center justify-center h-100">
            <h1><span id="error-code">{error}</span> {name}</h1>
            <p>{message}</p>
            <a class="mt-2" href="{url_for('home')}">Back to Home</a>
        </div>
    </body>

</html>\
"""

debug_page = """\
<!DOCTYPE html>
<html lang="en">

    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="icon" type="image/x-icon" href="/static/error.png">
        <link rel="stylesheet" href="{url_for('static', filename='style.css')}">
        <title>{error_type.upper()}</title>
    </head>

    <style>
        #error-code {
            color: #E94560;
        }

        .error {
            border-top: 3rem solid #E94560;
        }

        #error {
            width: 80%;
            max-width: 80rem;
            height: 70%;
            overflow: auto;
            background: #DCD7C9;
            color: #282A3A;
            border-radius: 1rem;
            box-shadow: rgba(0, 0, 0, 0.35) 0px 5px 15px;
        }

        #error-header {
            width: 100%;
            height: 3rem;
        }

        #error-message {
            width: 100%;
            height: auto;
            padding: 2rem;
            font-size: 1.25rem;
        }

        body {
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #282A3A;
        }

        ul {
            list-style: none;
        }
    </style>

    <body>
        <div id="error" :class="classnames({'error': error_type == 'error', 'warn': error_type == 'warn', 'info': error_type == 'info'})">
            <div id="error-message">
                <p class="mb-2 text-center">
                    <strong>
                        This tests a context manager that redirects to an error page and diplays the stacktrace
                    </strong>
                </p>
                <ul @if="not blank(tb)">
                    <li @for="idx, message in enumerate(tb)" :class="'ml-2' if idx not in [0, len(tb) - 1] else ''">
                        {message}
                    </li>
                </ul>
            </div>
        </div>
    </body>

</html>\
"""


@app.errorhandler(exceptions.InternalServerError)
def internal_error(error):
    """Internal error/debug handling."""
    return phml.parse(debug_page).render(
        error_code=error.code,
        error_name=error.name,
        tb=ERROR.traceback,
        error_type=ERROR.type,
    )


@app.errorhandler(exceptions.HTTPException)
def general_error(error):
    """General error handling"""

    message = (
        ERROR.messages[str(error.code)] if str(error.code) in ERROR.messages else error.description
    )
    return (
        phml.parse(error_page).render(error=error.code, name=error.name, message=message),
        error.code,
    )


@app.errorhandler(exceptions.NotFound)
def page_not_found(error):
    """Page not found error handling"""

    message = ERROR.messages[str(404)] if str(404) in ERROR.messages else error.description
    if Path("404.phml").is_file():
        return phml.load("404.phml").render(error=error.code, name=error.name, message=message)
    elif Path("404.html").is_file():
        with open("404.html", "r", encoding="utf-8") as not_found:
            return not_found.read()
    else:
        return (
            phml.parse(error_page).render(error=error.code, name=error.name, message=message),
            error.code,
        )
