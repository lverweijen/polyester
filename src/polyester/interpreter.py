import abc
import os
import tempfile
from json import JSONDecodeError
from typing import Type, Any

import narwhals as nw
import pyarrow.ipc as ipc

ARROW_PROTOCOLS = [
    "__arrow_c_schema__",
    "__arrow_c_array__",
    "__arrow_c_stream__"
]


class Interpreter(metaclass=abc.ABCMeta):
    remote_object: Type["RemoteObject"]
    remote_name: Type["RemoteName"]

    def __init__(self, channel, df_backend='polars'):
        self._channel = channel
        self.df_backend = df_backend

    def __getitem__(self, item: str) -> "RemoteName":
        return self.remote_name(self, item)

    def __setitem__(self, name: str, source: "Remote"):
        self.cmd("assign", target=name, source=source.to_dict())

    def module(self, name: str) -> Any:
        raise NotImplementedError("This interpreter doesn't support modules.")

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
                value = nw.from_arrow(arrow, backend=df_backend or self.df_backend)

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
        return RemoteObject(self, msg["id"])

    @staticmethod
    def _prepare_arg(obj) -> dict:
        if isinstance(obj, Remote):
            return obj.to_dict()
        else:
            return {'value': obj}

    def eval(self, code: str) -> "RemoteObject":
        msg = self.cmd("eval", code=code)
        return self.remote_object(self, msg["id"])

    def exec(self, code: str) -> None:
        self.cmd("exec", code=code)


class Remote(metaclass=abc.ABCMeta):
    _interpreter: Interpreter

    @abc.abstractmethod
    def to_dict(self):
        pass

    def get(self, df_backend=None):
        return self._interpreter.get(self, df_backend=df_backend)

    def __call__(self, *args, **kwargs):
        return self._interpreter.call(self, *args, **kwargs)


class RemoteObject(Remote):
    def __init__(self, interpreter, id):
        self._interpreter = interpreter
        self.id = id

    def __repr__(self):
        return f"{self.__class__.__name__}{self._interpreter, self.id})"

    def to_dict(self):
        return {"id": self.id}

    def __del__(self):
        self._interpreter.cmd("delete", id=self.id)


class RemoteName(Remote):
    def __init__(self, interpreter: Interpreter, name: str):
        self._interpreter = interpreter
        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}{self._interpreter, self.name}"

    def to_dict(self):
        return {"name": self.name}

    def __getattr__(self, item) -> "RemoteName":
        raise NotImplementedError(f"Attributes are not implemented for {type(self._interpreter).__name__}")
