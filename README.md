# Polyester

**Polyester** makes it possible to use R from Python by running R in a background process and communicating through a lightweight message protocol.

The goal is simplicity and reliability — especially on Windows — while keeping the design extensible to other languages in the future.

---

## Quick Example

```python
from polyester import get_interpreter

# Start an R interpreter
rr = get_interpreter(
    "R",
    path=r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
)

# Access an R module (namespace)
rbase = rr.module("base")

# Simple calculations
x = rr.eval("sin(100)")
y = rbase.cos(100)

print(x.get(), y.get())

# Bring a dataframe from R to Python
iris_r = rr.eval("iris")      # RemoteObject
iris_df = iris_r.get("pandas")
print(iris_df.head())
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

| Operation          | Parameters                          | Returns             | Description                      |
| ------------------ | ----------------------------------- | ------------------- | -------------------------------- |
| `insert`           | `x: simple/dataframe`               | `RemoteObject`      | Send Python data to R            |
| `get`              | `x: Remote`                         | `simple/dataframe`  | Retrieve data from R             |
| `rr[name]`         | `name: str`                         | `RemoteName` (lazy) | Reference a remote symbol        |
| `rr[name] = value` | `name: str`, `value: simple/Remote` | –                   | Assign remotely                  |
| `eval`             | `code: str`                         | `RemoteObject`      | Evaluate R code                  |
| `exec`             | `code: str`                         | –                   | Execute R code (no return value) |
| `call`             | `f: Remote`, `*args`, `**kwargs`    | `RemoteObject`      | Call a remote function           |

### RemoteObject vs RemoteName

* **RemoteObject**
  A concrete object that exists in the remote R environment.
  Automatically cleaned up when the Python object is deleted.

* **RemoteName**
  A lazy reference to a symbol or expression in R.
  It may or may not exist until evaluated.

Example:

```python
rr["x"] = 10
result = rr["x"].get()   # 10
```

---

## Data Exchange

DataFrames are transferred using Apache Arrow files for efficiency.

You can request a specific backend when retrieving:

```python
df = iris_r.get("pandas")
```

Future backends (e.g., polars) may be supported.

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
