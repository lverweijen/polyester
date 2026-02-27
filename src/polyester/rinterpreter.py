from pathlib import Path

from polyester.interpreter import RemoteObject, Interpreter, RemoteName
from polyester.channels import JsonChannel


class RemoteRObject(RemoteObject):
    pass


class RemoteRName(RemoteName):
    def __getattr__(self, item):
        raise NotImplementedError("Ambiguous attribute. Use `obj.dcolon/dollar/at(name)` instead.")

    def dcolon(self, name):
        """Insert double colon in name."""
        return RemoteRName(interpreter=self._interpreter, name=f"{self.name}::{name}")

    def dollar(self, name):
        """Insert dollar in name."""
        return RemoteRName(interpreter=self._interpreter, name=f"{self.name}${name}")

    def at(self, name):
        """Access S4 slot."""
        return RemoteRName(interpreter=self._interpreter, name=f"{self.name}@{name}")


class RModule:
    def __init__(self, interpreter: Interpreter, name: str):
        self._name = name
        self._interpreter = interpreter

    def __getattr__(self, item) -> RemoteName:
        return self._interpreter[f"{self._name}::{item}"]


class RInterpreter(Interpreter):
    remote_object = RemoteRObject
    remote_name = RemoteRName
    worker_path = Path(__file__).parent / "workers/rworker.R"

    def __init__(self, interpreter_path):
        if interpreter_path is None:
            interpreter_path = "Rscript"

        channel = JsonChannel([interpreter_path, "--vanilla", self.worker_path])
        super().__init__(channel)

    def module(self, name: str) -> RModule:
        return RModule(self, name)
