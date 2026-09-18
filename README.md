# Polyester

**Polyester** makes it possible to use R from Python by running R in a background process and communicating through a lightweight message protocol.

The goal is simplicity and reliability — especially on Windows — while keeping the design extensible to other languages in the future.

---

## Quick Example

```python
from polyester import RInterpreter

# Start an R interpreter
R = RInterpreter()

# Simple calculations (both return a RemoteRObject)
x = R.eval("sin(100)")
y = R.env.cos(100)

# Get results in python
print(x.fetch(), y.fetch())

# Bring a dataframe from R to Python (different backends supported)
iris_df = R.eval("iris").fetch('polars')
print(iris_df.head())

# Print head without first fetching to python
R.print(R.eval("head(iris)"))
```

---

## Core Concepts

Polyester revolves around a single concept: **an interpreter**.

An interpreter manages:

* A background R process
* A private remote environment
* Communication over JSON Lines
* Data exchange using Apache Arrow

---

## Interpreter API

An interpreter supports the following operations:

| Operation                                     | Parameters                          | Returns             | Description                             |
|-----------------------------------------------|-------------------------------------|---------------------|-----------------------------------------|
| `insert`                                      | `x: simple/dataframe`               | `RemoteObject`      | Send Python data to R                   |
| `get`                                         | `x: Remote`                         | `simple/dataframe`  | Retrieve data from R                    |
| `R.env.name` or `R.env[name]`                 | `name: str`                         | `RemoteName` (lazy) | Reference a remote symbol               |
| `R.env.name = value` or `R.env[name] = value` | `name: str`, `value: simple/Remote` | –                   | Assign remotely                         |
| `eval`                                        | `code: str/Template`                | `RemoteObject`      | Evaluate R code                         |
| `exec`                                        | `code: str/Template`                | –                   | Execute R code (no return value)        |
| `call`                                        | `f: Remote`, `*args`, `**kwargs`    | `RemoteObject`      | Call a remote function                  |
| `print`                                       | `x: str`                            | –                   | Print a remote object                   |
| `module`                                      | `x: str`                            | `RemoteModule`      | Reference a remote namespace or package |
| `expression`                                  | `x: str`                            | `RemoteExpression`  | Create a remote expression              |


### Remote names and objects

* **RemoteObject**
  A concrete object that exists in the remote R environment.
  Automatically cleaned up when the Python object is deleted.

* **RemoteName**
  A lazy reference to a symbol or expression in R.
  It may or may not exist until evaluated.

Example:

```python
R.env.x = 10
result = R.get(R.env.x)   # 10

# This can also be written the following way
result = R.env.x.fetch()   # 10
```

The following methods can be used on both `RemoteName` and `RemoteObject`:

| Method      | Parameters           | Returns            | Description            |
|-------------|----------------------|--------------------|------------------------|
| `obj.fetch` | –                    | `simple/dataframe` | Same as `R.get(self)`  |
| `obj.call`  | `*args, **kwargs`    | `RemoteObject`     | Call a remote function |
| `obj.pipe`  | `f, *args, **kwargs` | `RemoteObject`     | Pipe object through f  |

* **RemoteModule** A remote namespace to help construct `RemoteName`s.

Example:

```python
base = R.module("base")

# The __ is translated to a dot (calls base::data.frame)
df = base.data__frame(year = [2010, 2020],
                      population = [1_080_095, 1_120_015],
                      temperature = [20, 22]) 

# Functions in base (and other built-ins) can also be accessed through R.env directly
df = R.env.data__frame(...)
```

* **RemoteExpression** Pass a literal expression as an argument.
Can be used to construct datatypes like formulae
or function parameters that use Non Standard Evaluation.
Objects can be interpolated if given a [t-string](https://docs.python.org/3/reference/lexical_analysis.html#t-strings).

Example:

```python
nice_temperature = 21
subset_df = base.subset(df, R.expression(t"temperature >= {nice_temperature}"))
```

---

## Data Exchange

DataFrames are transferred using Apache Arrow files for efficiency.

You can request a specific backend when retrieving:

```python
df = iris_rdf.fetch("pandas")
```

If no `df_backend` is provided, [polars](https://pola.rs/) will be used.

---

## Important Notes

⚠ **Do not print to stdout from R.**

Polyester uses `stdout` for protocol communication.
Printing to `stdout()` inside R will corrupt the communication channel.

If you need logging inside R, use:

```r
message("debug info")
```

or write to `stderr()`.

In python, `R.print` can be used to print a remote object.

---

## Why Not Use rpy2?

rpy2 is a mature and powerful solution.

However:

* rpy2 is currently difficult to use on Windows in many environments.
* Polyester runs R as a subprocess and avoids tight binary coupling.
* The architecture is language-agnostic and may support additional languages (e.g., Julia) in the future.

If rpy2 becomes reliably usable in all target environments, Polyester may optionally integrate with it.

---

## Design Goals

* ✅ Windows support
* ✅ Minimal external dependencies
* ✅ Simple, explicit API
* ✅ Subprocess isolation
* 🔄 Possible future multi-language support

Performance is important, but clarity and robustness are higher priorities at this stage.

---

## Implementation Details

* R is started as a background subprocess.
* Communication happens over JSON Lines.
* DataFrames are exchanged via Apache Arrow files.
* Remote objects are reference-tracked and cleaned up automatically.

---

## Status

### Completed

* [x] Start R subprocess in background
* [x] JSON Lines protocol for communication
* [x] DataFrame transfer using Apache Arrow
* [x] Remote object lifecycle management
