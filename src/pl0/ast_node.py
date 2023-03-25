from __future__ import annotations

from abc import ABC
from dataclasses import dataclass


class ASTNode(ABC):
    """
    Represents a node in the AST
    """
    pass


@dataclass(frozen=True)
class Factor(ASTNode):
    """
    Represents a factor in a term
    """
    value: int | str | Expression


@dataclass(frozen=True)
class Term(ASTNode):
    """
    Represents a term in an expression
    """
    factors: list[Factor]
    ops: list[str]


@dataclass(frozen=True)
class Expression(ASTNode):
    """
    Represents an expression
    """
    prefix: str | None
    terms: list[Term]
    ops: list[str]


@dataclass(frozen=True)
class Const(ASTNode):
    """
    Represents a constant declaration
    """
    ident: str
    value: int


@dataclass(frozen=True)
class Var(ASTNode):
    """
    Represents a variable declaration
    """
    ident: str


@dataclass(frozen=True)
class Assignment(ASTNode):
    """
    Represents an assignment statement
    """
    ident: str
    expr: Expression


@dataclass(frozen=True)
class Call(ASTNode):
    """
    Represents a call statement
    """
    ident: str


class Condition(ASTNode):
    """
    Represents a condition
    """
    pass


@dataclass(frozen=True)
class OddCondition(Condition):
    """
    Represents an odd statement
    """
    expr: Expression


@dataclass(frozen=True)
class ComparisonCondition(Condition):
    """
    Represents a comparison condition
    """
    op: str
    lhs: Expression
    rhs: Expression


@dataclass(frozen=True)
class If(ASTNode):
    """
    Represents an if statement
    """
    cond: Condition
    stmt: Statement


@dataclass(frozen=True)
class While(ASTNode):
    """
    Represents a while statement
    """
    cond: Condition
    stmt: Statement


@dataclass(frozen=True)
class Begin(ASTNode):
    """
    Represents a begin statement
    """
    body: list[Statement]


# TODO: Add support for communication primitives
@dataclass(frozen=True)
class Statement(ASTNode):
    """
    Represents a statement
    """
    stmt: Assignment | Call | If | While | Begin


@dataclass(frozen=True)
class Block(ASTNode):
    """
    Represents a block
    """
    consts: list[Const]
    vars: list[Var]
    procs: list[Procedure]
    stmt: Statement


@dataclass(frozen=True)
class Procedure(ASTNode):
    """
    Represents a procedure
    """
    ident: str
    block: Block


@dataclass(frozen=True)
class Program(ASTNode):
    """
    Represents a program
    """
    block: Block
