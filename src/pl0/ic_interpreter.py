import icg
import symboltable

IROp = icg.IROp


class ICInterpreter:
    ic: list[icg.IR]  # intermediate code
    pc: int  # program counter
    stack: list[int | bool]  # contains values
    env: list[symboltable.SymbolTable]  # contains variables
    debug: bool

    def __init__(self, ic, /, *, debug=False):
        self.ic = ic
        self.pc = 0
        self.stack = []
        self.env = [symboltable.SymbolTable()]  # global scope
        self.debug = debug

    @property
    def current_ir(self) -> icg.IR:
        return self.ic[self.pc]

    @property
    def current_env(self) -> symboltable.SymbolTable:
        return self.env[-1]

    def retrieve(self, ident: str) -> symboltable.Symbol:
        for env in reversed(self.env):
            if (symbol := env.retrieve(ident)) is not None:
                return symbol
        raise KeyError(f"Identifier {ident!r} not found")

    def _search_ret(self) -> None:
        """
        Search for the corresponding RET instruction and set the pc to it.
        Should be called immediately after meeting a PROC declaration
        """
        proc_count = 1
        while proc_count > 0:
            ir = self.current_ir
            if ir.op == IROp.PROC:
                proc_count += 1
            elif ir.op == IROp.RET:
                proc_count -= 1
            self.pc += 1

    def run(self) -> None:
        while True:
            ir = self.current_ir
            self.pc += 1  # pc always points to the next instruction
            if self.debug:
                print(f"<DEBUG> {ir=}, {self.stack=}, {self.env=}")
            match ir.op:
                case IROp.ADD:
                    self.stack.append(self.stack.pop() + self.stack.pop())
                case IROp.SUB:
                    self.stack.append(-self.stack.pop() + self.stack.pop())
                case IROp.MUL:
                    self.stack.append(self.stack.pop() * self.stack.pop())
                case IROp.DIV:
                    divisor, dividend = self.stack.pop(), self.stack.pop()
                    if divisor == 0:
                        raise ZeroDivisionError("Divisor cannot be zero")
                    self.stack.append(dividend // divisor)
                case IROp.NEG:
                    self.stack.append(-self.stack.pop())
                case IROp.EQ:
                    self.stack.append(self.stack.pop() == self.stack.pop())
                case IROp.NE:
                    self.stack.append(self.stack.pop() != self.stack.pop())
                case IROp.LT:
                    self.stack.append(self.stack.pop() > self.stack.pop())
                case IROp.LE:
                    self.stack.append(self.stack.pop() >= self.stack.pop())
                case IROp.GT:
                    self.stack.append(self.stack.pop() < self.stack.pop())
                case IROp.GE:
                    self.stack.append(self.stack.pop() <= self.stack.pop())
                case IROp.ODD:
                    self.stack.append(self.stack.pop() % 2)
                case IROp.LOAD:
                    ident = self.retrieve(ir.opr)
                    if ident is None:
                        raise Exception(f"Ident {ir.opr} is not defined")
                    if ident.value is None:
                        raise Exception(f"Ident {ir.opr} is not initialized")
                    if ident.type == symboltable.SymbolType.PROC:
                        raise Exception(f"Trying to load a procedure {ir.opr}")
                    self.stack.append(ident.value)
                case IROp.STORE:
                    ident = self.retrieve(ir.opr)
                    if ident is None:
                        raise Exception(f"Ident {ir.opr} is not defined")
                    if ident.type != symboltable.SymbolType.VAR:
                        raise Exception(f"Ident {ir.opr} is not a variable")
                    ident.value = self.stack.pop()
                    if self.debug:
                        print(f"<DEBUG> Assign {ir.opr} to {ident.value}")
                case IROp.LIT:
                    self.stack.append(ir.opr)
                case IROp.CALL:
                    ident = self.retrieve(ir.opr)
                    if ident.type != symboltable.SymbolType.PROC:
                        raise Exception(f"Trying to call a non-procedure {ir.opr}")
                    self.stack.append(self.pc)
                    self.env.append(symboltable.SymbolTable())
                    self.pc = ident.value
                case IROp.RET:
                    self.env.pop()
                    self.pc = self.stack.pop()
                case IROp.JMP:
                    self.pc = ir.opr
                case IROp.JPF:
                    if not self.stack.pop():
                        self.pc = ir.opr
                case IROp.VAR:
                    self.current_env.register_var(ir.opr)
                case IROp.CONST:
                    self.current_env.register_const(ir.opr, self.stack.pop())
                case IROp.PROC:
                    self.current_env.register_proc(ir.opr, self.pc)
                    # when declaring a procedure, the following IRs (until the RET corresponding) are the procedure body
                    # , and we need to skip them
                    self._search_ret()
                case IROp.INPUT:
                    self.stack.append(int(input()))
                case IROp.OUTPUT:
                    print(self.stack.pop())
                case IROp.HALT:
                    break


def main():
    import sys

    import src_parser

    if len(sys.argv) < 2:
        print("Usage: python3.11 ic_interpreter.py <path-to-file>")
        return
    with open(sys.argv[1], "r") as f:
        src = f.read()
    parser = src_parser.Parser(src)
    ast = parser.parse()

    generator = icg.ICG(ast)
    ic = generator.generate()

    vm = ICInterpreter(ic, debug=True)
    vm.run()


if __name__ == "__main__":
    main()
