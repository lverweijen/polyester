from pathlib import Path

from polyester.interpreter import RemoteObject, Interpreter, RemoteName
from polyester.channels import JsonChannel


class RemoteRObject(RemoteObject):
    pass


class RemoteRName(RemoteName):
    def __getattr__(self, item):
        # TODO I'm not even really sure if this should use $ or @ or :: or . or something else
        return RemoteRName(interpreter=self._interpreter, name=f"{self._name}${item}")


class RInterpreter(Interpreter):
    remote_object = RemoteRObject
    remote_name = RemoteRName
    worker_path = Path(__file__).parent / "workers/jsonworker.R"

    def __init__(self, interpreter_path):
        if interpreter_path is None:
            interpreter_path = "Rscript"

        channel = JsonChannel([interpreter_path, "--vanilla", self.worker_path])
        super().__init__(channel)
