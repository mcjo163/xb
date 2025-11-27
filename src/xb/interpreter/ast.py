from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable
from lark import Token

import xb.interpreter.value as v
from xb.interpreter.value import Op
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError

class AstNode(ABC):
    # TODO: meta info?
    pass


class EvaluatableAstNode(AstNode):
    @abstractmethod
    def evaluate(self, env: Environment) -> v.Value:
        raise NotImplementedError


@dataclass
class Block(EvaluatableAstNode):
    exprs: list[Expr | None]

    def evaluate(self, env):
        stmts, ret = self.exprs[:-1], self.exprs[-1]

        for stmt in stmts:
            if stmt:
                stmt.evaluate(env)

        return ret.evaluate(env) if ret else v.Empty()


Assigner = Callable[[v.Value], None]
class Expr(EvaluatableAstNode):
    def evaluate_assignment_target(self, env: Environment) -> Assigner:
        """
        Most expressions cannot be assigned to. Valid assignment
        targets should override this implementation.

        Return a function to call with the assigned value.
        """
        _ = env
        raise XbRuntimeError("invalid assignment target")


@dataclass
class ConstDecl(Expr):
    ident: Identifier
    expr: Expr

    def evaluate(self, env):
        value = self.expr.evaluate(env)
        env.declare_const(str(self.ident.token), value)
        return value


@dataclass
class VarDecl(Expr):
    ident: Identifier
    expr: Expr

    def evaluate(self, env):
        value = self.expr.evaluate(env)
        env.declare_var(str(self.ident.token), value)
        return value


@dataclass
class Assign(Expr):
    target: Expr
    expr: Expr

    def evaluate(self, env):
        assign = self.target.evaluate_assignment_target(env)
        value = self.expr.evaluate(env)
        assign(value)
        return value


class IfNode(Expr):
    pass


@dataclass
class If(IfNode):
    condition_block: NestedBlock
    true_expr: Expr
    false_expr: Expr | None

    def evaluate(self, env):
        if self.condition_block.evaluate(env):
            return self.true_expr.evaluate(env)

        if self.false_expr is not None:
            return self.false_expr.evaluate(env)

        return v.Empty()


class Logic(IfNode):
    pass


@dataclass
class And(Logic):
    lhs: Logic
    rhs: Compare

    def evaluate(self, env):
        # && is short-circuiting
        return self.lhs.evaluate(env) and self.rhs.evaluate(env)


@dataclass
class Or(Logic):
    lhs: Logic
    rhs: Compare

    def evaluate(self, env):
        # || is short-circuiting
        return self.lhs.evaluate(env) or self.rhs.evaluate(env)


class Compare(Logic):
    pass


