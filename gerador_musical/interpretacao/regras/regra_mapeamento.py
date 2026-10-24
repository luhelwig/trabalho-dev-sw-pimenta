"""Abstrações das regras de mapeamento."""

from abc import ABC, abstractmethod

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.tokens import TipoToken, Token


class RegraMapeamento(ABC):
    """Uma linha da tabela de mapeamento: "se o token for X, faça Y"."""

    @abstractmethod
    def aceita(self, token: Token) -> bool:
        """True se esta regra trata este token."""

    @abstractmethod
    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Executa o efeito da regra (criar evento, mudar parâmetro, etc.)."""


class RegraPorCaractere(RegraMapeamento, ABC):
    """Base para regras disparadas por um conjunto fixo de caracteres.

    Evita repetir o mesmo aceita() em todas as regras de comando.
    Subclasses só implementam aplicar().
    """

    def __init__(self, caracteres: str) -> None:
        self.caracteres: frozenset[str] = frozenset(caracteres)

    def aceita(self, token: Token) -> bool:
        """True se o token é CARACTERE e está em self.caracteres."""
        return token.tipo is TipoToken.CARACTERE and token.lexema in self.caracteres
