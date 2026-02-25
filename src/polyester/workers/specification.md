# Protocol for workers

## Insert

Python to R
```json
{"cmd":"insert","value": 5}
{"cmd":"insert","path": "/tmp/blabla"}
```

R to Python
```json
{"status":"ok","id": ".5503..."}
```

## Get

```json
{"cmd":"get","id":".550e..."}
```

## Delete

```json
{"cmd":"delete","id":".550e..."}
```

## Assign

```json
{"cmd":"assign","id":".550e...","name":"a"}
```

## Call

```json
{
  "cmd":"call",
  "function":"mean",
  "args":[{"ref":".550e..."}]
}
```


## Data transfer

```json
{"cmd":"import_arrow","path":"file.arrow","backend":null}
{"cmd":"export_arrow","id": ".550e..."}
```

`backend` is reserved if there are multiple dataframe representations.
In Python, there is pandas and polars.
In R, there is dataframe, tibble and data.table.

## Eval / exec

Python → R:

```json
{"cmd":"eval","code":"sin(5)"}
```

R → Python:

```json
{"status":"ok","id":".550e8400-e29b-41d4-a716-446655440000"}
```

