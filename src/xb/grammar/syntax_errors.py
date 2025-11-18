from lark import Lark
from lark.exceptions import UnexpectedInput


class XbSyntaxError(SyntaxError):
    label: str
    examples: list[str]

    def __init__(self, context, line, column):
        self.context = context
        self.line = line
        self.column = column


    def __str__(self):
        return (
            f"error(syntax): {self.label} at line {self.line}, column {self.column}."
            f"\n\n{self.context}"
        )


class XbMissingComma(XbSyntaxError):
    label = "missing comma"
    examples = [
        "[1 2]",
        "{ a:1 y=2 }",
        "{ a y=2 }",
        "[\"string\" ()]",
    ]


recognized_errors = {
    cls: cls.examples
    for cls in [XbMissingComma]
}

def handle_unexpected_input(u: UnexpectedInput, src: str, grammar: Lark):
    exc_class = u.match_examples(
        grammar.parse,
        recognized_errors,
        use_accepts=True,
    )

    if not exc_class:
        raise u

    raise exc_class(u.get_context(src), u.line, u.column)
