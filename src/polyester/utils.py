from polyester.pyinterpreter import PyInterpreter
from polyester.rinterpreter import RInterpreter


def get_interpreter(lang="R", path=None):
    """Return an interpreter.

    :param lang: Which language you want.
    :param path: Where the interpreter is located.
    """
    match lang.lower():
        case "py" | "python":
            return PyInterpreter(path)
        case "r" | "rlang":
            return RInterpreter(path)
        case unknown_lang:
            raise ValueError(f"Unknown language: {unknown_lang}")
