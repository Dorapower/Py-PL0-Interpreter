from typing import TypeAlias

from src.pl0 import parser as mod

Parser: TypeAlias = mod.Parser


def test_simple():
    p = Parser(mod.Lexer('a := - 1 + 2.'))
    assert p.parse() == mod.Program(mod.Block(consts=[], vars=[], procs=[], stmt=mod.Statement(
        mod.Assignment('a', mod.Expression(prefix='-', terms=[
            mod.Term(factors=[mod.Factor(value=1)], ops=[]),
            mod.Term(factors=[mod.Factor(value=2)], ops=[]),
        ], ops=['+']))
    )))
