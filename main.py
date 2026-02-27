from polyester import get_interpreter
import polars as pl
import pandas as pd


def main():
    r_example()
    py_example()


def r_example():
    rr = get_interpreter("R", r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

    # Try some simple calculations
    rvalue = rr.eval("sin(100)")
    rvalue2 = rr["cos"](rvalue)
    print(f"{rvalue.get(), rvalue2.get()=}")

    # Bring a dataframe over from Rlang to python
    iris_rdf = rr.eval("iris")
    iris_df = pd.DataFrame.from_arrow(iris_rdf.get())
    print(iris_df)


def py_example():
    rpy = get_interpreter("py")
    rmath = rpy.module('math')

    # Perform some calculations in remote python-space
    # Simple constants (like 100) don't require rpy.insert(value)
    rvalue = rmath.sin(100)
    rvalue2 = rmath.cos(rvalue)

    # The values are boxed in RemoteObjects, so let's unbox them
    print(f"{rvalue.get(), rvalue2.get()=}")

    # Round-trip data to python and back
    # Complex objects require explicit transfer by rpy.insert(value)
    df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    rdf = rpy.insert(df)
    print(pl.DataFrame(rdf.get()))

main()
