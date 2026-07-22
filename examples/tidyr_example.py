from polyester import RInterpreter

R = RInterpreter(r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe")


def tidyr_example():
    rtidyr = R.module("tidyr")

    rdf = R.eval("data.frame(a=c(1,2,3), b=c(4,5,6))")
    longer_rdf = rtidyr.pivot_longer(rdf, cols=['a', 'b'])
    longer_df = R.get(longer_rdf)
    print(longer_df)

tidyr_example()
