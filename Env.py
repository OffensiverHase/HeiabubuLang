from __future__ import annotations

from typing import Tuple

from llvmlite import ir
from llvmlite.ir import Value, Type


class Environment:
    """variable table used by the IrBuilder. name: str -> value: ir.Value, type: ir.Type"""
    def __init__(self, records: dict[str, tuple[ir.Value, ir.Type]] | None = None, parent: Environment | None = None,
                 name: str = 'main'):
        self.records = records if records else {}
        self.parent = parent
        self.name = name

    def define(self, name: str, value: ir.Value, _type: ir.Type) -> ir.Value:
        self.records[name] = (value, _type)
        return value

    def lookup(self, name: str) -> tuple[None, None] | tuple[Value, Type]:
        """helper function, because __resolve returns None on not found, what errors on unpacking"""
        value = self.__resolve(name)
        if not value:
            return None, None
        return value

    def __resolve(self, name: str) -> tuple[ir.Value, ir.Type] | None:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.__resolve(name)
        else:
            return None
