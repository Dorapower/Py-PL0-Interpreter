#!/usr/bin/env python3.11
# This file implements a parser for PL/0 source code.
from __future__ import annotations

from typing import NamedTuple, TypeAlias

from lexer import Token, TokenType, Lexer

ASTNode: TypeAlias = NamedTuple


class Factor(ASTNode):
    """
    Represents a factor in a term
    """
    value: int | str | Expression


class Term(ASTNode):
    """
    Represents a term in an expression
    """
    factors: list[Factor]
    ops: list[str]


class Expression(ASTNode):
    """
    Represents an expression
    """
    prefix: str
    terms: list[Term]
    ops: list[str]


class Const(ASTNode):
    """
    Represents a constant declaration
    """
    name: str
    value: int


class Var(ASTNode):
    """
    Represents a variable declaration
    """
    name: str


class Assignment(ASTNode):
    """
    Represents an assignment statement
    """
    name: str
    expr: Expression


class Call(ASTNode):
    """
    Represents a call statement
    """
    name: str


Condition: TypeAlias = NamedTuple


class OddCondition(Condition):
    """
    Represents an odd statement
    """
    expr: Expression


class ComparisonCondition(Condition):
    """
    Represents a comparison condition
    """
    op: str
    lhs: Expression
    rhs: Expression


class If(ASTNode):
    """
    Represents an if statement
    """
    cond: Condition
    stmt: Statement


class While(ASTNode):
    """
    Represents a while statement
    """
    cond: Condition
    stmt: Statement


class Begin(ASTNode):
    """
    Represents a begin statement
    """
    body: list[Statement]


# TODO: Add support for communication primitives
class Statement(ASTNode):
    """
    Represents a statement
    """
    stmt: Assignment | Call | If | While | Begin


class Block(ASTNode):
    """
    Represents a block
    """
    consts: list[Const]
    vars: list[Var]
    procs: list[Procedure]
    stmt: Statement


class Procedure(ASTNode):
    """
    Represents a procedure
    """
    ident: str
    body: Block


