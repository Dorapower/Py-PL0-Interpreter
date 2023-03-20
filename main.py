#!/usr/bin/env python3.11
# This file implements a parser for PL/0 source code.
from __future__ import annotations

from enum import IntEnum
from enum import StrEnum
from typing import List, NamedTuple
import string


class TokenType(IntEnum):
    Op = 0
    Number = 1
    Name = 2
    Keyword = 3
    EOF = 4


VALID_IDENTIFIER_STARTS: str = string.ascii_letters + '_'
VALID_IDENTIFIERS: str = string.ascii_letters + string.digits + '_'


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

    def __init__(self, token_type: TokenType, value: str | int):
        self.type = token_type
        self.value = value

    @staticmethod
    def op(op: str):
        return Token(TokenType.Op, op)

    @staticmethod
    def number(number: int):
        return Token(TokenType.Number, number)

    @staticmethod
    def name(name: str = ''):
        return Token(TokenType.Name, name)

    @staticmethod
    def keyword(keyword: str):
        return Token(TokenType.Keyword, keyword)

    @staticmethod
    def eof():
        return Token(TokenType.EOF, 0)

    def __str__(self):
        return f'Token({self.type}, {self.value})'

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value


class Lexer:
    _i: int
    _s: str

    def __init__(self, s: str):
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
        if self._s[self._i] in VALID_IDENTIFIER_STARTS:
            while not self.eof and self._s[self._i] in VALID_IDENTIFIERS:
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

    @property
    def i(self):
        return self._i


# TODO: Separate AST into its own file

class Factor(NamedTuple):
    """
    Represents a factor in a term
    """
    value: int | str | Expression


class Term(NamedTuple):
    """
    Represents a term in an expression
    """
    factors: List[Factor]
    ops: List[str]


class Expression(NamedTuple):
    """
    Represents an expression
    """
    terms: List[Term]
    ops: List[str]


class Const(NamedTuple):
    """
    Represents a constant declaration
    """
    name: str
    value: int


class Var(NamedTuple):
    """
    Represents a variable declaration
    """
    name: str


class Assignment(NamedTuple):
    """
    Represents an assignment statement
    """
    name: str
    expr: Expression


class Call(NamedTuple):
    """
    Represents a call statement
    """
    name: str


class OddCondition(NamedTuple):
    """
    Represents an odd statement
    """
    expr: Expression


class ComparisonCondition(NamedTuple):
    """
    Represents a comparison condition
    """
    op: str
    lhs: Expression
    rhs: Expression


class Condition(NamedTuple):
    """
    Represents a condition
    """
    condition: OddCondition | ComparisonCondition


class If(NamedTuple):
    """
    Represents an if statement
    """
    cond: Condition
    stmt: Statement


class While(NamedTuple):
    """
    Represents a while statement
    """
    cond: Condition
    stmt: Statement


class Begin(NamedTuple):
    """
    Represents a begin statement
    """
    body: List[Statement]


# TODO: Add support for communication primitives
class Statement(NamedTuple):
    """
    Represents a statement
    """
    stmt: Assignment | Call | If | While | Begin


class Block(NamedTuple):
    """
    Represents a block
    """
    consts: List[Const]
    vars: List[Var]
    procs: List[Procedure]
    stmt: Statement


class Procedure(NamedTuple):
    """
    Represents a procedure
    """
    ident: str
    body: Block


class Program(NamedTuple):
    """
    Represents a program
    """
    block: Block


