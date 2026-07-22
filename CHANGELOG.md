# v0.2.0

- Expose `PyInterpreter` and `RInterpreter` directly. The `get_interpreter`-frontend isn't really needed and might be removed later.
- `interpreter.get()` now returns native dataframes instead of narwhals-dataframe that you have to unpack.
- Add `namespace` argument to `interpreter.get`.
- Allow template string in `exec/eval`. Python versions older than 3.14, may use [tstr](https://pypi.org/project/tstr/) instead.
- Add `RCode`-object that remains unevaluated. Probably useful when non-standard-evaluation is desired.
- Add experimental `dirtycall`-method to `RInterpreter`, which is a bit more flexible than `call`.
  The regular `call` is unable to deal with R sheninagans such as non-standard evaluation.
  The new methods skips the `json` protocol and pipes a functioncall through the `eval` function.
  If this approach turns out to work well, it might replace the `call`-function in a future version.

# v0.1.2
Fix assign-function

# v0.1.1
Actually include the R worker

# v0.1.0
Initial version
