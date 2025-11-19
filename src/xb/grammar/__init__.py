from typing import cast
from lark import Lark
from lark.exceptions import UnexpectedInput

from xb.grammar.syntax_errors import handle_unexpected_input
from xb.grammar.transformer import AstTransformer
from xb.interpreter.ast import Block


parser = Lark.open(
    "xb.lark",
    rel_to=__file__,
    start="block",
    parser="lalr",
    # transformer=AstTransformer()
)


def parse(src: str) -> Block:
    try:
        tree = parser.parse(src)
        print(tree.pretty())
        return cast(Block, AstTransformer().transform(tree))

    except UnexpectedInput as u:
        handle_unexpected_input(u, src, parser)

    return Block([None])
