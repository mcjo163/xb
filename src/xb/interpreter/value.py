from __future__ import annotations

from xb.interpreter.errors import XbRuntimeError
from xb.interpreter.environment import Environment
import xb.interpreter.ast as t

class Op:
    """
    The supported operations on Value instances. Delegates the implementation
    to the appropriate subclass methods if necessary.
    """

    @staticmethod
    def _types_match(a: Value, b: Value) -> bool:
        return type(a) is type(b)

    @staticmethod
    def _type_guard(a: Value, b: Value, op_name: str | None = None) -> None:
        if not Op._types_match(a, b):
            msg_start = f"cannot {op_name}" if op_name else "illegal operation between"
            raise XbRuntimeError(msg_start + f" types '{a.type_name}' and '{b.type_name}'")

    @staticmethod
    def eq(a: Value, b: Value) -> Value:
        if not Op._types_match(a, b):
            return Boolean(False)
        return a.eq(b)

    @staticmethod
    def neq(a: Value, b: Value) -> Value:
        return Op.not_(Op.eq(a, b))

    @staticmethod
    def lt(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "compare")
        return a.lt(b)

    @staticmethod
    def gt(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "compare")
        return a.gt(b)

    @staticmethod
    def lte(a: Value, b: Value) -> Value:
        return Op.not_(Op.gt(a, b))

    @staticmethod
    def gte(a: Value, b: Value) -> Value:
        return Op.not_(Op.lt(a, b))

    @staticmethod
    def add(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "add")
        return a.add(b)

    @staticmethod
    def not_(a: Value) -> Value:
        return Boolean(not Boolean.cast(a)._bool)


class Value[Subclass, TreeNode]():
    type_name: str

    @staticmethod
    def from_node(node: TreeNode, env: Environment) -> Subclass:
        _ = node, env
        # Must be implemented for each supported type.
        raise NotImplementedError

    @classmethod
    def cast(cls, value: Value) -> Subclass:
        _ = value
        raise XbRuntimeError(
            f"cannot cast type '{value.type_name}' to '{cls.type_name}'"
        )

    def display(self) -> str:
        return self.__repr__()

    def eq(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support equality comparison"
        )

    def lt(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support ordering"
        )

    def gt(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support ordering"
        )

    def add(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support addition"
        )

    def sub(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support subtraction"
        )

    def mul(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support multiplication"
        )

    def div(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support division"
        )

    def int_div(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support integer division"
        )

    def rem(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support integer division"
        )


class Empty(Value["Empty", t.Empty]):
    type_name = "()"

    @staticmethod
    def from_node(node, env):
        return Empty()

    def display(self) -> str:
        return self.type_name

    def eq(self, other) -> Value:
        # () is always equal to ()
        return Boolean(True)


class Boolean(Value["Boolean", t.Bool]):
    type_name = "boolean"

    def __init__(self, val: bool) -> None:
        self._bool = val

    @staticmethod
    def from_node(node, env):
        return Boolean(node.token == "true")

    @classmethod
    def cast(cls, value):
        match value:
            case Empty() | Boolean(_bool=False):
                return Boolean(False)
            case _:
                return Boolean(True)

    def display(self) -> str:
        return "true" if self._bool else "false"

    def eq(self, other) -> Value:
        return Boolean(self._bool == other._bool)


class String(Value["String", t.String]):
    type_name = "string"

    def __init__(self, val: str) -> None:
        self._str = val

    @staticmethod
    def from_node(node, env):
        # TODO: decide on/implement escaping strategy
        return String(eval(node.token))

    @classmethod
    def cast(cls, value):
        match value:
            case String(_str=s):
                return String(s)
            case _:
                return String(value.display())

    def display(self) -> str:
        # TODO: handle escaping more robustly
        return f'"{self._str}"'

    def eq(self, other) -> Value:
        return Boolean(self._str == other._str)


class Number(Value["Number", t.Number]):
    type_name = "number"

    def __init__(self, val: (int | float)) -> None:
        if type(val) is int or (i := int(val)) != val:
            self._val = val
        else:
            self._val = i

    @staticmethod
    def parse_string(string: str) -> (int | float):
        raw = string.lower()

        if len(raw) > 2 and raw[:2] == "0x":
            # hex literal
            return int(raw, base=0)

        if any(c in raw for c in [".", "e"]):
            # float candidate (prefer int if whole)
            f = float(raw)
            return i if (i := int(f)) == f else f

        return int(raw)

    @staticmethod
    def from_node(node, env):
        return Number(Number.parse_string(node.token))

    @classmethod
    def cast(cls, value):
        match value:
            case Number(_val=v):
                return Number(v)
            case String(_str=s):
                return Number(Number.parse_string(s))

        return super().cast(value)

    def display(self) -> str:
        return str(self._val)

    def eq(self, other) -> Value:
        return Boolean(self._val == other._val)
