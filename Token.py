from __future__ import annotations

from enum import Enum
from typing import Any


class Position:
    """A class representing the exact Position of a token for error logging"""
    def __init__(self, index: int, line: int, column: int, length: int) -> None:
        self.index = index
        self.line = line
        self.column = column
        self.len = length

    def advance(self, char: str) -> None:
        self.index += 1
        self.column += 1
        if char == '\n':
            self.line += 1
            self.column = 0

    def copy(self) -> Position:
        """Has to always be called, when giving into token objects in the Lexer, else further advances will also affect this position, invalidating data"""
        return Position(self.index, self.line, self.column, self.len)


class Token:
    """Tokens representing the smallest possible units a program is made of"""
    def __init__(self, token_type: TT, value: Any | None, pos: Position):
        self.type = token_type
        self.value = value
        self.pos = pos

    def __str__(self) -> str:
        return f'{self.type.value}: {self.value}' if self.value else f'{self.type.value}'

    def __repr__(self) -> str:
        return str(self)


class TT(Enum):
    """Enum for Token types mapping name to representation"""
    INT = 'int'
    FLOAT = 'float'
    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
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
    NEWLINE = '\n'
    LCURLY = '{'
    RCURLY = '}'
    DOT = '.'
    TO = '..'
    TYPE = 'type'
    ARROW = '->'
    EOF = 'end of file'
