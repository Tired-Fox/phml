from contextlib import contextmanager
from traceback import format_exc
from flask import abort

from .main import ERROR


@contextmanager
def debug(error=500):
    try:
        yield None
    except Exception as exception:  # pylint: disable=broad-except,unused-variable
        ERROR.traceback = [line for line in str(format_exc()).split("\n") if line.strip() != ""]
        abort(error)
