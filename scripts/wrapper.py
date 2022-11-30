from typing import Callable
from sys import stderr, stdout
from inspect import signature
from time import monotonic, sleep


def not_implemented(func: Callable):
    """Raise a not implemented error for a specific method."""

    def inner(*args, **kwargs):
        raise NotImplementedError(f"<def {func.__name__}> is not yet implemented")

    return inner


def NotImplemented(cls):
    """Raise a not implemented error for a specific class."""

    class Inner:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError(f"<class {cls.__name__}> is not yet implemented")

    return Inner


def deprecated(func: Callable):
    """Write to stderr that a specific method is deprecated."""

    def inner(*args, **kwargs):
        stderr.write(f"Deprecated: def {func.__name__}{signature(func)}\n")
        stderr.flush()
        func(*args, **kwargs)

    return inner


def Deprecated(cls):
    """Write to stderr that a specific class is deprecated."""

    class Inner(cls):
        def __init__(self, *args, **kwargs):
            bases = [base.__name__ for base in cls.__bases__ if base.__name__ != "object"]
            stderr.write(f"Deprecated: class {cls.__name__}({', '.join(bases)})\n")
            stderr.flush()
            super().__init__(*args, **kwargs)

    return Inner

def Time(func: Callable):
    """Time a given function execution and write the results to stdout."""
    def inner(*args, **kwargs):
        start = monotonic()
        result = func(*args, **kwargs)
        final = monotonic() - start
        stdout.write(f"""
Time: {final}s
Method: def {func.__name__}{signature(func)}
args=[{', '.join([str(arg) for arg in args if not isinstance(arg, (object, type))])}]
kwargs={{{', '.join([f'{key}: {value}' for key,value in kwargs.items()])}}}
""")
        stdout.flush()
        return result
    return inner

# --------------------------------------------------------------

@Time
def weather(day: str) -> str:
    day = day[0].upper() + day[1:].lower()
    print(day)


@Deprecated
class Weather:
    def __init__(self, day: str):
        self.day = day

    def print_day(self):
        self.day = weather(self.day)
        print(self.day)


if __name__ == "__main__":
    weather("friday")
    Weather("friday").print_day()
