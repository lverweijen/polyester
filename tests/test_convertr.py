# AI-generated

import datetime as dt
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from polyester.convert_r import to_r



@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("hello", '"hello"'),
        ('a"b', '"a\\"b"'),
        ("line\nbreak", '"line\\nbreak"'),

        (0, "0L"),
        (42, "42L"),
        (-7, "-7L"),

        (True, "TRUE"),
        (False, "FALSE"),

        (0.0, "0.0"),
        (3.14, "3.14"),
        (-2.5, "-2.5"),

        (complex(0, 0), "complex(real=0.0, imaginary=0.0)"),
        (complex(1, 0), "complex(real=1.0, imaginary=0.0)"),
        (complex(0, 1), "complex(real=0.0, imaginary=1.0)"),
        (complex(1, 2), "complex(real=1.0, imaginary=2.0)"),
        (complex(1, -2), "complex(real=1.0, imaginary=-2.0)"),
        (complex(-1, 2), "complex(real=-1.0, imaginary=2.0)"),
        (complex(-1, -2), "complex(real=-1.0, imaginary=-2.0)"),
        (complex(1.5, 2.25), "complex(real=1.5, imaginary=2.25)"),
        (
                complex(float("nan"), 2),
                "complex(real=NaN, imaginary=2.0)",
        ),
        (
                complex(1, float("nan")),
                "complex(real=1.0, imaginary=NaN)",
        ),
        (
                complex(float("inf"), -float("inf")),
                "complex(real=Inf, imaginary=-Inf)",
        ),

        (Path("data/file.csv"), '"data/file.csv"'),
        (os.fspath(Path("data/file.csv")), '"data\\\\file.csv"'),

        (["a", "b"], 'c("a", "b")'),
        ((1, 2, 3), "c(1L, 2L, 3L)"),

        (
            {"name": "Alice", "age": 42},
            'list(name="Alice", age=42L)',
        ),
    ],
)
def test_general_types(value, expected):
    assert to_r(value) == expected


def test_bool_is_not_rendered_as_integer():
    assert to_r(True) == "TRUE"
    assert to_r(False) == "FALSE"



@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            dt.date(2026, 9, 11),
            'as.Date("2026-09-11")',
        ),
        (
            dt.datetime(2026, 9, 11, 14, 30, 12),
            (
                'as.POSIXct("2026-09-11T14:30:12", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', tz="")'
            ),
        ),
        (
            dt.datetime(2026, 9, 11, 14, 30, 12, 123456),
            (
                'as.POSIXct("2026-09-11T14:30:12.123456", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', tz="")'
            ),
        ),
        (
            dt.datetime(
                2026,
                9,
                11,
                14,
                30,
                tzinfo=ZoneInfo("Europe/Amsterdam"),
            ),
            (
                'as.POSIXct("2026-09-11T14:30:00", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', '
                'tz="Europe/Amsterdam")'
            ),
        ),
        (
            dt.datetime(
                2026,
                1,
                15,
                14,
                30,
                tzinfo=ZoneInfo("Europe/Amsterdam"),
            ),
            (
                'as.POSIXct("2026-01-15T14:30:00", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', '
                'tz="Europe/Amsterdam")'
            ),
        ),
        (
            dt.datetime(
                2026,
                9,
                11,
                14,
                30,
                tzinfo=dt.timezone.utc,
            ),
            (
                'as.POSIXct("2026-09-11T14:30:00", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', '
                'tz="UTC")'
            ),
        ),
        (
            dt.datetime(
                2026,
                9,
                11,
                14,
                30,
                tzinfo=dt.timezone(dt.timedelta(hours=2)),
            ),
            (
                'as.POSIXct("2026-09-11T12:30:00", '
                'format=\'%Y-%m-%dT%H:%M:%OS\', '
                'tz="UTC")'
            ),
        ),
        (
            dt.time(14, 30, 12),
            "structure(52212.000000, class='difftime', units='secs')",
        ),
        (
            dt.time(14, 30, 12, 500000),
            "structure(52212.500000, class='difftime', units='secs')",
        ),
        (
            dt.timedelta(days=2, seconds=90),
            "structure(172890.000000, class='difftime', units='secs')",
        ),
        (
            dt.timedelta(seconds=-90),
            "structure(-90.000000, class='difftime', units='secs')",
        ),
    ],
)


def test_datetime_types(value, expected):
    assert to_r(value) == expected


def test_datetime_is_checked_before_date():
    value = dt.datetime(2026, 9, 11, 14, 30)

    result = to_r(value)

    assert "as.POSIXct" in result
    assert "as.Date" not in result


def test_timezone_name_is_preserved():
    value = dt.datetime(
        2026,
        9,
        11,
        14,
        30,
        tzinfo=ZoneInfo("America/New_York"),
    )

    result = to_r(value)

    assert 'tz="America/New_York"' in result
    assert "2026-09-11T14:30:00" in result


def test_fixed_offset_is_normalized_to_utc():
    value = dt.datetime(
        2026,
        9,
        11,
        14,
        30,
        tzinfo=dt.timezone(dt.timedelta(hours=2)),
    )

    result = to_r(value)

    assert "2026-09-11T12:30:00" in result
    assert 'tz="UTC"' in result


def test_timezone_aware_time_is_rejected():
    value = dt.time(14, 30, tzinfo=dt.timezone.utc)

    with pytest.raises(ValueError):
        to_r(value)


@pytest.mark.parametrize(
    "value",
    [
        object(),
        dt.time(12, tzinfo=dt.timezone.utc),
        # float("nan"),
        # float("inf"),
        # float("-inf"),
    ],
)
def test_unsupported_or_nonfinite_values_are_rejected(value):
    with pytest.raises((TypeError, ValueError)):
        to_r(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (float("nan"), "NaN"),
        (float("inf"), "Inf"),
        (float("-inf"), "-Inf"),
    ],
)
def test_special_float_values(value, expected):
    assert to_r(value) == expected
