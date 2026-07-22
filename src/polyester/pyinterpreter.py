import sys
from pathlib import Path

from polyester.interpreter import RemoteObject, Interpreter, RemoteName
from polyester.channels import JsonChannel

class RemotePyObject(RemoteObject):
    def to_code(self):
        return str(self.id)


class RemotePyName(RemoteName):
    def __getattr__(self, item):
        return RemotePyName(self._interpreter, f"{self.name}.{item}")

    def to_code(self):
        return self.name


class PyInterpreter(Interpreter):
    """Remote python interpreter."""
    remote_object = RemotePyObject
    remote_name = RemotePyName
    worker_path = Path(__file__).parent / "workers/pyworker.py"

    def __init__(self, interpreter_path=None):
        """Launch a remote python interpreter.

        :param interpreter_path: Path to interpreter to use.
            If unspecified, use the same interpreter as the current process.
        """
        if interpreter_path is None:
            interpreter_path = sys.executable
        channel = JsonChannel([interpreter_path, "-u", self.worker_path])
        super().__init__(channel)

    def module(self, name):
        """Import package and return its namespace as remote object."""
        self.exec(f"import {name}")
        return self[name]
