from xb.grammar import parse
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbError


def prompt() -> str | None:
    try:
        return input("> ")
    except EOFError:
        return None


def exec_xb(src: str, env=Environment()):
    try:
        if block := parse(src):
            print(block.evaluate(env).display())

    except Exception as e:
        if isinstance(e, XbError):
            print(e)
        else:
            print(e)


def repl():
    env = Environment()
    while (src := prompt()) is not None:
        exec_xb(src, env)


def file(path: str):
    with open(path) as f:
        src = f.read()
        exec_xb(src)
