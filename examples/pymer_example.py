import pandas as pd

from polyester import RInterpreter
from polyester.convert_r import RCode

R = RInterpreter(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")

def main():
    example1()
    example2_sugar()


def example1():
    # Evaluation in R-space
    R.objects.df = R.eval("lme4::sleepstudy")

    # Bringing data over to python-space
    print(R.get(R.objects.df))


def example2_sugar():
    # Declare package
    lme4 = R.module("lme4")

    # Create df in python
    df = pd.DataFrame([
        {"Reaction": 249.5600, "Days": 0, "Subject": 308},
        {"Reaction": 258.7047, "Days": 1, "Subject": 308},
        {"Reaction": 250.8006, "Days": 2, "Subject": 308},
        {"Reaction": 222.7339, "Days": 0, "Subject": 309},
        {"Reaction": 205.2658, "Days": 1, "Subject": 309},
        {"Reaction": 202.9778, "Days": 2, "Subject": 309},
    ])

    # Bring dataframe over to R-space
    R.objects.df = R.insert(df)

    # Run a model on our df
    R.objects.ft1 = lme4.lmer(RCode("Reaction ~ Days + (Days | Subject)"), R.objects.df)
    R.exec("capture.output(ft1, file=stderr())")


if __name__ == '__main__':
    main()
