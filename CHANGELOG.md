# v0.2.5

- Improve handling of t-string-backports through protocols.

# v0.2.4

- An `RCode` object now accepts template-strings.
- Conversion flags can now be used in t-strings to insert literal R code.
  For instance, `t"{varname!s}"` inserts the contents of `varname` without escaping.
  Without conversion flag, the value is escaped as usual.
- Use `R.env` as alias for `R.objects` to find names in R's global environment.
- Simplify R names containing a `.` by writing something like `R.env.data__frame` (which is translated to `data.frame` in R).
- Use indexing for more complex names, for example `R.env["+"]`, gets R's `+` function.

# v0.2.3

- Improve logic to automatically locate RScript.
  Most of the time, you can now write `R = RInterpreter()` without specifying an explicit location.

# v0.2.2

- Allow passing pathlikes like `pathlib.Path` to R (becomes string).
- Support passing datetime-objects to functions.
- Improve handling of numeric scalars (inf/nan/complex).
- Errors now raise `InterpreterError` instead of `ValueError`.
- Add `remote_object.fetch()` as an alias to `R.get(remote_object)`.
- Add `pipe` method to `RemoteR` to make chaining easier.

# v0.2.1

- Add `print` method to `interpreter`.
- Make `R.insert` work on simple values (str, float, bool).

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
