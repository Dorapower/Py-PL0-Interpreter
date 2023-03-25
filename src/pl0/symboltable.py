from dataclasses import dataclass
from enum import StrEnum, auto

from ast_node import Procedure


class SymbolType(StrEnum):
    CONST = auto()
    VAR = auto()
    PROC = auto()


@dataclass
class Symbol:
    ident: str
    type: SymbolType
    value: int | Procedure | None

    def assign(self, value: int):
        if self.type != SymbolType.VAR:
            raise TypeError(f"Cannot assign to {self.ident} as it is not a variable")
        self.value = value


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

    def register_proc(self, ident: str, proc: Procedure | int):
        """
        Registers a procedure in the symbol table
        :param ident: The identifier of the procedure
        :param proc: The procedure itself, or the address of the procedure
        :raises ValueError: If the procedure already exists
        """
        self._register(Symbol(ident, SymbolType.PROC, proc))

    def retrieve(self, ident: str) -> Symbol | None:
        """
        Retrieves a symbol from the symbol table, or None if it doesn't exist
        """
        for symbol in self.symbols:
            if symbol.ident == ident:
                return symbol
        return None

    def __str__(self):
        return f"SymbolTable({self.symbols})"
