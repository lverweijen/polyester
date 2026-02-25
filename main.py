from polyester import get_interpreter
import polars as pl
import pandas as pd


def main():
    r_example()
    py_example()


def r_example():
    rlang = get_interpreter("R", r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

    # Try some simple calculations
    value = rlang.eval("sin(100)")
    value2 = rlang.call("cos", value)
    print(f"{value.get(), value2.get()=}")

    # Bring a dataframe over from Rlang to python
    iris_r = rlang.eval("iris")
    iris_df = pd.DataFrame.from_arrow(iris_r.get())
    # iris_df = pl.DataFrame(iris_r.get())
    print(iris_df)


def py_example():
    py = get_interpreter("py")
    py.exec("import math")
    py.exec("cos = math.cos")
    value = py.eval("math.sin(100)")
    value2 = py.call("cos", value)
    print(f"{value.get(), value2.get()=}")

    # Round-trip data to python and back
    df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    df_py = py.insert(df)
    print(pl.DataFrame(df_py.get()))

main()