class Parser:
    lx: Lexer

    def __init__(self, lx: Lexer):
        self.lx = lx

    def check(self, token: Token) -> bool:
        """
        Checks if the next token is the given token, and if so, consumes it
        """
        cur = self.lx.i
        next_token = self.lx.next()
        if next_token == token:
            return True
        # if the next_token is a name, we don't need to check the value
        if next_token.type == TokenType.Name and token.type == TokenType.Name:
            return True
        self.lx._i = cur
        return False

    def program(self) -> Program:
        """
        Parses a program
        """
        block = self.block()
        if not self.check(Token.op('.')):
            raise SyntaxError('Expected "."')
        return Program(block)

    def block(self) -> Block:
        """
        Parses a block
        """
        consts = []
        variables = []
        procs = []
        if self.check(Token.keyword('const')):
            consts = self.consts()
        if self.check(Token.keyword('var')):
            variables = self.vars()
        while self.check(Token.keyword('procedure')):
            procs.append(self.procedure())
        stmt = self.statement()
        return Block(consts, variables, procs, stmt)

    def consts(self) -> List[Const]:
        """
        Parses a list of constants
        """
        consts = []
        while True:
            name = self.name()
            if not self.check(Token.op('=')):
                raise SyntaxError('Expected "="')
            value = self.number()
            consts.append(Const(name, value))
            if not self.check(Token.op(',')):
                break
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return consts

    def vars(self) -> List[Var]:
        """
        Parses a list of variables
        """
        variables = []
        while True:
            name = self.name()
            variables.append(Var(name))
            if not self.check(Token.op(',')):
                break
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return variables

    def name(self) -> str:
        """
        Parses a name
        """
        ident = self.lx.next()
        if ident.type != TokenType.Name:
            raise SyntaxError('Expected name')
        return ident.value

    def number(self) -> int:
        """
        Parses a number
        """
        num = self.lx.next()
        if num.type != TokenType.Number:
            raise SyntaxError('Expected number')
        return num.value

    def name_or_number(self) -> str | int:
        """
        Parses a name or number
        """
        ident = self.lx.next()
        if ident.type == TokenType.Name:
            return ident.value
        elif ident.type == TokenType.Number:
            return ident.value
        raise SyntaxError('Expected name or number')

    def procedure(self) -> Procedure:
        """
        Parses a procedure
        """
        ident = self.name()
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        block = self.block()
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return Procedure(ident, block)

    def statement(self) -> Statement:
        """
        Parses a statement
        """
        if self.check(Token.keyword('begin')):
            return Statement(self.begin())
        elif self.check(Token.keyword('if')):
            return Statement(self.if_statement())
        elif self.check(Token.keyword('while')):
            return Statement(self.while_statement())
        elif self.check(Token.keyword('call')):
            return Statement(self.call())
        else:
            return Statement(self.assignment())

    def begin(self) -> Begin:
        """
        Parses a begin statement
        """
        body = []
        body.append(self.statement())
        while not self.check(Token.keyword('end')):
            if not self.check(Token.op(';')):
                raise SyntaxError('Expected ";"')
            body.append(self.statement())
        return Begin(body)

    def if_statement(self) -> If:
        """
        Parses an if statement
        """
        cond = self.condition()
        if not self.check(Token.keyword('then')):
            raise SyntaxError('Expected "then"')
        stmt = self.statement()
        return If(cond, stmt)

    def while_statement(self) -> While:
        """
        Parses a while statement
        """
        cond = self.condition()
        if not self.check(Token.keyword('do')):
            raise SyntaxError('Expected "do"')
        stmt = self.statement()
        return While(cond, stmt)

    def condition(self) -> Condition:
        """
        Parses a condition
        """
        if self.check(Token.keyword('odd')):
            return Condition(self.odd())
        else:
            return Condition(self.comparison())

    def odd(self) -> OddCondition:
        """
        Parses an odd statement
        """
        expr = self.expression()
        return OddCondition(expr)

    def comparison(self) -> ComparisonCondition:
        """
        Parses a comparison
        """
        left = self.expression()
        op = self.lx.next()
        if op.type != TokenType.Op:
            raise SyntaxError('Expected operator')
        right = self.expression()
        return ComparisonCondition(op.value, left, right)

    def call(self) -> Call:
        """
        Parses a call statement
        """
        ident = self.name()
        return Call(ident)

    def assignment(self) -> Assignment:
        """
        Parses an assignment statement
        """
        ident = self.name()
        if not self.check(Token.op(':=')):
            raise SyntaxError('Expected ":="')
        expr = self.expression()
        return Assignment(ident, expr)

    def expression(self) -> Expression:
        """
        Parses an expression
        """
        terms, ops = [], []
        terms.append(self.term())
        while True:
            if self.check(Token.op('+')):
                ops.append('+')
            elif self.check(Token.op('-')):
                ops.append('-')
            else:
                break
            terms.append(self.term())
        return Expression(terms, ops)

    def term(self) -> Term:
        """
        Parses a term
        """
        factors, ops = [], []
        factors.append(self.factor())
        while True:
            if self.check(Token.op('*')):
                ops.append('*')
            elif self.check(Token.op('/')):
                ops.append('/')
            else:
                break
            factors.append(self.factor())
        return Term(factors, ops)

    def factor(self) -> Factor:
        """
        Parses a factor
        """
        if self.check(Token.op('(')):
            expr = self.expression()
            if not self.check(Token.op(')')):
                raise SyntaxError('Expected ")"')
            return Factor(expr)
        else:
            return Factor(self.name_or_number())


def test_lexer():
    test_program = \
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


def test_parser():
    test_program = \
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
    parser = Parser(Lexer(test_program))
    print(parser.program())


if __name__ == '__main__':
    test_parser()
