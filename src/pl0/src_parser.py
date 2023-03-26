#!/usr/bin/env python3.11
# This file implements a parser for PL/0 source code.
from __future__ import annotations

from ast_node import Program, Block, Const, Procedure, Statement, \
    Assignment, Call, If, While, Begin, Condition, Expression, Term, \
    Factor, Var, OddCondition, ComparisonCondition, Read, Write
from src_lexer import Token, TokenType, Lexer


class Parser:
    lx: Lexer
    debug: bool

    def __init__(self, program: str, /, *, debug: bool = False):
        self.lx = Lexer(program)
        self.debug = debug

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

    def parse(self) -> Program:
        """
        Parses a program, identical to parse_program()
        """
        return self.parse_program()

    def parse_program(self) -> Program:
        """
        Parses a program
        """
        if self.debug:
            print('<DEBUG> Parser.parse_program(): Parsing program')
        block = self.parse_block()
        if not self.check(Token.op('.')):
            raise SyntaxError('Expected "."')
        return Program(block)

    def parse_block(self) -> Block:
        """
        Parses a block
        """
        if self.debug:
            print('<DEBUG> Parser.parse_block(): Parsing block')
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
        if self.debug:
            print('<DEBUG> Parser.parse_constants(): Parsing constants')
        consts = []
        while True:
            name = self.parse_identifier()
            if not self.check(Token.op('=')):
                raise SyntaxError('Expected "="')
            value = self.parse_number()
            if self.debug:
                print(f'<DEBUG> Parser.parse_constants(): Parsed constant {name} = {value}')
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
        if self.debug:
            print('<DEBUG> Parser.parse_variables(): Parsing variables')
        variables = []
        while True:
            name = self.parse_identifier()
            if self.debug:
                print(f'<DEBUG> Parser.parse_variables(): Parsed variable {name}')
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
        if self.debug:
            print('<DEBUG> Parser.parse_identifier(): Parsing identifier')
        ident = self.lx.next()
        if ident.type != TokenType.Name:
            raise SyntaxError('Expected name')
        if self.debug:
            print(f'<DEBUG> Parser.parse_identifier(): Parsed identifier {ident.value}')
        return ident.value

    def parse_number(self) -> int:
        """
        Parses a number
        """
        if self.debug:
            print('<DEBUG> Parser.parse_number(): Parsing number')
        num = self.lx.next()
        if num.type != TokenType.Number:
            raise SyntaxError('Expected number')
        if self.debug:
            print(f'<DEBUG> Parser.parse_number(): Parsed number {num.value}')
        return num.value

    def parse_procedure(self) -> Procedure:
        """
        Parses a procedure
        """
        if self.debug:
            print('<DEBUG> Parser.parse_procedure(): Parsing procedure')
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
        if self.debug:
            print('<DEBUG> Parser.parse_statement(): Parsing statement')
        if self.check(Token.keyword('begin')):
            return Statement(self.parse_begin_statement())
        elif self.check(Token.keyword('if')):
            return Statement(self.parse_if_statement())
        elif self.check(Token.keyword('while')):
            return Statement(self.parse_while_statement())
        elif self.check(Token.keyword('call')):
            return Statement(self.parse_call_statement())
        elif self.check(Token.op('?')):
            return Statement(self.parse_read_statement())
        elif self.check(Token.op('!')):
            return Statement(self.parse_write_statement())
        else:
            return Statement(self.parse_assignment_statement())

    def parse_begin_statement(self) -> Begin:
        """
        Parses a begin statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_begin_statement(): Parsing begin statement')
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
        if self.debug:
            print('<DEBUG> Parser.parse_if_statement(): Parsing if statement')
        cond = self.parse_condition()
        if not self.check(Token.keyword('then')):
            raise SyntaxError('Expected "then"')
        stmt = self.parse_statement()
        return If(cond, stmt)

    def parse_while_statement(self) -> While:
        """
        Parses a while statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_while_statement(): Parsing while statement')
        cond = self.parse_condition()
        if not self.check(Token.keyword('do')):
            raise SyntaxError('Expected "do"')
        stmt = self.parse_statement()
        return While(cond, stmt)

    def parse_condition(self) -> Condition:
        """
        Parses a condition
        """
        if self.debug:
            print('<DEBUG> Parser.parse_condition(): Parsing condition')
        if self.check(Token.keyword('odd')):
            return self.parse_odd_condition()
        else:
            return self.parse_comparison_condition()

    def parse_odd_condition(self) -> OddCondition:
        """
        Parses an odd statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_odd_condition(): Parsing odd condition')
        expr = self.parse_expression()
        return OddCondition(expr)

    def parse_comparison_condition(self) -> ComparisonCondition:
        """
        Parses a comparison
        """
        if self.debug:
            print('<DEBUG> Parser.parse_comparison_condition(): Parsing comparison condition')
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
        if self.debug:
            print('<DEBUG> Parser.parse_call_statement(): Parsing call statement')
        ident = self.parse_identifier()
        return Call(ident)

    def parse_read_statement(self) -> Read:
        """
        Parses a read statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_read_statement(): Parsing read statement')
        ident = self.parse_identifier()
        return Read(ident)

    def parse_write_statement(self) -> Write:
        """
        Parses a write statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_write_statement(): Parsing write statement')
        expr = self.parse_expression()
        return Write(expr)

    def parse_assignment_statement(self) -> Assignment:
        """
        Parses an assignment statement
        """
        if self.debug:
            print('<DEBUG> Parser.parse_assignment_statement(): Parsing assignment statement')
        ident = self.parse_identifier()
        if not self.check(Token.op(':=')):
            raise SyntaxError('Expected ":="')
        expr = self.parse_expression()
        return Assignment(ident, expr)

    def parse_expression(self) -> Expression:
        """
        Parses an expression
        """
        if self.debug:
            print('<DEBUG> Parser.parse_expression(): Parsing expression')
        prefix = None
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
        if self.debug:
            print('<DEBUG> Parser.parse_term(): Parsing term')
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
        if self.debug:
            print('<DEBUG> Parser.parse_factor(): Parsing factor')
        token = self.lx.peek()
        if token == Token.op('('):
            self.lx.next()
            expr = self.parse_expression()
            if not self.check(Token.op(')')):
                raise SyntaxError('Expected ")"')
            if self.debug:
                print('<DEBUG> Parser.parse_factor(): Parsed parenthesized expression')
            return Factor(expr)
        elif token.type == TokenType.Name:
            return Factor(self.parse_identifier())
        elif token.type == TokenType.Number:
            return Factor(self.parse_number())
        raise SyntaxError('Expected name or number')


def main():
    import sys
    if len(sys.argv) != 2:
        print('Usage: python3.11 src_parser.py <path-to-file>')
        return
    with open(sys.argv[1]) as f:
        src = f.read()
    parser = Parser(src, debug=True)
    print(parser.parse())


if __name__ == '__main__':
    main()
