from __future__ import annotations


class Context:
    def __init__(self, parent: Context | None, name: str, file: str, file_text: str):
        self.parent = parent
        self.name = name
        self.file = file
        self.file_text = file_text

    def __str__(self):
        return f'\tsrc --> {self.file}\n\tfun -> {self.name}\n'

