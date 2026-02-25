import json
import tempfile
from json import JSONDecodeError
from typing import Type, Any

import narwhals as nw
import pyarrow.ipc as ipc

ARROW_PROTOCOLS = [
    "__arrow_c_schema__",
    "__arrow_c_array__",
    "__arrow_c_stream__"
]

class BaseInterpreter:
    remote_object: Type["RemoteObject"]

    def __init__(self, socket):
        self._remote = socket

    def cmd(self, cmd, **kwargs):
        self._write({"cmd": cmd, **kwargs})
        msg = self._read()
        status = msg["status"]
        if status == "ok":
            return msg
        else:
            raise ValueError(f"{msg}")

    def _write(self, msg):
        msg = json.dumps(msg)
        self._remote.stdin.write(msg)
        self._remote.stdin.write("\n")

    def _read(self):
        return json.loads(self._remote.stdout.readline())

    def insert(self, data, target_type=None):
        """Insert data.

        This either writes the data to a temporary file or encodes it in the json.
        """
        if any(hasattr(data, protocol) for protocol in ARROW_PROTOCOLS):
            table = nw.from_native(data).to_arrow()
            with tempfile.NamedTemporaryFile(delete=False, mode="wb") as tmp:
                with ipc.new_stream(tmp, table.schema) as writer:
                    writer.write_table(table)

            msg = self.cmd("insert", encoding="arrow", path=tmp.name, type=target_type)
        else:
            # Serialize value to json
            try:
                msg = self.cmd("insert", value=data)
            except JSONDecodeError:
                raise ValueError("Value {type(data)} not a dataframe or json-serializable.")

        return self.remote_object(self, msg["id"])

    def get(self, id):
        msg = self.cmd("get", id=id)

        try:
            return msg["value"]
        except KeyError:
            with open(msg["path"], "rb") as f:
                table = ipc.open_stream(f).read_all()
            return table

    def assign(self, name: str, value: Any):
        if value is not RemoteObject:
            value = self.insert(value)

        self.cmd("assign", name=name, id=value.id)

    def eval(self, code):
        msg = self.cmd("eval", code=code)
        return self.remote_object(self, msg["id"])

    def exec(self, code):
        self.cmd("exec", code=code)

    def call(self, function, *args):
        # TODO
        args = [{'ref': arg.id} for arg in args]
        msg = self.cmd("call", function=function, args=args)
        return self.remote_object(self, msg["id"])


class RemoteObject:
    def __init__(self, interpreter, id):
        self._interpreter = interpreter
        self.id = id

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"

    def get(self):
        return self._interpreter.get(self.id)

    def __del__(self):
        self._interpreter.cmd("delete", id=self.id)
