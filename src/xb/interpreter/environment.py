from __future__ import annotations
from dataclasses import dataclass

from xb.interpreter.errors import XbRuntimeError


@dataclass
class EnvironmentEntry:
    value: object
    is_const: bool


class Environment:
    dict: dict[str, EnvironmentEntry]

    def __init__(self, parent: Environment | None = None) -> None:
        self.parent = parent

        self.dict = {}

    def __getitem__(self, name: str) -> object | None:
        if name in self.dict.keys():
            return self.dict[name].value

        if self.parent:
            return self.parent[name]

        raise XbRuntimeError(f"name '{name}' not recognized in this scope")

    def __setitem__(self, name: str, value: object) -> None:
        if name in self.dict.keys():
            if self.dict[name].is_const:
                raise XbRuntimeError(f"name '{name}' is constant")

            self.dict[name].value = value

        elif self.parent:
            self.parent[name] = value

        else:
            raise XbRuntimeError(f"name '{name}' not recognized in this scope")

    def declare_const(self, name: str, value: object) -> None:
        if name in self.dict.keys():
            raise XbRuntimeError(f"name '{name}' is already bound")

        self.dict[name] = EnvironmentEntry(value, True)

    def declare_var(self, name: str, value: object) -> None:
        if name in self.dict.keys():
            raise XbRuntimeError(f"name '{name}' is already bound")

        self.dict[name] = EnvironmentEntry(value, False)
