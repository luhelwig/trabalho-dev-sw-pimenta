"""NOVA (Fase 2, Mudança 4): figuras de duração."""

from enum import Enum


class Duracao(Enum):
    """Figura de duração, identificada pelo número usado no texto ("A:3").

    O valor de cada membro é o identificador do enunciado (1 a 7).
    Cada figura vale metade da anterior.

    ATENÇÃO (decisão do grupo): o enunciado diz que a semibreve "vale o
    tempo inteiro (1)". Em MIDI/BPM o normal é a SEMÍNIMA valer 1 beat
    (logo semibreve = 4 beats). Escolham uma e usem em em_beats(), no
    atraso [n] e no Sintetizador.
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

        Raises:
            ValueError: identificador fora de 1–7.
        """
        raise NotImplementedError

    @classmethod
    def padrao(cls) -> "Duracao":
        """Duração usada quando a nota/pausa não traz ":n".

        TODO (decisão do grupo): o enunciado não define. Sugestão: SEMINIMA.
        """
        raise NotImplementedError

    def fracao_da_semibreve(self) -> float:
        """1, 1/2, 1/4, ..., 1/64."""
        raise NotImplementedError

    def em_beats(self) -> float:
        """Duração em beats (unidade usada pelo BPM e pelo atraso [n])."""
        raise NotImplementedError
