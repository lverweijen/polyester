import datetime as dt
import json
import math
import os
from collections.abc import Mapping, Sequence
from typing import Any

from polyester.interpreter import Remote


def to_r(obj: Any) -> str:
    """Convert an object to R.

    Mostly to be used for interpolation.
    """
    match obj:
        case Remote():
            return obj.to_code()
        case RCode():
            return str(obj)
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
        case os.PathLike():
            return json.dumps(os.fspath(obj).replace("\\", "/"))
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


class RCode:
    """This stores R code and is inserted as is."""
    def __init__(self, code):
        self._code = code

    def __str__(self):
        return self._code
