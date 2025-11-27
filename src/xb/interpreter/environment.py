from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

from xb.interpreter.errors import XbRuntimeError

if TYPE_CHECKING:
    from xb.interpreter.value import Value


@dataclass
class EnvironmentEntry:
    value: Value
    is_const: bool


class Environment:
    _dict: dict[str, EnvironmentEntry]

    def __init__(self, parent: Environment | None = None) -> None:
        self.parent = parent

        self._dict = {}

    def __getitem__(self, name: str) -> Value:
        if name in self._dict.keys():
            return self._dict[name].value

        if self.parent:
            return self.parent[name]

        raise XbRuntimeError(f"name '{name}' not recognized in this scope")

    def __setitem__(self, name: str, value: Value) -> None:
        if name in self._dict.keys():
            if self._dict[name].is_const:
                raise XbRuntimeError(f"name '{name}' is constant")

            self._dict[name].value = value

        elif self.parent:
            self.parent[name] = value

        else:
            raise XbRuntimeError(f"name '{name}' not recognized in this scope")

    def declare_const(self, name: str, value: Value) -> None:
        if name in self._dict.keys():
            raise XbRuntimeError(f"name '{name}' is already bound")

        self._dict[name] = EnvironmentEntry(value, True)

    def declare_var(self, name: str, value: Value) -> None:
        if name in self._dict.keys():
            raise XbRuntimeError(f"name '{name}' is already bound")

        self._dict[name] = EnvironmentEntry(value, False)

    def is_const(self, name: str) -> bool:
        return self._dict[name].is_const
