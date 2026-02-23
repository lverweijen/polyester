from polyester.pyinterpreter import PyInterpreter
from polyester.rinterpreter import RInterpreter


def main():
    py_example()


def r_example():
    rpath = r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
    rprocess = RInterpreter(rpath)

    # Try some simple calculations
    value = rprocess.eval("sin(100)")
    value2 = rprocess.call("cos", value)
    print(f"{value.get(), value2.get()=}")

    # Bring a dataframe over from R to python
    iris_r = rprocess.eval("iris")
    iris_df = iris_r.to_df('polars')
    print(iris_df)


def py_example():
    pyprocess = PyInterpreter()
    pyprocess.exec("import math")
    pyprocess.exec("cos = math.cos")
    value = pyprocess.eval("math.sin(100)")
    value2 = pyprocess.call("cos", value)
    print(f"{value.get(), value2.get()=}")

main()
