import sys
from pathlib import Path

from polyester.base.baseinterpreter import RemoteObject, RemoteExpression, BaseInterpreter
from polyester.base.channels import JsonChannel

class RemotePyObject(RemoteObject):
    pass


class RemotePyModule:
    def __getattr__(self, item):
        return RemoteExpression(f"{self.name}.{item}")


class PyInterpreter(BaseInterpreter):
    remote_object = RemotePyObject
    remote_module = RemotePyModule
    worker_path = Path(__file__).parent.parent / "workers/pyworker.py"

    def __init__(self, interpreter_path=None):
        if interpreter_path is None:
            interpreter_path = sys.executable
        channel = JsonChannel([interpreter_path, "-u", self.worker_path])
        super().__init__(channel)
