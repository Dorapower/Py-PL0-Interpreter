#!/usr/bin/env python3.11
# This file implements a parser for PL/0 source code.
from __future__ import annotations

from typing import NamedTuple

from lexer import Token, TokenType, Lexer


class Factor(NamedTuple):
    """
    Represents a factor in a term
    """
    value: int | str | Expression


class Term(NamedTuple):
    """
    Represents a term in an expression
    """
    factors: list[Factor]
    ops: list[str]


class Expression(NamedTuple):
    """
    Represents an expression
    """
    prefix: str
    terms: list[Term]
    ops: list[str]


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
    body: list[Statement]


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
    consts: list[Const]
    vars: list[Var]
    procs: list[Procedure]
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
        next_token = self.lx.peek()
        if next_token == token:
            self.lx.next()
            return True
        # if the next_token is a name, we don't need to check the value
        if next_token.type == TokenType.Name and token.type == TokenType.Name:
            self.lx.next()
            return True
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

    def consts(self) -> list[Const]:
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

    def vars(self) -> list[Var]:
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
        body = [self.statement()]
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
        prefix = ''
        terms, ops = [], []
        if self.check(Token.op('+')):
            prefix = '+'
        elif self.check(Token.op('-')):
            prefix = '-'
        terms.append(self.term())
        while True:
            if self.check(Token.op('+')):
                ops.append('+')
            elif self.check(Token.op('-')):
                ops.append('-')
            else:
                break
            terms.append(self.term())
        return Expression(prefix, terms, ops)

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


def main():
    import sys
    print("Enter a program:\n")
    program = sys.stdin.read()
    parser = Parser(Lexer(program))
    try:
        print(parser.program())
    except SyntaxError as e:
        print(e)


if __name__ == '__main__':
    main()