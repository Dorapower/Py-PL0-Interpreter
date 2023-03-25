import ast_node, symboltable


class ASTInterpreter:
    """
    Interprets an AST
    """
    def __init__(self, ast: ast_node.Program, debug: bool = False):
        self.ast = ast
        self.stack: list[symboltable.SymbolTable] = []
        self.stack.append(symboltable.SymbolTable())
        self.debug = debug

    @property
    def current_table(self) -> symboltable.SymbolTable:
        return self.stack[-1]

    def interpret(self):
        """
        Interprets the AST
        """
        self.interpret_program(self.ast)

    def interpret_program(self, program: ast_node.Program):
        """
        Interprets a program
        """
        self.interpret_block(program.block)

    def interpret_block(self, block: ast_node.Block):
        """
        Interprets a block
        """
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
        self.current_table.register_const(const.ident, const.value)

    def interpret_var(self, var: ast_node.Var):
        """
        Interprets a variable
        """
        self.current_table.register_var(var.ident)

    def interpret_procedure(self, proc: ast_node.Procedure):
        """
        Interprets a procedure
        """
        self.current_table.register_proc(proc.ident, proc)

    def interpret_statement(self, stmt: ast_node.Statement):
        """
        Interprets a statement
        """
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
        else:
            raise TypeError('Unknown statement type')

    def interpret_assignment(self, assignment: ast_node.Assignment):
        """
        Interprets an assignment
        """
        self.current_table.retrieve_var(assignment.ident).value = self.interpret_expression(assignment.expr)
        if self.debug:
            print(f'Assigned {assignment.ident} to {self.current_table.retrieve_var(assignment.ident).value}')

    def interpret_call(self, call: ast_node.Call):
        """
        Interprets a call
        """
        proc = self.current_table.retrieve_proc(call.ident).value
        self.interpret_block(proc.body)

    def interpret_if(self, if_stmt: ast_node.If):
        """
        Interprets an if statement
        """
        if self.interpret_condition(if_stmt.cond):
            self.interpret_statement(if_stmt.stmt)

    def interpret_while(self, while_stmt: ast_node.While):
        """
        Interprets a while statement
        """
        while self.interpret_condition(while_stmt.cond):
            self.interpret_statement(while_stmt.stmt)

    def interpret_begin(self, begin_stmt: ast_node.Begin):
        """
        Interprets a begin statement
        """
        for stmt in begin_stmt.body:
            self.interpret_statement(stmt)

    def interpret_condition(self, cond: ast_node.Condition) -> bool:
        """
        Interprets a condition
        """
        if isinstance(cond, ast_node.OddCondition):
            return self.interpret_expression(cond.expr) % 2 == 1
        elif isinstance(cond, ast_node.ComparisonCondition):
            return self.interpret_comparison(cond)

    def interpret_comparison(self, comp: ast_node.ComparisonCondition) -> bool:
        """
        Interprets a comparison
        """
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
        """
        if isinstance(factor.value, int):
            return factor.value
        elif isinstance(factor.value, str):
            return self.current_table.retrieve_var(factor.value).value
        elif isinstance(factor.value, ast_node.Expression):
            return self.interpret_expression(factor.value)


def main():
    import sys
    from src_parser import Parser

    print('Enter a program:')
    program = sys.stdin.read()
    ast = Parser(program).parse()
    interpreter = ASTInterpreter(ast, debug=True)
    interpreter.interpret()


if __name__ == '__main__':
    main()
