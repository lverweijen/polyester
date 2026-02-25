# #!/usr/bin/env python

"""
This is the python worker.

It is made mostly for reference purposes.
Although it can be used for sandboxing or for calling a different python interpreter than the main one.
"""

import json
import sys
import tempfile
import narwhals as nw

import pyarrow.ipc as ipc

ARROW_PROTOCOLS = [
    "__arrow_c_schema__",
    "__arrow_c_array__",
    "__arrow_c_stream__"
]


class PyWorker:
    def __init__(self):
        self._env = {}

    def run(self):
        while line := sys.stdin.readline():
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as err:
                response = {"status": "error", "message": str(err)}
            else:
                match msg["cmd"]:
                    case "eval":
                        response = self.handle_eval(msg)
                    case "exec":
                        response = self.handle_exec(msg)
                    case "get":
                        response = self.handle_get(msg)
                    case "insert":
                        response = self.handle_insert(msg)
                    case "delete":
                        response = self.handle_delete(msg)
                    case "assign":
                        response = self.handle_assign(msg),
                    case "call":
                        response = self.handle_call(msg)
                    case unknown_cmd:
                        raise ValueError(f"Unknown command: {unknown_cmd}")

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

    def store(self, value):
        self._env['_' + hex(id(value))] = value
        return id(value)

    def get(self, id):
        return self._env['_' + hex(id)]

    def delete(self, id):
        del self._env['_' + hex(id)]

    def handle_eval(self, msg):
        """Evaluate expression and store."""
        id = self.store(eval(msg["code"], self._env))
        return {"status": "ok", "id": id}

    def handle_exec(self, msg):
        """Execute code but don't store result."""
        exec(msg["code"], self._env)
        return {"status": "ok"}

    def handle_insert(self, msg):
        """Import value."""

        # TODO Support regular value in addition to arrow

        with open(msg["path"], "rb") as f:
            table = ipc.open_stream(f).read_all()

        backend = msg.get("type") or "polars"
        df = nw.from_arrow(table, backend=backend).to_native()
        id = self.store(df)
        return {"status": "ok", "id": id}

    def handle_get(self, msg):
        """Retrieve a stored value."""
        value = self.get(msg["id"])

        if any(hasattr(value, protocol) for protocol in ARROW_PROTOCOLS):
            table = nw.from_native(value).to_arrow()

            tmp = tempfile.NamedTemporaryFile(suffix=".arrow", delete=False)
            with ipc.new_stream(tmp, table.schema) as writer:
                writer.write_table(table)

            return {"status": "ok", "encoding": "arrow", "path": tmp.name}
        else:
            return {"status": "ok", "value": value}

    def handle_delete(self, msg):
        """Delete a value."""
        self.delete(msg["id"])
        return {"status": "ok"}

    def handle_assign(self, msg):
        """Assign value to a name."""
        name = msg["name"]
        value = self.get(msg["id"])
        self._env[name] = value
        return {"status": "ok"}

    def handle_call(self, msg):
        """Make a call."""
        f = self._env[msg['function']]
        args = [self.get(arg["ref"]) for arg in msg['args']]
        id = self.store(f(*args))
        return {"status": "ok", "id": id}


if __name__ == '__main__':
    worker = PyWorker()
    worker.run()
