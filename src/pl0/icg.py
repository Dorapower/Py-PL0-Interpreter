from enum import StrEnum, auto

from .ast_node import Program, Block, Const, Procedure, Statement, \
    Assignment, Call, If, While, Begin, Condition, Expression, Term, \
    Factor, Var, OddCondition, ComparisonCondition


class IROp(StrEnum):
    # to be improved in the future
    ADD = auto()  # +
    SUB = auto()  # -
    MUL = auto()  # *
    DIV = auto()  # /
    NEG = auto()  # unary -

    EQ = auto()  # ==
    NE = auto()  # !=

    LT = auto()  # <
    LE = auto()  # <=
    GT = auto()  # >
    GE = auto()  # >=
    ODD = auto()  # odd

    LOAD = auto()  # load from memory
    STORE = auto()  # store to memory
    LIT = auto()  # load literal

    CALL = auto()  # call procedure
    RET = auto()  # return from procedure
    JMP = auto()  # unconditional jump
    JPC = auto()  # jump if condition is true

    VAR = auto()  # variable
    CONST = auto()  # constant
    PROC = auto()  # procedure

    INPUT = auto()  # input
    OUTPUT = auto()  # output
    HALT = auto()  # halt


class IR:
    op: IROp
