# This file implements a parser for PL/0 source code.

from enum import IntEnum
from enum import StrEnum
from typing import List, NamedTuple
import string

class TokenType(IntEnum):
    Op      = 0
    Number  = 1
    Name    = 2
    Keyword = 3
    EOF     = 4

VALID_IDENTITFIER_STARTS:str = string.ascii_letters + '_'
VAILD_IDENTIFIERS:str = string.ascii_letters + string.digits + '_'

class Keyword(StrEnum):
    Begin = 'begin'
    Call = 'call'
    Const = 'const'
    Do = 'do'
    End = 'end'
    If = 'if'
    Odd = 'odd'
    Procedure = 'procedure'
    Then = 'then'
    Var = 'var'
    While = 'while'

class Token:
    Type: TokenType
    Value: str | int

    def __init__(self, type:TokenType, value:str | int):
        self.type = type
        self.value = value

    @staticmethod
    def op(op:str):
        return Token(TokenType.Op, op)

    @staticmethod
    def number(number:int):
        return Token(TokenType.Number, number)

    @staticmethod
    def name(name:str):
        return Token(TokenType.Name, name)

    @staticmethod
    def keyword(keyword:str):
        return Token(TokenType.Keyword, keyword)

    @staticmethod
    def eof():
        return Token(TokenType.EOF, 0)

    def __str__(self):
        return f'Token({self.type}, {self.value})'


class Lexer:
    _i: int
    _s: str

    def __init__(self, s:str):
        self._s = s
        self._i = 0

    @property
    def eof(self) -> bool:
        return self._i >= len(self._s)

    def _skip_whitespace(self):
        while not self.eof and self._s[self._i].isspace():
            self._i += 1
    
    def next(self) -> Token:
        val = ''
        self._skip_whitespace()
        
        # Check for EOF
        if self.eof:
            return Token.eof()
        
        # Check for number
        if self._s[self._i].isdigit():
            while not self.eof and self._s[self._i].isdigit():
                val += self._s[self._i]
                self._i += 1
            return Token.number(int(val))
            
        # Check for keywords
        for keyword in Keyword:
            if self._s[self._i:].startswith(keyword.value):
                self._i += len(keyword.value)
                return Token.keyword(keyword.value)

        # Check for identifier
        if self._s[self._i] in VALID_IDENTITFIER_STARTS:
            while not self.eof and self._s[self._i] in VAILD_IDENTIFIERS:
                val += self._s[self._i]
                self._i += 1
            return Token.name(val)

        # Check for single character operator
        if self._s[self._i] in '=#*+-/,;.()':
            val = self._s[self._i]
            self._i += 1
            return Token.op(val)

        # Check for assignment operator
        if self._s[self._i] == ':':
            self._i += 1
            if self._s[self._i] == '=':
                self._i += 1
                return Token.op(':=')
            else:
                raise SyntaxError('Invalid token')

        # Check for comparison operators
        if self._s[self._i] in '<>':
            val = self._s[self._i]
            self._i += 1
            if self._s[self._i] == '=':
                val += '='
                self._i += 1
            return Token.op(val)
        
        # Invalid token
        raise SyntaxError('Invalid token')


# class Const(NamedTuple):
#     """
#     Represents a constant declaration
#     """
#     name: str
#     value: int

# class Assignment(NamedTuple):
#     name: str
#     expr: Expression

# class Call(NamedTuple):
#     name: str

# class Begin(NamedTuple):
#     statements: List[Statement]



def test_lexer():
    test_program =\
    """
    var i, s;
    begin
    i := 0; s := 0;
    while i < 5 do
    begin
        i := i + 1;
        s := s + i * i
    end
    end.
    """
    lexer = Lexer(test_program)
    while not lexer.eof:
        print(lexer.next())

if __name__ == '__main__':
    test_lexer()