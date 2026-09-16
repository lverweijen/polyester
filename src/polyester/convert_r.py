import datetime as dt
import json
import math
import os
from collections.abc import Mapping, Sequence
from typing import Any, Self

try:
    from string.templatelib import Interpolation, Template, convert
except ImportError:
    from tstr import Interpolation, Template, convert

from polyester.interpreter import Remote


def to_r(obj: Any) -> str:
    """Convert an object to R.

    Mostly to be used for interpolation.
    """
    match obj:
        case Remote() | RCode():
            return obj.to_code()
        case bool():
            return str(obj).upper()
        case int():
            return f"{obj}L"
        case float():
            if math.isfinite(obj):
                return repr(obj)
            elif math.isinf(obj):
                return repr(obj).title()
            else:
                return "NaN"
        case complex():
            return f"complex(real={to_r(obj.real)}, imaginary={to_r(obj.imag)})"
        case str() | float():
            return json.dumps(obj)
        case None:
            return "NULL"
        case os.PathLike():
            return json.dumps(os.fspath(obj))
        case Mapping():
            out = ["list("]
            for k, v in obj.items():
                out.append(f"{k}=")
                out.append(to_r(v))
                out.append(", ")
            out.pop(-1)  # Remove trailing comma
            out.append(")")
            return "".join(out)
        case Sequence():
            out = ["c("]
            for x in obj:
                out.append(to_r(x))
                out.append(", ")
            out.pop(-1)  # Remove trailing comma
            out.append(")")
            return "".join(out)
        case dt.datetime():
            if obj.tzinfo is None:
                tz_name = ""
            elif isinstance(getattr(obj.tzinfo, "key", None), str):
                tz_name = obj.tzinfo.key
            else:
                # If timezone is a fixed offset (like UTC+2:00), convert obj to UTC
                obj = obj.astimezone(dt.timezone.utc)
                tz_name = "UTC"

            timestamp = obj.strftime("%Y-%m-%dT%H:%M:%S")
            if obj.microsecond:
                timestamp += f".{obj.microsecond:06d}"

            return (
                f"as.POSIXct({json.dumps(timestamp)}, "
                f"format='%Y-%m-%dT%H:%M:%OS', tz={json.dumps(tz_name)})"
            )
        case dt.date():
            return f"as.Date({json.dumps(obj.isoformat())})"
        case dt.time():
            if obj.tzinfo is not None:
                raise ValueError(
                    "R has no direct base type for a timezone-aware time-of-day"
                )

            # Represent time as timediff since midnight
            seconds = (
                obj.hour * 3600
                + obj.minute * 60
                + obj.second
                + obj.microsecond / 1_000_000
            )

            return (
                f"structure({seconds:.6f}, "
                f"class='difftime', units='secs')"
            )
        case dt.timedelta():
            seconds = (
                    obj.days * 86400
                    + obj.seconds
                    + obj.microseconds / 1_000_000
            )

            return (
                f"structure({seconds:.6f}, "
                f"class='difftime', units='secs')"
            )
        case _:
            raise TypeError(
                f"Unable to interpolate {obj!r}. \n"
                f"Arrays and dataframes needed to be "
                f"explicitly converted using R.insert(df).")


def convert_r(intp: Interpolation) -> str:
    """Convert interpolated R code to string.

    If no conversion flag is present, to_r(value) is returned.
    Otherwise, the converted value is returned literally.

    For example:
        value = "myvalue"
        t"{value}" -> '"myvalue"'  # to_r(value)
        t"{value!s}" -> "myvalue"  # literal
    """
    if intp.conversion:
        return convert(intp.value, intp.conversion)
    elif intp.format_spec:
        raise ValueError("format_spec not supported")
    else:
        return to_r(intp.value)


class RCode:
    """This stores R code and is inserted as is."""
    __slots__ = "_code"

    def __init__(self, code: str | Template | Self):
        if isinstance(code, str):
            self._code = code
        elif hasattr(code, "to_code"):  # handle self
            self._code = code.to_code()
        else:
            parts = []
            for item in code:
                if isinstance(item, str):
                    parts.append(item)
                else:
                    parts.append(convert_r(item))
            self._code = "".join(parts)

    def to_code(self) -> str:
        return self._code

    def __repr__(self) -> str:
        return f"RCode({self._code!r})"

    def __str__(self):
        return self._code
