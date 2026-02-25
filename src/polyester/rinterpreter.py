from pathlib import Path

from polyester.base.baseinterpreter import RemoteObject, BaseInterpreter, RemoteExpression, RemoteModule
from polyester.base.channels import JsonChannel


class RemoteRObject(RemoteObject):
    pass


class RemoteRModule(RemoteModule):
    def __getattr__(self, item):
        return RemoteExpression(f"{self.name}::{item}")


class RInterpreter(BaseInterpreter):
    remote_object = RemoteRObject
    remote_module = RemoteRModule
    worker_path = Path(__file__).parent.parent / "workers/jsonworker.R"

    def __init__(self, interpreter_path):
        if interpreter_path is None:
            interpreter_path = "Rscript"

        channel = JsonChannel([interpreter_path, "--vanilla", self.worker_path])
        super().__init__(channel)
