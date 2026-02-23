from polyester.pyinterpreter import PyInterpreter
from polyester.rinterpreter import RInterpreter


def get_interpreter(lang, path=None):
    match lang:
        case "py" | "python":
            return PyInterpreter(path)
        case "R":
            return RInterpreter(path)
        case unknown_lang:
            raise ValueError(f"Unknown language {unknown_lang}")