class Program(ASTNode):
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

    def parse_program(self) -> Program:
        """
        Parses a program
        """
        block = self.parse_block()
        if not self.check(Token.op('.')):
            raise SyntaxError('Expected "."')
        return Program(block)

    def parse_block(self) -> Block:
        """
        Parses a block
        """
        consts = []
        variables = []
        procs = []
        if self.check(Token.keyword('const')):
            consts = self.parse_constants()
        if self.check(Token.keyword('var')):
            variables = self.parse_variables()
        while self.check(Token.keyword('procedure')):
            procs.append(self.parse_procedure())
        stmt = self.parse_statement()
        return Block(consts, variables, procs, stmt)

    def parse_constants(self) -> list[Const]:
        """
        Parses a list of constants
        """
        consts = []
        while True:
            name = self.parse_identifier()
            if not self.check(Token.op('=')):
                raise SyntaxError('Expected "="')
            value = self.parse_number()
            consts.append(Const(name, value))
            if not self.check(Token.op(',')):
                break
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return consts

    def parse_variables(self) -> list[Var]:
        """
        Parses a list of variables
        """
        variables = []
        while True:
            name = self.parse_identifier()
            variables.append(Var(name))
            if not self.check(Token.op(',')):
                break
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return variables

    def parse_identifier(self) -> str:
        """
        Parses an identifier
        """
        ident = self.lx.next()
        if ident.type != TokenType.Name:
            raise SyntaxError('Expected name')
        return ident.value

    def parse_number(self) -> int:
        """
        Parses a number
        """
        num = self.lx.next()
        if num.type != TokenType.Number:
            raise SyntaxError('Expected number')
        return num.value

    def parse_procedure(self) -> Procedure:
        """
        Parses a procedure
        """
        ident = self.parse_identifier()
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        block = self.parse_block()
        if not self.check(Token.op(';')):
            raise SyntaxError('Expected ";"')
        return Procedure(ident, block)

    def parse_statement(self) -> Statement:
        """
        Parses a statement
        """
        if self.check(Token.keyword('begin')):
            return Statement(self.parse_begin_statement())
        elif self.check(Token.keyword('if')):
            return Statement(self.parse_if_statement())
        elif self.check(Token.keyword('while')):
            return Statement(self.parse_while_statement())
        elif self.check(Token.keyword('call')):
            return Statement(self.parse_call_statement())
        else:
            return Statement(self.parse_assignment_statement())

    def parse_begin_statement(self) -> Begin:
        """
        Parses a begin statement
        """
        body = [self.parse_statement()]
        while not self.check(Token.keyword('end')):
            if not self.check(Token.op(';')):
                raise SyntaxError('Expected ";"')
            body.append(self.parse_statement())
        return Begin(body)

    def parse_if_statement(self) -> If:
        """
        Parses an if statement
        """
        cond = self.parse_condition()
        if not self.check(Token.keyword('then')):
            raise SyntaxError('Expected "then"')
        stmt = self.parse_statement()
        return If(cond, stmt)

    def parse_while_statement(self) -> While:
        """
        Parses a while statement
        """
        cond = self.parse_condition()
        if not self.check(Token.keyword('do')):
            raise SyntaxError('Expected "do"')
        stmt = self.parse_statement()
        return While(cond, stmt)

    def parse_condition(self) -> Condition:
        """
        Parses a condition
        """
        if self.check(Token.keyword('odd')):
            return self.parse_odd_condition()
        else:
            return self.parse_comparison_condition()

    def parse_odd_condition(self) -> OddCondition:
        """
        Parses an odd statement
        """
        expr = self.parse_expression()
        return OddCondition(expr)

    def parse_comparison_condition(self) -> ComparisonCondition:
        """
        Parses a comparison
        """
        left = self.parse_expression()
        op = self.lx.next()
        if op.type != TokenType.Op:
            raise SyntaxError('Expected operator')
        right = self.parse_expression()
        return ComparisonCondition(op.value, left, right)

    def parse_call_statement(self) -> Call:
        """
        Parses a call statement
        """
        ident = self.parse_identifier()
        return Call(ident)

    def parse_assignment_statement(self) -> Assignment:
        """
        Parses an assignment statement
        """
        ident = self.parse_identifier()
        if not self.check(Token.op(':=')):
            raise SyntaxError('Expected ":="')
        expr = self.parse_expression()
        return Assignment(ident, expr)

    def parse_expression(self) -> Expression:
        """
        Parses an expression
        """
        prefix = ''
        terms, ops = [], []
        if self.check(Token.op('+')):
            prefix = '+'
        elif self.check(Token.op('-')):
            prefix = '-'
        terms.append(self.parse_term())
        while True:
            if self.check(Token.op('+')):
                ops.append('+')
            elif self.check(Token.op('-')):
                ops.append('-')
            else:
                break
            terms.append(self.parse_term())
        return Expression(prefix, terms, ops)

    def parse_term(self) -> Term:
        """
        Parses a term
        """
        factors, ops = [], []
        factors.append(self.parse_factor())
        while True:
            if self.check(Token.op('*')):
                ops.append('*')
            elif self.check(Token.op('/')):
                ops.append('/')
            else:
                break
            factors.append(self.parse_factor())
        return Term(factors, ops)

    def parse_factor(self) -> Factor:
        """
        Parses a factor
        """
        token = self.lx.peek()
        if token == Token.op('('):
            expr = self.parse_expression()
            if not self.check(Token.op(')')):
                raise SyntaxError('Expected ")"')
            return Factor(expr)
        elif token.type == TokenType.Name:
            return Factor(self.parse_identifier())
        elif token.type == TokenType.Number:
            return Factor(self.parse_number())
        raise SyntaxError('Expected name or number')


def main():
    import sys
    print("Enter a program:")
    program = sys.stdin.read()
    parser = Parser(Lexer(program))
    try:
        print(parser.parse_program())
    except SyntaxError as e:
        print(e)


if __name__ == '__main__':
    main()
