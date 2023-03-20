#!/usr/bin/env python3.11
# This file implements a simple lexer for the PL/0 language.
from __future__ import annotations

import string
from enum import Enum, StrEnum, auto
from typing import NamedTuple


class TokenType(Enum):
    Op = auto()
    Number = auto()
    Name = auto()
    Keyword = auto()
    EOF = auto()


VALID_IDENTIFIER_STARTS: str = string.ascii_letters + '_'
VALID_IDENTIFIER_CONTINUES: str = string.ascii_letters + string.digits + '_'


class Keyword(StrEnum):
    BEGIN = 'begin'
    CALL = 'call'
    CONST = 'const'
    DO = 'do'
    END = 'end'
    IF = 'if'
    ODD = 'odd'
    PROCEDURE = 'procedure'
    THEN = 'then'
    VAR = 'var'
    WHILE = 'while'


class Token(NamedTuple):
    type: TokenType
    value: str | int | None = None

    @staticmethod
    def op(val: str, /) -> Token:
        return Token(TokenType.Op, val)

    @staticmethod
    def number(val: int, /) -> Token:
        return Token(TokenType.Number, val)

    @staticmethod
    def name(val: str, /) -> Token:
        return Token(TokenType.Name, val)

    @staticmethod
    def keyword(val: str, /) -> Token:
        return Token(TokenType.Keyword, val)

    @staticmethod
    def eof() -> Token:
        return Token(TokenType.EOF)


class Lexer:
    """
    A simple lexer for the PL/0 language.
    Call next() for the next token, and peek() to see the next token.
    """
    _i: int
    _s: str
    _length: int
    _current: Token

    def __init__(self, s: str, /) -> None:
        self._i = 0
        self._s = s
        self._length = len(s)
        self._current = self._next()

    @property
    def eof(self):
        return self._current.type == TokenType.EOF

    def _eof(self):
        return self._i >= self._length

    def _skip_whitespace(self) -> None:
        while not self._eof() and self._s[self._i].isspace():
            self._i += 1

    def _next(self):
        val = ''
        self._skip_whitespace()

        # Check for EOF
        if self._eof():
            return Token.eof()

        # Check for a number
        if self._s[self._i].isdigit():
            while not self._eof() and self._s[self._i].isdigit():
                val += self._s[self._i]
                self._i += 1
            return Token.number(int(val))

        # Check for an identifier or keyword
        if self._s[self._i] in VALID_IDENTIFIER_STARTS:
            while not self._eof() and self._s[self._i] in VALID_IDENTIFIER_CONTINUES:
                val += self._s[self._i]
                self._i += 1
            if val in Keyword.__members__.values():
                return Token.keyword(val)
            return Token.name(val)

        # Check for a two character operator
        if self._s[self._i:self._i + 2] in [':=', '<=', '>=']:
            val = self._s[self._i:self._i + 2]
            self._i += 2
            return Token.op(val)

        # Check for a single character operator
        if self._s[self._i] in '+-*/=#,;.()<>':
            val = self._s[self._i]
            self._i += 1
            return Token.op(val)

        raise ValueError(f'Invalid character: {self._s[self._i]}')

    def next(self):
        """
        Get the next token.
        """
        token = self._current
        self._current = self._next()
        return token

    def peek(self):
        """
        Peek at the next token.
        """
        return self._current


def main():
    import sys
    print('Enter a program:\n')
    src = sys.stdin.read()
    lexer = Lexer(src)
    while not lexer.eof:
        print(lexer.next())


if __name__ == '__main__':
    main()
