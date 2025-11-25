"""
Transforms the parse tree into the custom AST structure used
by the interpreter.
"""

from lark import Transformer, v_args

import xb.interpreter.ast as t


# mimics v_args(inline=False) to avoid creating a full function def
def collect_args(Node):
    return lambda _, *c: Node(list(c))


@v_args(inline=True)
class AstTransformer(Transformer):
    block = collect_args(t.Block)

    # expr
    const_decl = t.ConstDecl
    var_decl = t.VarDecl
    assign = t.Assign

    # if expr
    if_ = t.If

    # logic
    and_ = t.And
    or_ = t.Or

    # compare
    eq = t.Equal
    neq = t.NotEqual
    lt = t.LessThan
    gt = t.GreaterThan
    lte = t.LessThanOrEqual
    gte = t.GreaterThanOrEqual

    # sum
    add = t.Add
    sub = t.Subtract

    # product
    mul = t.Multiply
    div = t.Divide
    int_div = t.IntegerDivide
    mod = t.Mod

    # pow
    pow = t.Pow

    # coalesce
    coalesce = t.Coalesce

    # unary
    neg = t.Negate
    not_ = t.Not

    # access
    key_access = t.KeyAccess
    index_access = t.IndexAccess

    # atoms
    identifier = t.Identifier
    p_block = t.NestedBlock

    # constructs
    array = collect_args(t.Array)
    object = collect_args(t.Object)

    key = t.Key
    infer_pair = t.InferPair
    const_pair = t.ConstPair
    var_pair = t.VarPair

    # literals
    number = t.Number
    string = t.String
    bool = t.Bool
    empty = t.Empty
