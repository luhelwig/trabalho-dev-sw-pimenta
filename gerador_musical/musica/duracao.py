"""NOVA (Fase 2, Mudança 4): figuras de duração das notas.

BEATS_POR_SEMIBREVE = 4 registra a decisão do grupo: a semínima vale
1 beat, então a semibreve vale 4 beats.
"""

from enum import Enum
BEATS_POR_SEMIBREVE = 4

class Duracao(Enum):
    """Figura de duração, identificada pelo número usado no texto ("A:3").

    O valor de cada membro é o identificador do enunciado (1 a 7), e cada
    figura vale metade da anterior:

        SEMIBREVE=1 (4 beats), MINIMA=2 (2), SEMINIMA=3 (1), COLCHEIA=4 (1/2),
        SEMICOLCHEIA=5 (1/4), FUSA=6 (1/8), SEMIFUSA=7 (1/16)
    """

    SEMIBREVE = 1
    MINIMA = 2
    SEMINIMA = 3
    COLCHEIA = 4
    SEMICOLCHEIA = 5
    FUSA = 6
    SEMIFUSA = 7

    @classmethod
    def from_identificador(cls, identificador: int) -> "Duracao":
        """Converte o dígito lido no texto (1–7) em Duracao.

        Args:
            identificador: número escrito depois de ':' na nota.

        Returns:
            A figura correspondente.

        Raises:
            ValueError: identificador fora de 1–7.
        """
        try:
            return cls(identificador)
        except ValueError:
            raise ValueError(f"Duração Inválida: {identificador}! (Use 1 a 7)")


    @classmethod
    def padrao(cls) -> "Duracao":
        """Devolve a duração usada quando a nota não traz ":n" (semínima)."""
        return cls.SEMINIMA

    def fracao_da_semibreve(self) -> float:
        """Devolve quanto a figura vale em relação à semibreve.

        Returns:
            1 / 2 ** (identificador - 1): semibreve 1, mínima 1/2, semínima 1/4...
        """
        return 1/ 2**(self.value - 1)

    def em_beats(self) -> float:
        """Devolve a duração em beats (unidade do BPM e do atraso "[n]").

        Returns:
            fracao_da_semibreve() * BEATS_POR_SEMIBREVE. Ex.: semínima = 1.0.
        """
        return self.fracao_da_semibreve() * BEATS_POR_SEMIBREVE
