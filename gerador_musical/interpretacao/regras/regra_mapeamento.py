"""Abstrações das regras de mapeamento."""

from abc import ABC, abstractmethod

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.tokens import TipoToken, Token


class RegraMapeamento(ABC):
    """Uma linha da tabela de mapeamento: "se o token for X, faça Y".

    Classe abstrata: toda regra concreta implementa aceita() e aplicar().
    """

    @abstractmethod
    def aceita(self, token: Token) -> bool:
        """Diz se esta regra trata este token.

        Args:
            token: token a examinar.

        Returns:
            True se a regra deve ser aplicada ao token.
        """

    @abstractmethod
    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Executa o efeito da regra (criar evento, mudar parâmetro, etc.).

        Args:
            token: token que a regra aceitou.
            contexto: estado da linha que está sendo interpretada.
        """


class RegraPorCaractere(RegraMapeamento, ABC):
    """Base para regras disparadas por um conjunto fixo de caracteres.

    Já implementa aceita(), que seria igual em todas as regras de comando;
    as subclasses só implementam aplicar().

    Attributes:
        caracteres: conjunto de caracteres que disparam a regra.
    """

    def __init__(self, caracteres: str) -> None:
        """Guarda os caracteres que disparam a regra.

        Args:
            caracteres: string com todos os caracteres aceitos (ex.: "abcdefgh").
        """
        self.caracteres: frozenset[str] = frozenset(caracteres)

    def aceita(self, token: Token) -> bool:
        """Diz se o token é CARACTERE e está em self.caracteres.

        Args:
            token: token a examinar.
        """
        return token.tipo is TipoToken.CARACTERE and token.lexema in self.caracteres
