"""NOVA (Fase 2): unidade léxica de uma linha.

Na Fase 1 cada caractere era uma unidade. Na Fase 2 algumas unidades têm
vários caracteres ("C#:3", "[4]"), por isso existe o Token.
"""

from dataclasses import dataclass
from enum import Enum, auto

from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical


class TipoToken(Enum):
    """Tipo de token.

    ATRASO: "[n]" no início da linha.
    NOTA: letra A–G + acidente opcional + ":n" opcional.
    CARACTERE: qualquer outro caractere isolado (comando, pausa, etc.).
    """

    ATRASO = auto()     # "[n]" no início da linha
    NOTA = auto()       # letra A–G + acidente opcional + ":n" opcional
    CARACTERE = auto()  # qualquer outro caractere isolado (comando, pausa, etc.)


@dataclass(frozen=True)
class Token:
    """Pedaço do texto já reconhecido pelo Tokenizador. Objeto imutável.

    Attributes:
        tipo: ATRASO, NOTA ou CARACTERE.
        lexema: trecho original do texto, ex.: "C#:3".
        coluna: posição na linha (para mensagens e testes).
        nota: a nota, só em tokens NOTA.
        duracao: a duração de ":n", só em tokens NOTA (None se não houver).
        valor: o número do atraso, só em tokens ATRASO.
    """

    tipo: TipoToken
    lexema: str                  # trecho original do texto, ex.: "C#:3"
    coluna: int                  # posição na linha (para mensagens e testes)
    nota: NotaMusical | None = None
    duracao: Duracao | None = None
    valor: int | None = None     # usado pelo ATRASO

    def eh_nota(self) -> bool:
        """Diz se o token é uma nota."""
        return self.tipo is TipoToken.NOTA

    def eh_caractere(self, caractere: str) -> bool:
        """Diz se o token é um CARACTERE igual ao informado.

        Args:
            caractere: caractere a comparar com o lexema.
        """
        return self.tipo is TipoToken.CARACTERE and self.lexema == caractere
