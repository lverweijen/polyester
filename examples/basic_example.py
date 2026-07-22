import polars as pl
from tstr import t

from polyester import RInterpreter, PyInterpreter

R = RInterpreter(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")
PY = PyInterpreter()


def main():
    r_example()
    py_example()


def r_example():
    # Try some simple calculations
    y1 = R.eval("sin(100)")
    y2 = R.eval(t("cos({y1})"))
    print(f"{R.get(y1), R.get(y2)=}")

    # Bring a dataframe over from Rlang to python
    remote_df = R.eval("iris")
    df = R.get(remote_df, "pandas")
    print(df)


def py_example():
    pymath = PY.module('math')

    # Perform some calculations in remote python-space
    # Simple constants (like 100) don't require rpy.insert(value)
    pyvalue = pymath.sin(100)
    pyvalue2 = pymath.cos(pyvalue)

    # The values are boxed in RemoteObjects, so let's unbox them
    print(f"{PY.get(pyvalue), PY.get(pyvalue2)=}")

    # Round-trip data to python and back
    # Complex objects require explicit transfer by rpy.insert(value)
    df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    remote_df = PY.insert(df)
    print(PY.get(remote_df))


main()
