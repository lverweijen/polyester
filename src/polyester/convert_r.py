from typing import Any
from collections.abc import Mapping, Sequence

from polyester.interpreter import Remote


def to_r(obj: Any) -> str:
    """Convert an object to R.

    Mostly to be used for interpolation.
    """
    match obj:
        case Remote():
            return obj.to_code()
        case bool():
            return str(obj).upper()
        case str() | int() | float():
            return repr(obj)
        case Mapping():
            out = ["list("]
            for k, v in obj.items():
                out.append(f"{k}=")
                out.append(to_r(v))
                out.append(",")
            out.pop(-1)  # Remove trailing comma
            out.append(")")
            return "".join(out)
        case Sequence():
            out = ["c("]
            for x in obj:
                out.append(to_r(x))
                out.append(",")
            out.pop(-1)  # Remove trailing comma
            out.append(")")
            return "".join(out)
        case RCode():
            return str(obj)
        case _:
            raise TypeError(f"Unable to interpolate {obj!r}")


class RCode:
    """This stores R code and is inserted as is."""
    def __init__(self, code):
        self._code = code

    def __str__(self):
        return self._code
