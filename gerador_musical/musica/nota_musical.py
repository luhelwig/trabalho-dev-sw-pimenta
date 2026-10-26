"""NOVA (Fase 2, Mudança 4): nota com acidente (sustenido ou bemol)."""

from dataclasses import dataclass
from enum import Enum
from operator import and_


class Acidente(Enum):
    """Acidente aplicado à nota. O valor de cada membro é o caractere do texto.

    NATURAL = "" (sem acidente), SUSTENIDO = "#", BEMOL = "b".
    """

    NATURAL = ""
    SUSTENIDO = "#"
    BEMOL = "b"

    @classmethod
    def from_caractere(cls, caractere: str) -> "Acidente":
        """Converte o caractere do texto em Acidente.

        Args:
            caractere: '#', 'b' ou qualquer outro texto.

        Returns:
            SUSTENIDO para '#', BEMOL para 'b' e NATURAL para o resto.
        """
        try:
            return cls(caractere)
        except ValueError:
            return cls.NATURAL

    @staticmethod
    def eh_acidente(caractere: str) -> bool:
        """Diz se o caractere é um acidente.

        Args:
            caractere: caractere logo depois da letra da nota.

        Returns:
            True para '#' ou 'b'.
        """
        return caractere in ("#", "b")

    def deslocamento_semitons(self) -> int:
        """Devolve quantos semitons o acidente desloca a nota.

        Returns:
            +1 para sustenido, -1 para bemol e 0 para natural.
        """
        if self is Acidente.SUSTENIDO:
            return 1
        elif self is Acidente.BEMOL:
            return -1
        else:
            return 0



@dataclass(frozen=True)
class NotaMusical:
    """Nota sem oitava: letra (A–G) + acidente. Objeto de valor imutável.

    Duas notas com a mesma letra e o mesmo acidente são iguais. Mapeamento do
    enunciado: A=Lá, B=Si, C=Dó, D=Ré, E=Mi, F=Fá, G=Sol. A letra H deixou
    de ser nota na Fase 2.

    Attributes:
        letra: letra maiúscula de 'A' a 'G'.
        acidente: Acidente aplicado (NATURAL por padrão).
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
        """Diz se o caractere começa uma nota.

        Args:
            caractere: caractere do texto.

        Returns:
            True só para 'A'..'G' maiúsculos.
        """
        return len(caractere) == 1 and caractere in cls.LETRAS_DE_NOTA

    def semitom(self) -> int:
        """Devolve a posição na escala cromática a partir do Dó, já com o acidente.

        Dó=0, Ré=2, Mi=4, Fá=5, Sol=7, Lá=9, Si=11. Com acidente o resultado
        pode ser -1 (Cb) ou 12 (B#), que caem na oitava vizinha.

        Returns:
            Semitom da letra + deslocamento do acidente.
        """
        return self.SEMITONS[self.letra] + self.acidente.deslocamento_semitons()

    def altura_midi(self, oitava: int) -> int:
        """Calcula o número MIDI da nota numa oitava (Dó4 = 60, Lá4 = 69).

        Args:
            oitava: oitava da nota (0 a 8).

        Returns:
            12 * (oitava + 1) + semitom().

        Raises:
            ValueError: se o resultado sair da faixa MIDI 0–127.
        """
        valor_midi= 12 * (oitava +1 ) + self.semitom()
        if valor_midi < 0 or valor_midi > 127:
            raise ValueError(f"Nota fora da faixa MIDI (0–127): {valor_midi}")
        else:
            return valor_midi


    def nome(self) -> str:
        """Devolve o nome legível da nota, ex.: 'Lá#', 'Mib'."""
        return self.NOMES[self.letra] + self.acidente.value
