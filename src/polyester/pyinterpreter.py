import sys
from pathlib import Path

from polyester.interpreter import RemoteObject, Interpreter, RemoteName
from polyester.channels import JsonChannel

class RemotePyObject(RemoteObject):
    pass


class RemotePyName(RemoteName):
    def __getattr__(self, item):
        return RemotePyName(self._interpreter, f"{self.name}.{item}")


class PyInterpreter(Interpreter):
    remote_object = RemotePyObject
    remote_name = RemotePyName
    worker_path = Path(__file__).parent / "workers/pyworker.py"

    def __init__(self, interpreter_path=None):
        if interpreter_path is None:
            interpreter_path = sys.executable
        channel = JsonChannel([interpreter_path, "-u", self.worker_path])
        super().__init__(channel)

    def module(self, name):
        self.exec(f"import {name}")
        return self[name]
