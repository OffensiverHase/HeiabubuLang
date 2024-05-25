from __future__ import annotations

from typing import List

from Context import Context
from Error import IllegalCharError, InvalidSyntaxError
from Methods import fail
from Token import Position, Token, TT


class Lexer:
    """Class for Lexical Analysis, split the text into tokens"""
    def __init__(self, context: Context) -> None:
        self.context = context
        self.text = context.file_text
        self.pos = Position(-1, 0, -1, 1)
        self.current_char: str | None = None
        self.escape_chars = dict(n='\n', t='\t')
        self.types = dict(INT='int', FLOAT='float', NULL='null', BOOL='bool', STR='str', BYTE='byte', LIST='list')
        self._advance()

    def _advance(self) -> None:
        self.pos.advance(self.current_char if self.current_char else ' ')
        self.current_char = self.text[self.pos.index] if self.pos.index < len(self.text) else None

    def make_tokens(self) -> List[Token] | IllegalCharError:
        """Split the whole text into tokens, ignore whitespaces, carriage returns and comments"""
        tokens: List[Token] = []
        while self.current_char:
            match self.current_char:
                case ' ':
                    self._advance()
                case '':
                    self._advance()
                case '\t':
                    self._advance()
                case '\r':
                    self._advance()

                case '#':
                    self._remove_comment()

                case '\n':
                    tokens.append(Token(TT.NEWLINE, None, self.pos.copy()))
                    self._advance()

                case ';':
                    tokens.append(Token(TT.NEWLINE, None, self.pos.copy()))
                    self._advance()

                case '+':
                    tokens.append(Token(TT.PLUS, None, self.pos.copy()))
                    self._advance()

                case '*':
                    tokens.append(Token(TT.MUL, None, self.pos.copy()))
                    self._advance()

                case '/':
                    tokens.append(Token(TT.DIV, None, self.pos.copy()))
                    self._advance()

                case '^':
                    tokens.append(Token(TT.POW, None, self.pos.copy()))
                    self._advance()

                case '(':
                    tokens.append(Token(TT.LPAREN, None, self.pos.copy()))
                    self._advance()

                case ')':
                    tokens.append(Token(TT.RPAREN, None, self.pos.copy()))
                    self._advance()

                case '!':
                    tokens.append(Token(TT.NOT, None, self.pos.copy()))
                    self._advance()

                case '=':
                    tokens.append(Token(TT.EQUALS, None, self.pos.copy()))
                    self._advance()

                case '&':
                    tokens.append(Token(TT.AND, None, self.pos.copy()))
                    self._advance()

                case '|':
                    tokens.append(Token(TT.OR, None, self.pos.copy()))
                    self._advance()

                case '~':
                    tokens.append(Token(TT.XOR, None, self.pos.copy()))
                    self._advance()

                case ',':
                    tokens.append(Token(TT.COMMA, None, self.pos.copy()))
                    self._advance()

                case '[':
                    tokens.append(Token(TT.LSQUARE, None, self.pos.copy()))
                    self._advance()

                case ']':
                    tokens.append(Token(TT.RSQUARE, None, self.pos.copy()))
                    self._advance()

                case ':':
                    tokens.append(Token(TT.COLON, None, self.pos.copy()))
                    self._advance()

                case '{':
                    tokens.append(Token(TT.LCURLY, None, self.pos.copy()))
                    self._advance()

                case '}':
                    tokens.append(Token(TT.RCURLY, None, self.pos.copy()))
                    self._advance()

                case '-':
                    tokens.append(self._make_minus_things())

                case '.':
                    tokens.append(self._make_dot_things())

                case '<':
                    tokens.append(self._make_smaller_things())

                case '>':
                    tokens.append(self._make_bigger_things())

                case "'":
                    tokens.append(self._make_string())

                case _:
                    if self.current_char.isdigit():
                        tokens.append(self._make_number())
                    elif self.current_char.isalpha():
                        tokens.append(self._make_identifier())
                    else:
                        return IllegalCharError(f'Found illegal char: {self.current_char}', self.pos, self.context,
                                                'tokenizing')
        tokens.append(Token(TT.EOF, None, self.pos.copy()))
        return tokens

    def _make_identifier(self) -> Token:
        id_str = ""
        start_pos = self.pos.copy()

        while self.current_char and (self.current_char.isalnum() or self.current_char in '_$'):
            id_str += self.current_char
            self._advance()

        if id_str.upper() in self.types:
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.TYPE, id_str, start_pos)
        elif id_str.upper() in TT.keywords.value:
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.KEYWORD, id_str.upper(), start_pos)
        else:
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.IDENTIFIER, id_str, start_pos)

    def _make_number(self) -> Token:
        number_str = ""
        dot_count = 0
        start_pos = self.pos.copy()
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 0:
                    dot_count += 1
                else:
                    break
            number_str += self.current_char
            self._advance()

        start_pos.len = self.pos.index - start_pos.index
        if dot_count == 0:
            return Token(TT.INT, int(number_str), start_pos)
        return Token(TT.FLOAT, float(number_str), start_pos)

    def _make_string(self) -> Token:
        start_pos = self.pos.copy()
        self._advance()
        str_str = ""
        escape = False
        while self.current_char and self.current_char != "'" or escape:
            if escape:
                escape = False
                str_str += self.escape_chars.get(self.current_char, self.current_char)
            elif self.current_char == '\'':
                escape = True
            else:
                str_str += self.current_char
            self._advance()
        if not self.current_char:
            fail(InvalidSyntaxError(f"Unclosed string literal'{str_str}'", start_pos, self.context, 'tokenizing'))
        self._advance()
        start_pos.len = self.pos.index - start_pos.index
        return Token(TT.STRING, str_str, start_pos)

    def _remove_comment(self) -> None:
        while self.current_char and self.current_char != '\n':
            self._advance()

        self._advance()

    def _make_smaller_things(self) -> Token:
        start_pos = self.pos.copy()
        self._advance()
        match self.current_char:
            case '=':
                self._advance()
                start_pos.len = self.pos.index - start_pos.index
                return Token(TT.LESSEQUAL, None, start_pos)
            case '>':
                self._advance()
                start_pos.len = self.pos.index - start_pos.index
                return Token(TT.UNEQUALS, None, start_pos)
            case '-':
                self._advance()
                start_pos.len = self.pos.index - start_pos.index
                return Token(TT.ASSIGN, None, start_pos)
            case _:
                return Token(TT.LESS, None, start_pos)

    def _make_bigger_things(self) -> Token:
        start_pos = self.pos.copy()
        self._advance()
        if self.current_char == '=':
            self._advance()
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.GREATEREQUAL, None, start_pos)
        else:
            return Token(TT.GREATER, None, start_pos)

    def _make_dot_things(self) -> Token:
        start_pos = self.pos.copy()
        self._advance()
        if self.current_char == '.':
            self._advance()
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.TO, None, start_pos)
        else:
            return Token(TT.DOT, None, start_pos)

    def _make_minus_things(self) -> Token:
        start_pos = self.pos.copy()
        self._advance()
        if self.current_char == '>':
            self._advance()
            start_pos.len = self.pos.index - start_pos.index
            return Token(TT.ARROW, None, start_pos)
        else:
            return Token(TT.MINUS, None, self.pos.copy())
