import pytest
from typing import TypeAlias

from context import lexer as mod

Lexer: TypeAlias = mod.Lexer
Token: TypeAlias = mod.Token
TokenType: TypeAlias = mod.TokenType


@pytest.mark.parametrize('s, expected', [
    (' ', []),
    ('+', [Token(TokenType.Op, '+')]),
    ('if_0', [Token(TokenType.Name, 'if_0')]),
    ('if', [Token(TokenType.Keyword, 'if')]),
    ('var i, s;', [
        Token(TokenType.Keyword, 'var'),
        Token(TokenType.Name, 'i'),
        Token(TokenType.Op, ','),
        Token(TokenType.Name, 's'),
        Token(TokenType.Op, ';')
    ]),
])
def test_simple(s, expected):
    lex = Lexer(s)
    for e in expected:
        assert lex.next() == e
