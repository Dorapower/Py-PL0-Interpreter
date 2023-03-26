import ast_node
import symboltable


class ASTInterpreter:
    """
    Interprets an AST
    """
    ast: ast_node.Program
    stack: list[symboltable.SymbolTable]
    # The reason I use a list is when an identifier is declared in a local scope,
    # it should be removed when the scope is exited
    debug: bool

    def __init__(self, ast: ast_node.Program, /, *, debug: bool = False):
        self.ast = ast
        self.stack: list[symboltable.SymbolTable] = []
        self.stack.append(symboltable.SymbolTable())
        self.debug = debug

    @property
    def current_table(self) -> symboltable.SymbolTable:
        return self.stack[-1]

    def retrieve(self, ident: str) -> symboltable.Symbol | None:
        """
        Retrieves a symbol from the symbol table, or None if it doesn't exist
        """
        for table in reversed(self.stack):
            symbol = table.retrieve(ident)
            if symbol is not None:
                return symbol
        return None

    def interpret(self):
        """
        Interprets the AST
        """
        self.interpret_program(self.ast)

    def interpret_program(self, program: ast_node.Program):
        """
        Interprets a program
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_program')
        self.interpret_block(program.block)

    def interpret_block(self, block: ast_node.Block):
        """
        Interprets a block
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_block')
        self.stack.append(symboltable.SymbolTable())
        for const in block.consts:
            self.interpret_const(const)
        for var in block.vars:
            self.interpret_var(var)
        for proc in block.procs:
            self.interpret_procedure(proc)
        self.interpret_statement(block.stmt)
        self.stack.pop()

    def interpret_const(self, const: ast_node.Const):
        """
        Interprets a constant
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_const')
        self.current_table.register_const(const.ident, const.value)

    def interpret_var(self, var: ast_node.Var):
        """
        Interprets a variable
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_var')
        self.current_table.register_var(var.ident)

    def interpret_procedure(self, proc: ast_node.Procedure):
        """
        Interprets a procedure
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_procedure')
        self.current_table.register_proc(proc.ident, proc)

    def interpret_statement(self, stmt: ast_node.Statement):
        """
        Interprets a statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_statement')
        if isinstance(stmt.stmt, ast_node.Assignment):
            self.interpret_assignment(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.Call):
            self.interpret_call(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.If):
            self.interpret_if(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.While):
            self.interpret_while(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.Begin):
            self.interpret_begin(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.Read):
            self.interpret_read(stmt.stmt)
        elif isinstance(stmt.stmt, ast_node.Write):
            self.interpret_write(stmt.stmt)
        else:
            raise TypeError('Unknown statement type')

    def interpret_assignment(self, assignment: ast_node.Assignment):
        """
        Interprets an assignment
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_assignment')
        ident = self.retrieve(assignment.ident)
        if ident is None:
            raise NameError(f'Cannot assign to {assignment.ident} as it is not defined')
        if ident.type != symboltable.SymbolType.VAR:
            raise TypeError(f'Cannot assign to {assignment.ident} as it is not a variable')
        ident.assign(self.interpret_expression(assignment.expr))
        if self.debug:
            print(f'<DEBUG> Assigned {assignment.ident} to {ident.value}')

    def interpret_call(self, call: ast_node.Call):
        """
        Interprets a call
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_call')
        result = None
        # Search for the procedure in the stack
        for table in reversed(self.stack):
            result = table.retrieve(call.ident)
            if result is not None:
                break
        if result.type == symboltable.SymbolType.PROC:
            return self.interpret_block(result.value.block)
        raise TypeError(f'Cannot call {call.ident} as it is not a procedure')

    def interpret_if(self, if_stmt: ast_node.If):
        """
        Interprets an if statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_if')
        if self.interpret_condition(if_stmt.cond):
            self.interpret_statement(if_stmt.stmt)

    def interpret_while(self, while_stmt: ast_node.While):
        """
        Interprets a while statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_while')
        while self.interpret_condition(while_stmt.cond):
            self.interpret_statement(while_stmt.stmt)

    def interpret_begin(self, begin_stmt: ast_node.Begin):
        """
        Interprets a begin statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_begin')
        for stmt in begin_stmt.body:
            self.interpret_statement(stmt)

    def interpret_read(self, read_stmt: ast_node.Read):
        """
        Interprets a read statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_read')
        ident = self.retrieve(read_stmt.ident)
        if ident is None:
            raise NameError(f'Cannot assign to {read_stmt.ident} as it is not defined')
        if ident.type != symboltable.SymbolType.VAR:
            raise TypeError(f'Cannot assign to {read_stmt.ident} as it is not a variable')
        ident.assign(int(input(f'Enter a value for {read_stmt.ident}: ')))
        if self.debug:
            print(f'Read {read_stmt.ident} to {ident.value}')

    def interpret_write(self, write_stmt: ast_node.Write):
        """
        Interprets a write statement
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_write')
        print(self.interpret_expression(write_stmt.expr))

    def interpret_condition(self, cond: ast_node.Condition) -> bool:
        """
        Interprets a condition
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_condition')
        if isinstance(cond, ast_node.OddCondition):
            return self.interpret_expression(cond.expr) % 2 == 1
        elif isinstance(cond, ast_node.ComparisonCondition):
            return self.interpret_comparison(cond)

    def interpret_comparison(self, comp: ast_node.ComparisonCondition) -> bool:
        """
        Interprets a comparison
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_comparison')
        lhs = self.interpret_expression(comp.lhs)
        rhs = self.interpret_expression(comp.rhs)
        match comp.op:
            case '=':
                return lhs == rhs
            case '#':
                return lhs != rhs
            case '<':
                return lhs < rhs
            case '<=':
                return lhs <= rhs
            case '>':
                return lhs > rhs
            case '>=':
                return lhs >= rhs
            case _:
                raise TypeError('Unknown comparison operator')

    def interpret_expression(self, expr: ast_node.Expression) -> int:
        """
        Interprets an expression
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_expression')
        if expr.prefix == '-':
            result = -self.interpret_term(expr.terms[0])
        else:
            result = self.interpret_term(expr.terms[0])
        for term, op in zip(expr.terms[1:], expr.ops):
            if op == '+':
                result += self.interpret_term(term)
            else:
                result -= self.interpret_term(term)
        return result

    def interpret_term(self, term: ast_node.Term) -> int:
        """
        Interprets a term
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_term')
        result = self.interpret_factor(term.factors[0])
        for factor, op in zip(term.factors[1:], term.ops):
            if op == '*':
                result *= self.interpret_factor(factor)
            else:
                result //= self.interpret_factor(factor)
        return result

    def interpret_factor(self, factor: ast_node.Factor) -> int:
        """
        Interprets a factor
        Note: parent scope will be searched for identifiers
        """
        if self.debug:
            print('<DEBUG> ASTInterpreter.interpret_factor')
        if isinstance(factor.value, int):
            return factor.value
        elif isinstance(factor.value, ast_node.Expression):
            return self.interpret_expression(factor.value)
        elif isinstance(factor.value, str):
            result = None
            for table in reversed(self.stack):
                result = table.retrieve(factor.value)
                if result is not None:  # identifier found
                    break
            return result.value


def main():
    import sys
    from src_parser import Parser

    if len(sys.argv) < 2:
        print('Usage: python3.11 ast_interpreter.py <path-to-file>')
        return
    src = open(sys.argv[1]).read()
    ast = Parser(src).parse()
    interpreter = ASTInterpreter(ast, debug=True)
    interpreter.interpret()


if __name__ == '__main__':
    main()
