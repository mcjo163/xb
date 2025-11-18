from xb.grammar import parse
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbError


def prompt() -> str | None:
    try:
        return input("> ")
    except EOFError:
        return None


def run():
    env = Environment()

    while (src := prompt()) is not None:
        try:
            if block := parse(src):
                print(block.evaluate(env))

        except Exception as e:
            if isinstance(e, XbError):
                print(e)
            else:
                print(e)
