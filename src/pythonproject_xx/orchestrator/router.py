from __future__ import annotations

DEFAULT_MAPPING = {
    "architect": "mock:tiny",
    "codegen": "mock:tiny",
    "tester": "mock:tiny",
    "critic": "mock:tiny",
}

class Router:
    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping or DEFAULT_MAPPING

    def model_for(self, role: str) -> str:
        return self.mapping.get(role, "mock:tiny")