from polyester import get_interpreter
import polars as pl
import pandas as pd


def main():
    # r_example()
    # py_example()
    tidyr_example()


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


def tidyr_example():
    rr = get_interpreter("R", r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")
    rtidyr = rr.module("tidyr")

    rdf = rr.eval("data.frame(a=c(1,2,3), b=c(4,5,6))")
    # cols = "a"  # works
    cols = rr.eval("c('a', 'b')")  # this also works, but may require generating R expressions
    # cols = rr.eval("['a', 'b']")  # doesn't work, because this becomes list("a", "b"), while R needs a vector.
    longer_rdf = rtidyr.pivot_longer(rdf, cols=cols)
    longer_df = longer_rdf.get()
    print(longer_df)

main()
