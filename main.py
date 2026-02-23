from polyester.pyinterpreter import PyInterpreter
from polyester.utils import get_interpreter


def main():
    r_example()
    py_example()


def r_example():
    interpreter = get_interpreter("R", r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

    # Try some simple calculations
    value = interpreter.eval("sin(100)")
    value2 = interpreter.call("cos", value)
    print(f"{value.get(), value2.get()=}")

    # Bring a dataframe over from R to python
    iris_r = interpreter.eval("iris")
    iris_df = iris_r.to_df('polars')
    print(iris_df)


def py_example():
    # interpreter = get_interpreter("py")
    interpreter = PyInterpreter()
    interpreter.exec("import math")
    interpreter.exec("cos = math.cos")
    value = interpreter.eval("math.sin(100)")
    value2 = interpreter.call("cos", value)
    print(f"{value.get(), value2.get()=}")

main()
