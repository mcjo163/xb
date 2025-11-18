from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from lark import Token
from xb.interpreter.environment import Environment


class AstNode(ABC):
    # TODO: meta info?
    pass


class EvaluatableAstNode(AstNode):
    @abstractmethod
    def evaluate(self, env: Environment):
        raise NotImplementedError


@dataclass
class Block(EvaluatableAstNode):
    exprs: list[Expr | None]

    def evaluate(self, env):
        stmts, ret = self.exprs[:-1], self.exprs[-1]

        for stmt in stmts:
            if stmt:
                stmt.evaluate(env)

        return ret.evaluate(env) if ret else None


class Expr(EvaluatableAstNode):
    # TODO: some way to "evaluate" to an lvalue vs an rvalue
    pass


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
        pass


class Compare(Expr):
    pass


@dataclass
class Equal(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) == self.rhs.evaluate(env)


@dataclass
class NotEqual(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) != self.rhs.evaluate(env)


@dataclass
class LessThan(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) < self.rhs.evaluate(env)


@dataclass
class GreaterThan(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) > self.rhs.evaluate(env)


@dataclass
class LessThanOrEqual(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) <= self.rhs.evaluate(env)


@dataclass
class GreaterThanOrEqual(Compare):
    lhs: Compare
    rhs: Logic

    def evaluate(self, env):
        return self.lhs.evaluate(env) >= self.rhs.evaluate(env)


class Logic(Compare):
    pass


@dataclass
class And(Logic):
    lhs: Logic
    rhs: Sum

    def evaluate(self, env):
        return self.lhs.evaluate(env) and self.rhs.evaluate(env)


@dataclass
class Or(Logic):
    lhs: Logic
    rhs: Sum

    def evaluate(self, env):
        return self.lhs.evaluate(env) or self.rhs.evaluate(env)


class Sum(Logic):
    pass


@dataclass
class Add(Sum):
    lhs: Sum
    rhs: Product

    def evaluate(self, env):
        return self.lhs.evaluate(env) + self.rhs.evaluate(env)


@dataclass
class Subtract(Sum):
    lhs: Sum
    rhs: Product

    def evaluate(self, env):
        return self.lhs.evaluate(env) - self.rhs.evaluate(env)


class Product(Sum):
    pass


@dataclass
class Multiply(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return self.lhs.evaluate(env) * self.rhs.evaluate(env)


@dataclass
class Divide(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return self.lhs.evaluate(env) / self.rhs.evaluate(env)


@dataclass
class IntegerDivide(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return self.lhs.evaluate(env) // self.rhs.evaluate(env)


@dataclass
class Remainder(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        return self.lhs.evaluate(env) % self.rhs.evaluate(env)


@dataclass
class Mod(Product):
    lhs: Product
    rhs: PowNode

    def evaluate(self, env):
        # TODO: double check this
        return self.lhs.evaluate(env) % self.rhs.evaluate(env)


class PowNode(Product):
    pass


@dataclass
class Pow(PowNode):
    lhs: PowNode
    rhs: CoalesceNode

    def evaluate(self, env):
        return self.lhs.evaluate(env) ** self.rhs.evaluate(env)


class CoalesceNode(PowNode):
    pass


@dataclass
class Coalesce(CoalesceNode):
    lhs: CoalesceNode
    rhs: Unary

    def evaluate(self, env):
        left = self.lhs.evaluate(env)
        return left if left is not None else self.rhs.evaluate(env)


class Unary(CoalesceNode):
    pass


@dataclass
class Negate(Unary):
    val: Unary

    def evaluate(self, env):
        return -(self.val.evaluate(env))


@dataclass
class Not(Unary):
    val: Unary

    def evaluate(self, env):
        return not self.val.evaluate(env)


class Access(Unary):
    pass


@dataclass
class KeyAccess(Access):
    lhs: Access
    key: Identifier

    def evaluate(self, env):
        return self.lhs.evaluate(env)[str(self.key.token)]


@dataclass
class IndexAccess(Access):
    lhs: Access
    index_expr: Atom

    def evaluate(self, env):
        return self.lhs.evaluate(env)[int(self.index_expr.evaluate(env))]


class Atom(Access):
    pass


@dataclass
class Identifier(Atom):
    token: Token

    def evaluate(self, env):
        return env[self.token]


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
        return float(self.token)


@dataclass
class String(Literal):
    token: Token

    def evaluate(self, env):
        return self.token[1:-1]


@dataclass
class Bool(Literal):
    token: Token

    def evaluate(self, env):
        return self.token == "true"


@dataclass
class Empty(Literal):
    def evaluate(self, env):
        return None


class Construct(Atom):
    pass


@dataclass
class Array(Construct):
    exprs: list[Expr]

    def evaluate(self, env):
        return [*map(
            lambda e: e.evaluate(env),
            self.exprs,
        )]


class Pair(AstNode):
    @abstractmethod
    def key_value(self, env: Environment) -> tuple[str, object]:
        raise NotImplementedError


@dataclass
class InferPair(Pair):
    ident: Identifier

    def key_value(self, env):
        name = str(self.ident.token)
        return name, env[name]


@dataclass
class ConstPair(Pair):
    ident: Identifier
    expr: Expr

    def key_value(self, env):
        return str(self.ident.token), self.expr.evaluate(env)


@dataclass
class VarPair(Pair):
    ident: Identifier
    expr: Expr

    def key_value(self, env):
        return str(self.ident.token), self.expr.evaluate(env)


@dataclass
class Object(Construct):
    pairs: list[Pair]

    def evaluate(self, env):
        return {
            k: v
            for k, v in map(
                lambda p: p.key_value(env),
                self.pairs,
            )
        }
