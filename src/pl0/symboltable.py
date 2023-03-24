from dataclasses import dataclass
from enum import StrEnum, auto

from .ast_node import Procedure

class SymbolType(StrEnum):
    CONST = auto()
    VAR = auto()
    PROC = auto()


@dataclass
class Symbol:
    ident: str
    type: SymbolType
    value: int | Procedure | None

class SymbolTable:
    symbols: list[Symbol]

    def __init__(self):
        self.symbols = []

    def _register(self, symbol: Symbol):
        for s in self.symbols:
            if s.ident == symbol.ident:
                raise ValueError(f"Symbol {symbol.ident} already exists")
        self.symbols.append(symbol)

    def register_const(self, ident: str, value: int):
        self._register(Symbol(ident, SymbolType.CONST, value))

    def register_var(self, ident: str):
        self._register(Symbol(ident, SymbolType.VAR, None))

    def register_proc(self, ident: str, proc: Procedure):
        self._register(Symbol(ident, SymbolType.PROC, proc))

    def _retrieve(self, ident: str) -> Symbol:
        for symbol in self.symbols:
            if symbol.ident == ident:
                if symbol.value is None:
                    raise ValueError(f"Symbol {ident} has not been initialized")
                return symbol
        raise ValueError(f"Symbol {ident} has not been declared")

    def retrieve_const(self, ident: str) -> Symbol:
        symbol = self._retrieve(ident)
        if symbol.type != SymbolType.CONST:
            raise ValueError(f"Symbol {ident} is not a constant")
        return symbol

    def retrieve_var(self, ident: str) -> Symbol:
        symbol = self._retrieve(ident)
        if symbol.type != SymbolType.VAR:
            raise ValueError(f"Symbol {ident} is not a variable")
        return symbol

    def retrieve_proc(self, ident: str) -> Symbol:
        symbol = self._retrieve(ident)
        if symbol.type != SymbolType.PROC:
            raise ValueError(f"Symbol {ident} is not a procedure")
        return symbol

    def __str__(self):
        return f"SymbolTable({self.symbols})"