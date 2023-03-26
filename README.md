# Py-PL0-Parser
A PL/0 Parser implemented in Python

## Grammar
The grammar is based on wikipedia's [PL/0](https://en.wikipedia.org/wiki/PL/0) page.
```ebnf
program = block "." ;

block = [ "const" ident "=" number {"," ident "=" number} ";"]
        [ "var" ident {"," ident} ";"]
        { "procedure" ident ";" block ";" } statement ;

statement = [ ident ":=" expression | "call" ident 
              | "?" ident | "!" expression 
              | "begin" statement {";" statement } "end" 
              | "if" condition "then" statement 
              | "while" condition "do" statement ];

condition = "odd" expression |
            expression ("="|"#"|"<"|"<="|">"|">=") expression ;

expression = [ "+"|"-"] term { ("+"|"-") term};

term = factor {("*"|"/") factor};

factor = ident | number | "(" expression ")";
```
### Keywords
**Note**: Keywords are case-insensitive in this implementation.
- `const`: declares constants
- `var`: declares variables
- `procedure`: declares a procedure
- `call`: calls a procedure
- `begin`: composite statements
- `end`: composite statements ends
- `if`: conditional statement condition
- `then`: conditional statement body
- `while`: loop statement condition
- `do`: loop statement body
- `odd`: condition operator, returns true if the expression is odd

### Operators
- `+`, `-`: unary operators
- `+`, `-`, `*`, `/`: arithmetic operators
- `=`, `#`, `<`, `<=`, `>`, `>=`: comparison operators
- `:=`: assignment operator
- `?`: input operator
- `!`: output operator
- `;`: statement separator
- `,`: variable separator
- `(`, `)`: parenthesis
- `.`: program end

## Features
- [x] Lexer: converts source code into tokens
- [x] Parser: converts tokens into an AST
- [x] ASTInterpreter: interprets the AST
- [x] IR Generator: generates an IR from the AST
- [x] IR Interpreter: interprets the IR

## Test
To test a certain program, either use pytest to run the test file or run the following command:
```bash
python3.11 <path-to-program> < <path-to-input>
```
and the output will be printed to the console.