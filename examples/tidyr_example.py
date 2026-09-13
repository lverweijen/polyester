from polyester import RInterpreter

R = RInterpreter()


def tidyr_example():
    tidyr = R.module("tidyr")

    rdf = R.eval("data.frame(a=c(1,2,3), b=c(4,5,6))")

    # In R: tidyr::pivot_longer(rdf, cols=c("a", "b"))
    longer_rdf = tidyr.pivot_longer(rdf, cols=['a', 'b'])
    R.print(longer_rdf)

    # In R: rdf |> tidyr::pivot_longer(cols=c("a", "b"))
    longer_rdf2 = rdf.pipe(tidyr.pivot_longer, cols=['a', 'b'])
    R.print(longer_rdf2)

tidyr_example()
