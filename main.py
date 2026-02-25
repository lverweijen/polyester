from polyester import get_interpreter
import polars as pl
import pandas as pd


def main():
    r_example()
    py_example()


def r_example():
    r = get_interpreter("r", r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

    # Try some simple calculations
    value = r.eval("sin(100)")
    value2 = r.call("cos", value)
    print(f"{value.get(), value2.get()=}")

    # Bring a dataframe over from r to python
    iris_r = r.eval("iris")
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
