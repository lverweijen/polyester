import subprocess
from pathlib import Path

from polyester.base.baseinterpreter import RemoteObject, BaseInterpreter

WORKER_PATH = Path(__file__).parent.parent / "workers/jsonworker.R"

class RemoteRObject(RemoteObject):
    pass

class RInterpreter(BaseInterpreter):
    remote_object = RemoteRObject

    def __init__(self, path=None):
        if path is None:
            path = "Rscript"

        socket = subprocess.Popen(
            [path, "--vanilla", WORKER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        super().__init__(socket)

class RemotePyObject(RemoteObject):
    pass
