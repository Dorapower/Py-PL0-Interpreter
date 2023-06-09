from dataclasses import dataclass
from enum import StrEnum, auto

import ast_node


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
    JPF = auto()  # jump if condition is false

    VAR = auto()  # define variable
    CONST = auto()  # define constant
    PROC = auto()  # define procedure

    INPUT = auto()  # input
    OUTPUT = auto()  # output
    HALT = auto()  # halt


@dataclass
class IR:
    op: IROp
    opr: int | str | None = None  # could be a number, a variable name, or a target index in the IR list
    # The top value in the stack is used as the value for declaration, so value member is not needed

    def __str__(self):
        if self.opr is None:
            return f"{self.op}"
        else:
            return f"{self.op:<6}{self.opr}"


class ICG:
    """
    Intermediate code generator, converts an AST to intermediate code

    The intermediate code is a list of IR objects
    """
    ast: ast_node.Program
    buf: list[IR]  # buffer for intermediate code
    debug: bool

    def __init__(self, ast: ast_node.Program, /, *, debug=False):
        self.ast = ast
        self.buf = []
        self.debug = debug

    def generate(self) -> list[IR]:
        """
        Generates intermediate code from the AST
        """
        self.generate_program(self.ast)
        return self.buf

    def generate_program(self, node: ast_node.Program):
        if self.debug:
            print("<DEBUG> ICG.generate_program")
        self.generate_block(node.block)
        self.buf.append(IR(IROp.HALT))

    def generate_block(self, node: ast_node.Block):
        if self.debug:
            print("<DEBUG> ICG.generate_block")
        self.generate_const(node.consts)
        self.generate_var(node.vars)
        self.generate_proc(node.procs)
        self.generate_statement(node.stmt)

    def generate_const(self, consts: list[ast_node.Const]):
        if self.debug:
            print("<DEBUG> ICG.generate_const")
        for const in consts:
            # const definition will use the top value in the stack
            self.buf.append(IR(IROp.LIT, const.value))
            self.buf.append(IR(IROp.CONST, const.ident))

    def generate_var(self, variables: list[ast_node.Var]):
        if self.debug:
            print("<DEBUG> ICG.generate_var")
        for var in variables:
            self.buf.append(IR(IROp.VAR, var.ident))

    def generate_proc(self, procs: list[ast_node.Procedure]):
        if self.debug:
            print("<DEBUG> ICG.generate_proc")
        for proc in procs:
            self.buf.append(IR(IROp.PROC, proc.ident))
            self.generate_block(proc.block)
            self.buf.append(IR(IROp.RET))

    def generate_statement(self, stmt: ast_node.Statement):
        if self.debug:
            print("<DEBUG> ICG.generate_statement")
        stmt = stmt.stmt  # Maybe change in the future
        if isinstance(stmt, ast_node.Assignment):
            self.generate_assign(stmt)
        elif isinstance(stmt, ast_node.Call):
            self.generate_call(stmt)
        elif isinstance(stmt, ast_node.If):
            self.generate_if(stmt)
        elif isinstance(stmt, ast_node.While):
            self.generate_while(stmt)
        elif isinstance(stmt, ast_node.Begin):
            self.generate_begin(stmt)
        elif isinstance(stmt, ast_node.Read):
            self.generate_read(stmt)
        elif isinstance(stmt, ast_node.Write):
            self.generate_write(stmt)
        else:
            raise NotImplementedError(f"Statement {stmt} not implemented")

    def generate_assign(self, node: ast_node.Assignment):
        if self.debug:
            print("<DEBUG> ICG.generate_assign")
        self.generate_expression(node.expr)
        self.buf.append(IR(IROp.STORE, node.ident))

    def generate_call(self, node: ast_node.Call):
        if self.debug:
            print("<DEBUG> ICG.generate_call")
        self.buf.append(IR(IROp.CALL, node.ident))

    def generate_if(self, node: ast_node.If):
        if self.debug:
            print("<DEBUG> ICG.generate_if")
        self.generate_condition(node.cond)
        # jump to the end of the block if the condition is false
        jpf_index = len(self.buf)
        self.buf.append(IR(IROp.JPF))
        self.generate_statement(node.stmt)
        self.buf[jpf_index].opr = len(self.buf)

    def generate_while(self, node: ast_node.While):
        if self.debug:
            print("<DEBUG> ICG.generate_while")
        # jump to here after the body
        cond_index = len(self.buf)
        self.generate_condition(node.cond)
        # jump to the end of the block if the condition is false
        jpf_index = len(self.buf)
        self.buf.append(IR(IROp.JPF))
        self.generate_statement(node.stmt)
        self.buf.append(IR(IROp.JMP, cond_index))
        self.buf[jpf_index].opr = len(self.buf)

    def generate_begin(self, node: ast_node.Begin):
        if self.debug:
            print("<DEBUG> ICG.generate_begin")
        for stmt in node.body:
            self.generate_statement(stmt)

    def generate_read(self, node: ast_node.Read):
        if self.debug:
            print("<DEBUG> ICG.generate_read")
        self.buf.append(IR(IROp.INPUT))
        self.buf.append(IR(IROp.STORE, node.ident))

    def generate_write(self, node: ast_node.Write):
        if self.debug:
            print("<DEBUG> ICG.generate_write")
        self.generate_expression(node.expr)
        self.buf.append(IR(IROp.OUTPUT))

    def generate_condition(self, node: ast_node.Condition):
        if self.debug:
            print("<DEBUG> ICG.generate_condition")
        if isinstance(node, ast_node.OddCondition):
            self.generate_expression(node.expr)
            self.buf.append(IR(IROp.ODD))
        elif isinstance(node, ast_node.ComparisonCondition):
            self.generate_comparison(node)
        else:
            raise ValueError(f"Invalid condition {node}")

    def generate_comparison(self, node: ast_node.ComparisonCondition):
        if self.debug:
            print("<DEBUG> ICG.generate_comparison")
        self.generate_expression(node.lhs)
        self.generate_expression(node.rhs)
        if node.op == "==":
            self.buf.append(IR(IROp.EQ))
        elif node.op == "#":
            self.buf.append(IR(IROp.NE))
        elif node.op == "<":
            self.buf.append(IR(IROp.LT))
        elif node.op == "<=":
            self.buf.append(IR(IROp.LE))
        elif node.op == ">":
            self.buf.append(IR(IROp.GT))
        elif node.op == ">=":
            self.buf.append(IR(IROp.GE))
        else:
            raise ValueError(f"Invalid comparison operator {node.op}")

    def generate_expression(self, node: ast_node.Expression):
        if self.debug:
            print("<DEBUG> ICG.generate_expression")
        assert len(node.terms) == len(node.ops) + 1
        self.generate_term(node.terms[0])
        match node.prefix:
            case '+' | None:
                pass
            case '-':
                self.buf.append(IR(IROp.NEG))
            case _:
                raise ValueError(f"Invalid prefix {node.prefix}")
        for term, op in zip(node.terms[1:], node.ops):
            self.generate_term(term)
            match op:
                case '+':
                    self.buf.append(IR(IROp.ADD))
                case '-':
                    self.buf.append(IR(IROp.SUB))
                case _:
                    raise ValueError(f"Invalid operator {op}")

    def generate_term(self, node: ast_node.Term):
        if self.debug:
            print("<DEBUG> ICG.generate_term")
        assert len(node.factors) == len(node.ops) + 1
        self.generate_factor(node.factors[0])
        for factor, op in zip(node.factors[1:], node.ops):
            self.generate_factor(factor)
            match op:
                case '*':
                    self.buf.append(IR(IROp.MUL))
                case '/':
                    self.buf.append(IR(IROp.DIV))
                case _:
                    raise ValueError(f"Invalid operator {op}")

    def generate_factor(self, node: ast_node.Factor):
        if self.debug:
            print("<DEBUG> ICG.generate_factor")
        if isinstance(node.value, int):
            self.buf.append(IR(IROp.LIT, node.value))
        elif isinstance(node.value, str):
            self.buf.append(IR(IROp.LOAD, node.value))
        elif isinstance(node.value, ast_node.Expression):
            self.generate_expression(node.value)

    def __str__(self) -> str:
        idx_width = len(str(len(self.buf)))
        return 'ICG:\n' + '\n'.join(f'{i:{idx_width}d}: {elem}' for i, elem in enumerate(self.buf))


def main():
    import sys
    from src_parser import Parser

    if len(sys.argv) != 2:
        print("Usage: python3.11 src_intermediate.py <path-to-file>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    parser = Parser(src)
    ast = parser.parse()

    icg = ICG(ast, debug=True)
    ir = icg.generate()
    for idx, ic in enumerate(ir):
        print(f'{idx:2d}: {ic}')


if __name__ == "__main__":
    main()

