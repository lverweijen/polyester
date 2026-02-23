This package aims to make R available from Python

## Quick example

```python

from polyester.rinterpreter import RInterpreter

rpath = r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
rlang = RInterpreter(rpath)

# Simple calculations
value = rlang.eval("sin(100)")
value2 = rlang.call("cos", value)
print(f"{value.get(), value2.get()=}")

# Bring a dataframe over from R to python
iris_r = rlang.eval("iris")
iris_df = iris_r.to_df('polars')  # other back-ends like pandas are also supported
print(iris_df)
```

## How does it work

You need to work with `RObject`s. Most operations generate a new R object.
Once you are done, you can convert the object back to python.

Use `robj.get()` for simple json-serializable types. For dataframes, `robj.to_df(backend)` can be used.

## Why not use Rpy2?

Because:

> Running rpy2 on Windows is currently not supported

And unfortunately I'm stuck in a world where I have to Windows.
Compared to rpy2 we aim for:

- Stability over performance;
- Windows support;
- I'm also interested in supported other languages than R.

However, at some point this package may fall back to something like rpy2 if we can get it to work.

## TODO

- [ ] Augment handle_call
- [ ] Support Julia

## Maybes
- [ ] Switch to socket
- [ ] Switch to msgpack
- [ ] Consider mmap as optional alternative
- [ ] Consider rpy2 as an optional backend
