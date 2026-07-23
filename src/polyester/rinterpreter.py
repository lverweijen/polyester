from pathlib import Path
from typing import overload

from polyester.convert_r import to_r
from polyester.interpreter import RemoteObject, Interpreter, RemoteName
from polyester.channels import JsonChannel


class RemoteRObject(RemoteObject):
    def to_code(self):
        return f"`{self.id}`"


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

    def to_code(self):
        if self.ns:
            return f"{self.ns}::{self.name}"
        else:
            return self.name

    def __call__(self, *args, **kwargs):
        return self._interpreter.dirtycall(self, *args, **kwargs)


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
    """Remote R interpreter."""
    remote_object = RemoteRObject
    remote_name = RemoteRName
    worker_path = Path(__file__).parent / "workers/rworker.R"

    def __init__(self, interpreter_path):
        """
        Launch a remote R interpreter.

        :param interpreter_path: Path to Rscript
        """
        if interpreter_path is None:
            interpreter_path = "Rscript"

        channel = JsonChannel([interpreter_path, "--vanilla", self.worker_path])
        super().__init__(channel)

    def __getitem__(self, item):
        if "::" in item:
            ns, name = item.split("::", maxsplit=1)
            return self.remote_name(name, ns=ns)
        else:
            return self.remote_name(item)

    def convert_object(self, obj):
        return to_r(obj)

    def module(self, name: str) -> RModule:
        return RModule(self, name)

    def dirtycall(self, function: "Remote", /, *args, **kwargs) -> "RemoteObject":
        """Call function, but uses interpolation instead of protocol.

        This seems to be a more flexible approach to call R functions.
        """
        build = [(function.to_code()), "("]
        for arg in args:
            build.append(to_r(arg))
            build.append(",")
        build.pop(-1)  # remove trailing comma
        for k, v in kwargs.items():
            build.append(f"{k} = {to_r(v)}")
        build.append(",")
        build.pop(-1)  # remove trailing comma
        build.append(")")
        code = "".join(build)
        return self.eval(code)

    @overload
    def print(self, x: "Remote", capture_output=False) -> None: ...
    @overload
    def print(self, x: "Remote", capture_output=True) -> str: ...
    def print(self, x: "Remote", capture_output=False):
        """Print the canonical representation of an object.

        :param x: Object to print
        :param capture_output: If true, output is returned instead of printed.
        :return: Either output or nothing
        """
        remote_obj = self.eval(f"capture.output({to_r(x)})")
        output = self.get(remote_obj)

        # Output can be a str or list, because in R it's a character().
        if isinstance(output, str):
            output = [output]

        if capture_output:
            return "\n".join(output)
        else:
            for s in output:
                print(s)
