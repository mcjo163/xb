from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from xb.interpreter.errors import XbRuntimeError

if TYPE_CHECKING:
    import xb.interpreter.ast as t  # noqa: F401, `t` used in string types to avoid circular import
    from xb.interpreter.environment import Environment

class Op:
    """
    The supported operations on Value instances. Delegates the implementation
    to the appropriate subclass methods if necessary.

    The following operators are lazy and thus are handled in AST evaluation:
    - `&&`
    - `||`
    - `??`
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
    def sub(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "subtract")
        return a.sub(b)

    @staticmethod
    def mul(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "multiply")
        return a.mul(b)

    @staticmethod
    def div(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "divide")
        return a.div(b)

    @staticmethod
    def int_div(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "integer divide")
        return a.int_div(b)

    @staticmethod
    def mod(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "mod")
        return a.mod(b)

    @staticmethod
    def pow(a: Value, b: Value) -> Value:
        Op._type_guard(a, b, "exponentiate")
        return a.pow(b)

    @staticmethod
    def neg(a: Value) -> Value:
        return a.neg()

    @staticmethod
    def not_(a: Value) -> Value:
        return Boolean(not Boolean.cast(a)._bool)

    @staticmethod
    def index_get(target: Value, index: Value) -> Value:
        return target.index_get(index)

    @staticmethod
    def index_set(target: Value, index: Value, item: Value) -> None:
        target.index_set(index, item)

    @staticmethod
    def key_get(target: Value, key: str) -> Value:
        return target.key_get(key)

    @staticmethod
    def key_set(target: Value, key: str, item: Value) -> None:
        target.key_set(key, item)


class Value[Subclass, TreeNode]():
    type_name: str

    # Mainly for unit tests.
    def __bool__(self) -> bool:
        return Boolean.cast(self)._bool

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

    def mod(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support modulo"
        )

    def pow(self, other: Subclass) -> Value:
        _ = other
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support exponentiation"
        )

    def neg(self) -> Value:
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support negation"
        )

    def index_get(self, index: Value) -> Value:
        _ = index
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support index access"
        )

    def index_set(self, index: Value, item: Value) -> None:
        _ = index, item
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support index assignment"
        )

    def key_get(self, key: str) -> Value:
        _ = key
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support key access"
        )

    def key_set(self, key: str, item: Value) -> None:
        _ = key, item
        raise XbRuntimeError(
            f"type '{self.type_name}' does not support key assignment"
        )


class Empty(Value["Empty", "t.Empty"]):
    type_name = "()"

    @staticmethod
    def from_node(node, env):
        return Empty()

    def display(self) -> str:
        return self.type_name

    def eq(self, other) -> Value:
        # () is always equal to ()
        return Boolean(True)


class Boolean(Value["Boolean", "t.Bool"]):
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


class String(Value["String", "t.String"]):
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

    def lt(self, other) -> Value:
        return Boolean(self._str < other._str)

    def gt(self, other) -> Value:
        return Boolean(self._str > other._str)

    def add(self, other) -> Value:
        return String(self._str + other._str)


class Number(Value["Number", "t.Number"]):
    type_name = "number"

    def __init__(self, val: (int | float)) -> None:
        if type(val) is int or (i := int(val)) != val:
            self._val = val
        else:
            self._val = i

    @staticmethod
    def _parse_string(string: str) -> (int | float):
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
        return Number(Number._parse_string(node.token))

    @classmethod
    def cast(cls, value):
        match value:
            case Number(_val=v):
                return Number(v)
            case String(_str=s):
                return Number(Number._parse_string(s))

        return super().cast(value)

    def display(self) -> str:
        return str(self._val)

    def eq(self, other) -> Value:
        return Boolean(self._val == other._val)

    def lt(self, other) -> Value:
        return Boolean(self._val < other._val)

    def gt(self, other) -> Value:
        return Boolean(self._val > other._val)

    def add(self, other) -> Value:
        return Number(self._val + other._val)

    def sub(self, other) -> Value:
        return Number(self._val - other._val)

    def mul(self, other) -> Value:
        return Number(self._val * other._val)

    def div(self, other) -> Value:
        if other._val == 0:
            raise XbRuntimeError("division by 0")

        return Number(self._val / other._val)

    def int_div(self, other) -> Value:
        if other._val == 0:
            raise XbRuntimeError("division by 0")

        return Number(self._val // other._val)

    def mod(self, other) -> Value:
        if other._val == 0:
            raise XbRuntimeError("division by 0")

        return Number(self._val % other._val)

    def pow(self, other) -> Value:
        return Number(self._val ** other._val)

    def neg(self) -> Value:
        return Number(-self._val)


class Array(Value["Array", "t.Array"]):
    type_name = "array"

    def __init__(self, vals: list[Value]) -> None:
        self._list = vals

    @staticmethod
    def from_node(node, env):
        return Array([expr.evaluate(env) for expr in node.exprs])

    @classmethod
    def cast(cls, value: Value):
        if type(value) is Array:
            return value

        return super().cast(value)

    def display(self) -> str:
        # TODO: prettier printing?
        return f"[{", ".join(v.display() for v in self._list)}]"

    def eq(self, other) -> Value:
        # TODO: decide on deep equal or reference equal. perhaps another
        # keyword to indicate reference equality (like Python `is`)?
        len_eq = len(self._list) == len(other._list)
        vals_eq = all(Op.eq(s, o) for s, o in zip(self._list, other._list))
        return Boolean(len_eq and vals_eq)

    def _validate_index(self, index: Value) -> int:
        if type(index) is not Number:
            raise XbRuntimeError(
                f"cannot index type '{self.type_name}' with type '{index.type_name}'"
            )

        if type(index._val) is not int or index._val < 0:
            raise XbRuntimeError(f"{self.type_name} index must be a positive integer")

        if index._val >= len(self._list):
            raise XbRuntimeError(f"{self.type_name} index out of range")

        return index._val

    def index_get(self, index) -> Value:
        return self._list[self._validate_index(index)]

    def index_set(self, index, item) -> None:
        self._list[self._validate_index(index)] = item


class Object(Value["Object", "t.Object"]):
    type_name = "object"

    @dataclass
    class Entry:
        value: Value
        is_const: bool

    def __init__(self, d: dict[str, Object.Entry]) -> None:
        self._dict = d

    @staticmethod
    def from_node(node, env):
        def entry_from_pair(pair: t.Pair) -> tuple[str, Object.Entry]:
            key, value, const = pair.key_value_const(env)
            return key, Object.Entry(value, const)

        return Object({
            key: entry
            for key, entry in map(entry_from_pair, node.pairs)
        })

    @classmethod
    def cast(cls, value: Value):
        if type(value) is Object:
            return value

        return super().cast(value)

    def display(self) -> str:
        # TODO: prettier printing?
        def display_pair(k: str, e: Object.Entry) -> str:
            # TODO: handle cyclic refrerences somehow
            return (
                f"{k} : {e.value.display()}"
            ) if e.is_const else (
                f"{k} = {e.value.display()}"
            )

        return f"{{{
            ", ".join(display_pair(k, e) for k, e in self._dict.items())
        }}}"

    def eq(self, other) -> Value:
        # TODO: handle cyclic references
        count_eq = len(self._dict.items()) == len(other._dict.items())
        items_eq = all(
            k in other._dict.keys() \
                and e.is_const == other._dict[k].is_const \
                and Op.eq(e.value, other._dict[k].value)
            for k, e in self._dict.items()
        )
        return Boolean(count_eq and items_eq)

    def _validate_key(self, key: str) -> None:
        if key not in self._dict.keys():
            raise XbRuntimeError(f'unrecognized key "{key}"')

    def key_get(self, key: str) -> Value:
        self._validate_key(key)
        return self._dict[key].value

    def key_set(self, key: str, item: Value) -> None:
        self._validate_key(key)

        if self._dict[key].is_const:
            raise XbRuntimeError(f'field "{key}" is constant')

        self._dict[key].value = item
