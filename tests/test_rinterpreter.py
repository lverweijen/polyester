import pytest

from polyester import RInterpreter
from polyester.channels import ChannelError
from polyester.interpreter import InterpreterError

R = RInterpreter(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

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
