import abc
import os
import tempfile
from abc import ABCMeta
from json import JSONDecodeError
from typing import Type, Any

import narwhals as nw
import pyarrow.ipc as ipc

try:
    from string.templatelib import Template, Interpolation
except ImportError:
    from tstr import Template, Interpolation

ARROW_PROTOCOLS = [
    "__arrow_c_schema__",
    "__arrow_c_array__",
    "__arrow_c_stream__"
]


class Interpreter(metaclass=abc.ABCMeta):
    """Representation of remote interpreter."""
    remote_object: Type["RemoteObject"]
    remote_name: Type["RemoteName"]

    def __init__(self, channel, df_backend='polars'):
        self._channel = channel
        self.df_backend = df_backend

    def __getitem__(self, item: str) -> "RemoteName":
        return self.remote_name(self, item)

    def __setitem__(self, name: str, source: "Remote"):
        self.cmd("assign", target=name, source=source.to_dict())

    def module(self, name: str = None) -> Any:
        raise NotImplementedError("This interpreter doesn't support modules.")

    def _convert_code(self, code: str | Template):
        if not isinstance(code, Template):
            return code

        parts = []
        for item in code:
            match item:
                case str() as s:
                    parts.append(s)
                case Interpolation(value, _, conversion, format_spec):
                    if conversion:
                        raise ValueError("Conversion not supported")
                    if format_spec:
                        raise ValueError("format_spec not supported")

                    if isinstance(value, Remote):
                        encoded = value.to_code()
                    else:
                        encoded = self.convert_object(value)

                    parts.append(encoded)
        return "".join(parts)

    def convert_object(self, obj):
        raise NotImplementedError("This interpreter doesn't support templated code.")

    @property
    def objects(self):
        return self.module(None)

    def cmd(self, cmd: str, **kwargs) -> dict:
        self._channel.write({"cmd": cmd, **kwargs})
        msg = self._channel.read()
        status = msg["status"]
        if status == "ok":
            return msg
        else:
            raise ValueError(f"{msg}")

    def insert(self, data: Any, target_type=None) -> "RemoteObject":
        """Insert data.

        This either writes the data to a temporary file or encodes it in the json.
        """
        if any(hasattr(data, protocol) for protocol in ARROW_PROTOCOLS):
            table = nw.from_native(data).to_arrow()
            with tempfile.NamedTemporaryFile(delete=False, mode="wb") as tmp:
                with ipc.new_stream(tmp, table.schema) as writer:
                    writer.write_table(table)

            msg = self.cmd("insert", encoding="arrow", path=tmp.name, type=target_type)
        else:
            # Serialize value to json
            try:
                msg = self.cmd("insert", value=data)
            except JSONDecodeError:
                raise ValueError("Value {type(data)} not a dataframe or json-serializable.")

        return self.remote_object(self, msg["id"])

    def get(self, obj: "Remote", df_backend=None) -> Any:
        msg = self.cmd("get", **obj.to_dict())
        try:
            value = msg["value"]
        except KeyError:
            with open(msg["path"], "rb") as f:
                arrow = ipc.open_stream(f).read_all()
                value = nw.from_arrow(arrow, backend=df_backend or self.df_backend).to_native()

            try:
                os.remove(msg["path"])
            except OSError:
                pass

        return value

    def call(self, function: "Remote", /, *args, **kwargs) -> "RemoteObject":
        packed_function = function.to_dict()
        packed_args = list(map(self._prepare_arg, args))
        packed_kwargs = {k: self._prepare_arg(v) for k, v in kwargs.items()}
        msg = self.cmd("call", function=packed_function, args=packed_args, kwargs=packed_kwargs)
        return self.remote_object(self, msg["id"])

    @staticmethod
    def _prepare_arg(obj) -> dict:
        if isinstance(obj, Remote):
            return obj.to_dict()
        else:
            return {'value': obj}

    def eval(self, code: str) -> "RemoteObject":
        code = self._convert_code(code)
        msg = self.cmd("eval", code=code)
        return self.remote_object(self, msg["id"])

    def exec(self, code: str) -> None:
        code = self._convert_code(code)
        self.cmd("exec", code=code)


class Remote(metaclass=abc.ABCMeta):
    """Representation of something remote to the interpreter."""
    _interpreter: Interpreter

    @abc.abstractmethod
    def to_dict(self):
        pass

    @abc.abstractmethod
    def to_code(self):
        pass

    def get(self, df_backend=None):
        return self._interpreter.get(self, df_backend=df_backend)

    def __call__(self, *args, **kwargs):
        return self._interpreter.call(self, *args, **kwargs)


class RemoteObject(Remote, metaclass=ABCMeta):
    """Representation of remote Object."""
    def __init__(self, interpreter, id):
        self._interpreter = interpreter
        self.id = id

    def __repr__(self):
        return f"{self.__class__.__name__}{self._interpreter, self.id})"

    def to_dict(self):
        return {"id": self.id}

    def __del__(self):
        self._interpreter.cmd("delete", id=self.id)


class RemoteName(Remote, metaclass=ABCMeta):
    """Representation of remote Name."""
    def __init__(self, interpreter: Interpreter, name: str, ns=None):
        self._interpreter = interpreter
        self.name = name
        self.ns = ns

    def __repr__(self):
        return f"{self.__class__.__name__}{self._interpreter, self.name}"

    def to_dict(self):
        if not self.ns:
            return {"name": self.name}
        else:
            return {"name": self.name, "ns": self.ns}

    def __getattr__(self, item) -> "RemoteName":
        raise NotImplementedError(f"Attributes are not implemented for {type(self._interpreter).__name__}")
