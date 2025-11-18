class XbError(Exception):
    def __init__(self, scope: str, message: str) -> None:
        self.scope = scope
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"error({self.scope}): {self.message}"


class XbRuntimeError(XbError):
    def __init__(self, message: str) -> None:
        super().__init__("runtime", message)
