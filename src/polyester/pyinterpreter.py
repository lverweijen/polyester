import subprocess
from pathlib import Path

from polyester.base.baseinterpreter import RemoteObject, BaseInterpreter

WORKER_PATH = Path(__file__).parent.parent / "workers/pyworker.py"

class RemotePyObject(RemoteObject):
    pass

class PyInterpreter(BaseInterpreter):
    remote_object = RemotePyObject

    def __init__(self, path=None):  # vanilla
        # TODO Later, we can use a real socket
        if path is None:
            path = "python"
        process = subprocess.Popen(
            [path, "-u", WORKER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        super().__init__(process)
