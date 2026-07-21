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
    def __init__(self, interpreter: Interpreter, ns: str = None):
        self._ns = ns
        self._interpreter = interpreter

    def __getattr__(self, item) -> RemoteName:
        ip = self._interpreter
        return ip.remote_name(ip, item, ns=self._ns)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            ip = self._interpreter
            ip.cmd("assign", target=key, ns=self._ns, source=value.to_dict())


class RInterpreter(Interpreter):
    remote_object = RemoteRObject
    remote_name = RemoteRName
    worker_path = Path(__file__).parent / "workers/rworker.R"

    def __init__(self, interpreter_path):
        if interpreter_path is None:
            interpreter_path = "Rscript"

        channel = JsonChannel([interpreter_path, "--vanilla", self.worker_path])
        super().__init__(channel)

    def __getitem__(self, item):
        if "::" in item:
            ns, name = item.split("::", maxsplit=1)
            return self.remote_name(name, ns=ns)

    def module(self, name: str) -> RModule:
        return RModule(self, name)
