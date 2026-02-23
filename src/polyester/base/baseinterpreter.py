import json
from typing import Type

import narwhals as nw
import pyarrow.ipc as ipc


class BaseInterpreter:
    remote_object: Type["RemoteObject"]

    def __init__(self, socket):
        self._remote = socket

    def write(self, msg):
        msg = json.dumps(msg)
        self._remote.stdin.write(msg)
        self._remote.stdin.write("\n")

    def read(self):
        return json.loads(self._remote.stdout.readline())

    def cmd(self, cmd, **kwargs):
        self.write({"cmd": cmd, **kwargs})
        msg = self.read()
        status = msg["status"]
        if status == "ok":
            return msg
        else:
            raise ValueError(f"{msg}")

    def eval(self, code):
        msg = self.cmd("eval", code=code)
        return self.remote_object(self, msg["id"])

    def exec(self, code):
        self.cmd("exec", code=code)

    def call(self, function, *args):
        args = [{'ref': arg.id} for arg in args]
        msg = self.cmd("call", function=function, args=args)
        return self.remote_object(self, msg["id"])

    def __setitem__(self, name, value):
        self.cmd("assign", name=name, id=value)


class RemoteObject:
    def __init__(self, interpreter, id):
        self._ip = interpreter
        self.id = id

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"

    def get(self):
        return self._ip.cmd("get", id=self.id)["value"]

    def to_arrow(self):
        msg = self._ip.cmd("export_arrow", id=self.id)

        with open(msg["path"], "rb") as f:
            table = ipc.open_stream(f).read_all()

        return table

    def to_df(self, backend="pandas"):
        return nw.from_arrow(self.to_arrow(), backend=backend).to_native()

    def to_pandas(self):
        return self.to_arrow().to_pandas()

    def __del__(self):
        self._ip.cmd("delete", id=self.id)
