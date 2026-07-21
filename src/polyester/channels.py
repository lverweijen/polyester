import json
import subprocess
from json import JSONDecodeError


class JsonChannel:
    """Communicate messages through LJSON over stdin/stdout of a subprocess."""
    def __init__(self, args):
        self._remote = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def write(self, msg):
        msg = json.dumps(msg)
        self._remote.stdin.write(msg)
        self._remote.stdin.write("\n")

    def read(self):
        l = self._remote.stdout.readline()
        try:
            return json.loads(l)
        except JSONDecodeError:
            raise Exception(f"Invalid message ({l}). Perhaps print to stderr, not stdout.")
