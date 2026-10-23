"""NOVA (Fase 2, Mudança 4): nota com acidente (sustenido/bemol)."""

from dataclasses import dataclass
from enum import Enum
from operator import and_


class Acidente(Enum):
    """Acidente aplicado à nota. O valor é o caractere usado no texto."""

    NATURAL = ""
    SUSTENIDO = "#"
    BEMOL = "b"

    @classmethod
    def from_caractere(cls, caractere: str) -> "Acidente":
        """'#' -> SUSTENIDO, 'b' -> BEMOL, qualquer outro -> NATURAL."""
        try:
            return cls(caractere)
        except ValueError:
            return cls.NATURAL

    @staticmethod
    def eh_acidente(caractere: str) -> bool:
        return caractere in ("#", "b")

    def deslocamento_semitons(self) -> int:
        """+1 para sustenido, -1 para bemol, 0 para natural."""
        if self is Acidente.SUSTENIDO:
            return 1
        elif self is Acidente.BEMOL:
            return -1
        else:
            return 0



@dataclass(frozen=True)
class NotaMusical:
    """Nota sem oitava: letra (A–G) + acidente. Objeto de valor imutável.

    Mapeamento do enunciado: A=Lá, B=Si, C=Dó, D=Ré, E=Mi, F=Fá, G=Sol.
    A letra H deixou de ser nota na Fase 2.
    """

    LETRAS_DE_NOTA = "ABCDEFG"
    SEMITONS = {"C": 0,
                "D": 2,
                "E": 4,
                "F": 5,
                "G": 7,
                "A": 9,
                "B": 11}

    NOMES = {"A": "Lá",
             "B": "Si",
             "C": "Dó",
             "D": "Ré",
             "E": "Mi",
             "F": "Fá",
             "G": "Sol"}

    letra: str
    acidente: Acidente = Acidente.NATURAL

    @classmethod
    def eh_letra_de_nota(cls, caractere: str) -> bool:
        """True para 'A'..'G' maiúsculos."""
        return len(caractere) == 1 and caractere in cls.LETRAS_DE_NOTA

    def semitom(self) -> int:
        """Posição na escala cromática (Dó=-1 ... Si=12), já com o acidente.
        (ex.: Cb e B#, que atravessam a oitava).
        """
        return self.SEMITONS[self.letra] + self.acidente.deslocamento_semitons()

    def altura_midi(self, oitava: int) -> int:
        """Número MIDI da nota na oitava dada (Dó4 = 60).
        """
        valor_midi= 12 * (oitava +1 ) + self.semitom()
        if valor_midi < 0 or valor_midi > 127:
            raise ValueError(f"Nota fora da faixa MIDI (0–127): {valor_midi}")
        else:
            return valor_midi


    def nome(self) -> str:
        """Nome legível, ex.: 'Lá#', 'Mib' (útil para logs/testes)."""
        return self.NOMES[self.letra] + self.acidente.value
