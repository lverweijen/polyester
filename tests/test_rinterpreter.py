import pytest
from tstr import t

from polyester import RInterpreter
from polyester.channels import ChannelError
from polyester.interpreter import InterpreterError

R = RInterpreter()


def test_exec():
    R.exec("a <- c(1, 2, 3)")
    a = R.get(R.objects.a)
    assert a == [1, 2, 3]


def test_eval():
    remote_y = R.eval("5 * 3")
    y = R.get(remote_y)
    assert y == 15


def test_roundtrip():
    ...


def test_clutter_recover():
    """What if we mess up terminal output?"""
    with pytest.raises(ChannelError):
        R.exec("""print("hello world")""")

    # Try a recovery
    R._channel.recover()

    # Did we recover from printing?
    remote_y = R.eval("5 * 3")
    y = R.get(remote_y)
    assert y == 15


def test_error():
    with pytest.raises(InterpreterError):
        R.eval("5 * undefined")


_varname = "value"
_varvalue = 42
@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (R.expression("result ~ predictor1 + predictor2"), "result ~ predictor1 + predictor2"),
        (R.expression(t("var = value")), "var = value"),
        (R.expression(t("{_varname} = {_varvalue}")), "\"value\" = 42L"),
        (R.expression(t("{_varname!s} = {_varvalue!s}")), "value = 42"),
        (R.expression(t("{_varname!r} = {_varvalue!r}")), "'value' = 42"),
        (R.expression(t("{_varname!a} = {_varvalue!a}")), "'value' = 42"),
    ],
)
def test_expression_template(value, expected):
    assert value.to_code() == expected
