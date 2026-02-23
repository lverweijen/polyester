import json
import subprocess
import time
from pathlib import Path
import narwhals as nw

import pyarrow.ipc as ipc

from polyester.jsoninterpreter import JsonInterpreter

WORKER_PATH = Path(__file__).parent.parent / "workers/pyworker.py"


class PyInterpreter(JsonInterpreter):
    def __init__(self, path="python"):  # vanilla
        # TODO Later, we can use a real socket
        socket = subprocess.Popen(
            [path, "-u", WORKER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        super().__init__(socket)

    def cmd(self, cmd, **kwargs):
        msg = json.dumps({"cmd": cmd, **kwargs})
        self._socket.stdin.write(msg + "\n")
        raw_msg = self._socket.stdout.readline()
        msg = json.loads(raw_msg)
        status = msg["status"]
        if status == "ok":
            return msg
        else:
            raise ValueError(f"{msg}")

    def eval(self, code):
        msg = self.cmd("eval", code=code)
        return PyObject(self, msg["id"])

    def exec(self, code):
        self.cmd("exec", code=code)

    def call(self, function, *args):
        args = [{'ref': arg.id} for arg in args]
        msg = self.cmd("call", function=function, args=args)
        return PyObject(self, msg["id"])

    def __setitem__(self, name, value):
        self.cmd("assign", name=name, id=value)


class PyObject:
    def __init__(self, interpreter, id):
        self._ip = interpreter
        self.id = id

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"

    def get(self):
        return self._ip.cmd("get", id=self.id)["value"]

    def to_arrow(self):
        msg = self._ip.cmd("export_arrow", id=self.id)
        path = Path(msg["path"])

        with open(path, "rb") as f:
            table = ipc.open_stream(f).read_all()

        return table

    def to_df(self, backend="pandas"):
        return nw.from_arrow(self.to_arrow(), backend=backend).to_native()

    def to_pandas(self):
        return self.to_arrow().to_pandas()

    def __del__(self):
        self._ip.cmd("delete", id=self.id)


