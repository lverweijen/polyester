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
            # Maybe call self.recover() here, but if that fails, we never see the error message.
            raise ChannelError(f"Invalid message ({l}). Perhaps print to stderr, not stdout.")

    def recover(self):
        """Try to recover from a bad position.

        If recovery fails, the interpreter will probably hang.
        """

        # It would be nice it there were some kind of non-blocking version of this.
        while "status" not in json.loads(self._remote.stdout.readline()):
            pass


class ChannelError(Exception):
    pass