@dataclass
class Equal(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.eq(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class NotEqual(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.neq(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class LessThan(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.lt(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class GreaterThan(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.gt(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class LessThanOrEqual(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.lte(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class GreaterThanOrEqual(Compare):
    lhs: Compare
    rhs: Sum

    def evaluate(self, env):
        return Op.gte(self.lhs.evaluate(env), self.rhs.evaluate(env))


class Sum(Logic):
    pass


@dataclass
class Add(Sum):
    lhs: Sum
    rhs: Product

    def evaluate(self, env):
        return Op.add(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class Subtract(Sum):
    lhs: Sum
    rhs: Product

    def evaluate(self, env):
        return Op.sub(self.lhs.evaluate(env), self.rhs.evaluate(env))


class Product(Sum):
    pass


@dataclass
class Multiply(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return Op.mul(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class Divide(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return Op.div(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class IntegerDivide(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return Op.int_div(self.lhs.evaluate(env), self.rhs.evaluate(env))


@dataclass
class Mod(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return Op.mod(self.lhs.evaluate(env), self.rhs.evaluate(env))


class PowNode(Product):
    pass


@dataclass
class Pow(PowNode):
    lhs: PowNode
    rhs: CoalesceNode

    def evaluate(self, env):
        return Op.pow(self.lhs.evaluate(env), self.rhs.evaluate(env))


class CoalesceNode(PowNode):
    pass


@dataclass
class Coalesce(CoalesceNode):
    lhs: CoalesceNode
    rhs: Unary

    def evaluate(self, env):
        left = self.lhs.evaluate(env)
        return left if not Op.eq(left, v.Empty()) else self.rhs.evaluate(env)


class Unary(CoalesceNode):
    pass


@dataclass
class Negate(Unary):
    val: Unary

    def evaluate(self, env):
        return Op.neg(self.val.evaluate(env))


@dataclass
class Not(Unary):
    val: Unary

    def evaluate(self, env):
        return Op.not_(self.val.evaluate(env))


@dataclass
class Args(AstNode):
    exprs: list[Expr]


class AccessOrCall(Unary):
    pass


@dataclass
class KeyAccess(AccessOrCall):
    lhs: AccessOrCall
    key: Key

    def evaluate(self, env):
        key = str(self.key.token)
        return self.lhs.evaluate(env).key_get(key)

    def evaluate_assignment_target(self, env) -> Assigner:
        target = self.lhs.evaluate(env)
        key = str(self.key.token)

        def assign(v: v.Value):
            target.key_set(key, v)
        return assign


@dataclass
class IndexAccess(AccessOrCall):
    lhs: AccessOrCall
    index_expr: Expr

    def evaluate(self, env):
        index = self.index_expr.evaluate(env)
        return self.lhs.evaluate(env).index_get(index)

    def evaluate_assignment_target(self, env) -> Assigner:
        target = self.lhs.evaluate(env)
        index = self.index_expr.evaluate(env)

        def assign(v: v.Value):
            target.index_set(index, v)
        return assign


@dataclass
class Call(AccessOrCall):
    lhs: AccessOrCall
    args: Args

    def evaluate(self, env):
        return Op.call(
            self.lhs.evaluate(env),
            [e.evaluate(env) for e in self.args.exprs],
        )


class Atom(AccessOrCall):
    pass


@dataclass
class Identifier(Atom):
    token: Token

    def evaluate(self, env):
        return env[self.token]

    def evaluate_assignment_target(self, env) -> Assigner:
        def assign(v: v.Value):
            env[self.token] = v
        return assign


@dataclass
class Key(AstNode):
    token: Token


@dataclass
class NestedBlock(Atom):
    block: Block

    def evaluate(self, env):
        inner_env = Environment(env)
        return self.block.evaluate(inner_env)


class Literal(Atom):
    pass


@dataclass
class Number(Literal):
    token: Token

    def evaluate(self, env):
        return v.Number.from_node(self, env)


@dataclass
class String(Literal):
    token: Token

    def evaluate(self, env):
        return v.String.from_node(self, env)


@dataclass
class Bool(Literal):
    token: Token

    def evaluate(self, env):
        return v.Boolean.from_node(self, env)


@dataclass
class Empty(Literal):
    def evaluate(self, env):
        return v.Empty.from_node(self, env)


class Construct(Atom):
    pass


@dataclass
class Array(Construct):
    exprs: list[Expr]

    def evaluate(self, env):
        return v.Array.from_node(self, env)


class Pair(AstNode):
    @abstractmethod
    def key_value_const(self, env: Environment) -> tuple[str, v.Value, bool]:
        raise NotImplementedError


@dataclass
class InferPair(Pair):
    ident: Identifier

    def key_value_const(self, env):
        name = str(self.ident.token)
        return name, env[name], env.is_const(name)


@dataclass
class ConstPair(Pair):
    key: Key
    expr: Expr

    def key_value_const(self, env):
        return str(self.key.token), self.expr.evaluate(env), True


@dataclass
class VarPair(Pair):
    key: Key
    expr: Expr

    def key_value_const(self, env):
        return str(self.key.token), self.expr.evaluate(env), False


@dataclass
class Object(Construct):
    pairs: list[Pair]

    def evaluate(self, env):
        return v.Object.from_node(self, env)


@dataclass
class Params(AstNode):
    identifiers: list[Identifier]


@dataclass
class Function(Construct):
    params: Params
    body: Expr

    def evaluate(self, env):
        return v.Function.from_node(self, env)
