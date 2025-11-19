from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable

from lark import Token
from xb.interpreter.environment import Environment
from xb.interpreter.errors import XbRuntimeError


class AstNode(ABC):
    # TODO: meta info?
    pass


class EvaluatableAstNode(AstNode):
    @abstractmethod
    def evaluate(self, env: Environment) -> Any:
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


Assigner = Callable[[object], None]
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
    key: Key

    def evaluate(self, env):
        key = str(self.key.token)
        try:
            return self.lhs.evaluate(env)[key]
        except KeyError:
            raise XbRuntimeError(f"unrecognized key '{key}'")
        except TypeError:
            raise XbRuntimeError(f"unsupported key '{key}'")

    def evaluate_assignment_target(self, env) -> Assigner:
        target = self.lhs.evaluate(env)
        key = str(self.key.token)

        def assign(v: object):
            # TODO: check for illegal assignment (const, bad type, etc.)...
            # ideally encapsulated in the Value class
            try:
                target[key] = v
            except TypeError:
                raise XbRuntimeError(f"cannot assign to keys on type '{type(target).__name__}'")
        return assign


@dataclass
class IndexAccess(Access):
    lhs: Access
    index_expr: Expr

    def evaluate_index(self, env: Environment) -> object:
        raw_index = self.index_expr.evaluate(env)
        return int(raw_index) if type(raw_index) is float else raw_index

    def evaluate(self, env):
        index = self.evaluate_index(env)
        try:
            return self.lhs.evaluate(env)[index]

        except (KeyError, TypeError):
            raise XbRuntimeError(f"unsupported index '{index}'")
        except IndexError:
            raise XbRuntimeError("index out of range")

    def evaluate_assignment_target(self, env) -> Assigner:
        target = self.lhs.evaluate(env)
        index = self.evaluate_index(env)

        def assign(v: object):
            try:
                target[index] = v
            except (KeyError, TypeError):
                raise XbRuntimeError(f"unsupported index '{index}'")
            except IndexError:
                raise XbRuntimeError("index out of range")
        return assign


class Atom(Access):
    pass


@dataclass
class Identifier(Atom):
    token: Token

    def evaluate(self, env):
        return env[self.token]

    def evaluate_assignment_target(self, env) -> Assigner:
        def assign(o: object):
            env[self.token] = o
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
    key: Key
    expr: Expr

    def key_value(self, env):
        return str(self.key.token), self.expr.evaluate(env)


@dataclass
class VarPair(Pair):
    key: Key
    expr: Expr

    def key_value(self, env):
        return str(self.key.token), self.expr.evaluate(env)


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
