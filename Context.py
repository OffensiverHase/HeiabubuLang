from __future__ import annotations


class Context:
    def __init__(self, parent: Context | None, name: str, var_map: VarMap, file: str, file_text: str):
        self.parent = parent
        self.name = name
        self.var_map = var_map
        self.file = file
        self.file_text = file_text

    def __str__(self):
        return self.name if not self.parent else f'\n\t\t{self.name}\t\t:{self.file}{self.parent}'


class VarMap:
    pass
