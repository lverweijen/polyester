# Protocol for workers

## Insert

Python to R
```json
{"cmd":"insert","value": 5}
{"cmd":"insert","path": "/tmp/blabla.arrow","encoding": "arrow"}
```

R to Python
```json
{"status":"ok","id": ".5503..."}
```

## Get

```json
{"cmd":"get","id":".550e..."}
{"cmd":"get","name":"dplyr::bind_rows"}
```

## Delete

```json
{"cmd":"delete","id":".550e..."}
```

## Assign

```json
{"cmd":"assign","id":".550e...","name":"a"}
```

**TODO**
Alternative
```json
{"cmd":"assign","target":"a","source":{"id":".550e..."}}
{"cmd":"assign","target":"a","source":{"name":"b"}}
{"cmd":"assign","target":"a","source":{"value":[1,2,3]}}
```

## Call

```json
{
  "cmd":"call",
  "function":{"name":"mean"},
  "args":[{"id":".550e..."},{"name":"a"}{"value":5}]
}
```

## Exec

```json
{"cmd":"exec","code":"import math"}
```

R → Python:

```json
{"status":"ok"}
```

## Eval

Python → R:

```json
{"cmd":"eval","code":"sin(5)"}
```

R → Python:

```json
{"status":"ok","id":".550e8400-e29b-41d4-a716-446655440000"}
```
