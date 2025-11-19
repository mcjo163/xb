import os
from typing import cast
from lark import Lark
from lark.exceptions import UnexpectedInput

from xb.grammar.syntax_errors import handle_unexpected_input
from xb.grammar.transformer import AstTransformer
from xb.interpreter.ast import Block

transformer = AstTransformer()

# If not requested, the parser will transform the AST as it is
# parsing the input, and we will never see the intermediate
# lark.Tree representation.
debug_tree = os.environ.get("XB_DEBUG") is not None

parser = Lark.open(
    "xb.lark",
    rel_to=__file__,
    start="block",
    parser="lalr",
    transformer=None if debug_tree else transformer,
)


def parse(src: str) -> Block:
    try:
        parse_result = parser.parse(src)

        if debug_tree:
            print(parse_result.pretty())
            return cast(Block, AstTransformer().transform(parse_result))

        return cast(Block, parse_result)

    except UnexpectedInput as u:
        handle_unexpected_input(u, src, parser)

    return Block([None])
