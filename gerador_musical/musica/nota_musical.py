"""NOVA (Fase 2, Mudança 4): nota com acidente (sustenido/bemol)."""

from dataclasses import dataclass
from enum import Enum


class Acidente(Enum):
    """Acidente aplicado à nota. O valor é o caractere usado no texto."""

    NATURAL = ""
    SUSTENIDO = "#"
    BEMOL = "b"

    @classmethod
    def from_caractere(cls, caractere: str) -> "Acidente":
        """'#' -> SUSTENIDO, 'b' -> BEMOL, qualquer outro -> NATURAL."""
        raise NotImplementedError

    @staticmethod
    def eh_acidente(caractere: str) -> bool:
        raise NotImplementedError

    def deslocamento_semitons(self) -> int:
        """+1 para sustenido, -1 para bemol, 0 para natural."""
        raise NotImplementedError


@dataclass(frozen=True)
class NotaMusical:
    """Nota sem oitava: letra (A–G) + acidente. Objeto de valor imutável.

    Mapeamento do enunciado: A=Lá, B=Si, C=Dó, D=Ré, E=Mi, F=Fá, G=Sol.
    A letra H deixou de ser nota na Fase 2.
    """

    LETRAS_DE_NOTA = "ABCDEFG"

    letra: str
    acidente: Acidente = Acidente.NATURAL

    @classmethod
    def eh_letra_de_nota(cls, caractere: str) -> bool:
        """True para 'A'..'G' maiúsculos."""
        raise NotImplementedError

    def semitom(self) -> int:
        """Posição na escala cromática (Dó=0 ... Si=11), já com o acidente.

        TODO: tabela letra -> semitom e tratamento de casos de borda
        (ex.: Cb e B#, que atravessam a oitava).
        """
        raise NotImplementedError

    def altura_midi(self, oitava: int) -> int:
        """Número MIDI da nota na oitava dada (Dó4 = 60).

        Sugestão: 12 * (oitava + 1) + semitom().
        """
        raise NotImplementedError

    def nome(self) -> str:
        """Nome legível, ex.: 'Lá#', 'Mib' (útil para logs/testes)."""
        raise NotImplementedError
