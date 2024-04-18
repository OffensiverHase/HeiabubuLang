from __future__ import annotations

from enum import Enum
from typing import Any


class Position:
    def __init__(self, index: int, line: int, column: int) -> None:
        self.index = index
        self.line = line
        self.column = column

    def advance(self, char: str) -> None:
        self.index += 1
        self.column += 1
        if char == '\n':
            self.line += 1
            self.column = 0

    def copy(self) -> Position:
        return Position(self.index, self.line, self.column)


class Token:
    def __init__(self, token_type: TT, value: Any | None, pos: Position):
        self.type = token_type
        self.value = value
        self.pos = pos

    def __str__(self) -> str:
        return f'{self.type.name}: {self.value}' if self.value else f'{self.type.name}'

    def __repr__(self) -> str:
        return str(self)


class TT(Enum):
    keywords = ['VAR', 'IF', 'THEN', 'ELSE', 'FOR', 'STEP', 'WHILE', 'FUN', 'RETURN', 'BREAK', 'CONTINUE', 'OBJECT']
    INT = 'int'
    FLOAT = 'float'
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    POW = '^'
    LPAREN = '('
    RPAREN = ')'
    IDENTIFIER = 'identifier'
    KEYWORD = 'keyword'
    ASSIGN = '<-'
    EQUALS = '='
    UNEQUALS = '<>'
    LESS = '<'
    GREATER = '>'
    LESSEQUAL = '<='
    GREATEREQUAL = '>='
    NOT = '!'
    AND = '&'
    OR = '|'
    XOR = '~'
    COMMA = ','
    STRING = 'string'
    LSQUARE = '['
    RSQUARE = ']'
    GET = '[...]'
    COLON = ':'
    NEWLINE = '\\n'
    LCURLY = '{'
    RCURLY = '}'
    DOT = '.'
    TO = '..'
    TYPE = 'type'
    ARROW = '->'
    EOF = 'end of file'
