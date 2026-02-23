# Protocol for workers

## Eval

### Python → R:

```json
{"cmd":"eval","code":"sin(5)"}
```

### R → Python:

```json
{"status":"ok","id":".550e8400-e29b-41d4-a716-446655440000"}
```

## Get

```json
{"cmd":"get","id":".550e..."}
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

## Delete

```json
{"cmd":"delete","id":".550e..."}
```

## Data transfer

```json
{"cmd":"import_arrow","path":"file.arrow","backend":null}
{"cmd":"export_arrow","id": ".550e..."}
```

`backend` is reserved if there are multiple dataframe representations.
In Python, there is pandas and polars.
In R, there is dataframe, tibble and data.table.
