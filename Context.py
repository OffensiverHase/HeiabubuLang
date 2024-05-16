from __future__ import annotations


class Context:
    def __init__(self, parent: Context | None, name: str, file: str, file_text: str):
        self.parent = parent
        self.name = name
        self.file = file
        self.file_text = file_text

    def __str__(self):
        return f'\n{self.file}:\t\t{self.name}' if not self.parent else f'\n{self.file}:\t\t{self.name}{self.parent}'

