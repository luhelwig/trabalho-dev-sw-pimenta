"""NOVA (Fase 2): unidade léxica de uma linha.

Na Fase 1 cada caractere era uma unidade. Na Fase 2 algumas unidades têm
vários caracteres ("C#:3", "[4]"), por isso existe o Token.
"""

from dataclasses import dataclass
from enum import Enum, auto

from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical


class TipoToken(Enum):
    ATRASO = auto()     # "[n]" no início da linha
    NOTA = auto()       # letra A–G + acidente opcional + ":n" opcional
    CARACTERE = auto()  # qualquer outro caractere isolado (comando, pausa, etc.)


@dataclass(frozen=True)
class Token:
    tipo: TipoToken
    lexema: str                  # trecho original do texto, ex.: "C#:3"
    coluna: int                  # posição na linha (para mensagens e testes)
    nota: NotaMusical | None = None
    duracao: Duracao | None = None
    valor: int | None = None     # usado pelo ATRASO

    def eh_nota(self) -> bool:
        return self.tipo is TipoToken.NOTA

    def eh_caractere(self, caractere: str) -> bool:
        """True se for CARACTERE e o lexema for exatamente `caractere`."""
        return self.tipo is TipoToken.CARACTERE and self.lexema == caractere
