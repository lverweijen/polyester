import json


class JsonInterpreter:
    def __init__(self, socket):
        self._socket = socket

    def cmd(self, cmd, **kwargs):
        msg = json.dumps({"cmd": cmd, **kwargs})
        self._socket.stdin.write(msg + "\n")
        msg = json.loads(self._socket.stdout.readline())
        status = msg["status"]
        if status == "ok":
            return msg
        else:
            raise ValueError(f"{msg}")
