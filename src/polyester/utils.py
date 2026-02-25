from polyester.interpreter import Interpreter, RemoteName
from polyester.pyinterpreter import PyInterpreter
from polyester.rinterpreter import RInterpreter


def get_interpreter(lang, path=None):
    match lang.lower():
        case "py" | "python":
            return PyInterpreter(path)
        case "r" | "rlang":
            return RInterpreter(path)
        case unknown_lang:
            raise ValueError(f"Unknown language: {unknown_lang}")


def rimport(interpreter: Interpreter, module_name: str):
    """Make an R package behave a little bit like a python module."""
    return _RModule(interpreter, module_name)


class _RModule:
    def __init__(self, interpreter: Interpreter, name: str):
        self.name = name
        self.interpreter = interpreter
        self._cached = []

    def __getattr__(self, item) -> RemoteName:
        return self.interpreter[f"{self.name}::{item}"]
