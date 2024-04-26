from __future__ import annotations

from llvmlite import ir


class Environment:
    def __init__(self, records: dict[str, tuple[ir.Value, ir.Type]] | None = None, parent: Environment | None = None,
                 name: str = 'main'):
        self.records = records if records else {}
        self.parent = parent
        self.name = name

    def define(self, name: str, value: ir.Value, _type: ir.Type) -> ir.Value:
        self.records[name] = (value, _type)
        return value

    def lookup(self, name: str) -> tuple[ir.Value, ir.Type]:
        return self.__resolve(name)

    def __resolve(self, name: str) -> tuple[ir.Value, ir.Type] | None:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.__resolve(name)
        else:
            return None
