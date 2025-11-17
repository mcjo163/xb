from lark import Lark


parser = Lark.open(
    "xb.lark",
    rel_to=__file__,
    start="block",
    parser="lalr",
)


def prompt() -> str | None:
    try:
        return input("> ")
    except EOFError:
        return None


def parse(src: str) -> None:
    tree = parser.parse(src)
    print(tree.pretty())


def main() -> None:
    while (src := prompt()) is not None:
        try:
            parse(src)
        except Exception as err:
            print(err)
