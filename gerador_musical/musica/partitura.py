"""NOVA (Fase 2): resultado da interpretação — todas as vozes + andamento."""

from dataclasses import dataclass

from gerador_musical.musica.voz import Voz


@dataclass(frozen=True)
class MudancaAndamento:
    """'>' ou '<' lido numa voz, posicionado no tempo da música.

    Guarda o DELTA, não o BPM final: as linhas são lidas uma de cada vez,
    então só dá para saber o BPM real em cada ponto depois de ordenar
    todas as mudanças por posição (ver Partitura.bpm_em).
    """

    posicao_beats: float
    delta_bpm: int


class Partitura:
    """Representação completa da música, independente de MIDI e de texto."""

    def __init__(self, bpm_inicial: int) -> None:
        self.bpm_inicial: int = bpm_inicial
        self.vozes: list[Voz] = []
        self.mudancas_andamento: list[MudancaAndamento] = []

    def adicionar_voz(self, voz: Voz) -> None:
        raise NotImplementedError

    def get_vozes(self) -> list[Voz]:
        raise NotImplementedError

    def numero_de_vozes(self) -> int:
        raise NotImplementedError

    def get_bpm_inicial(self) -> int:
        raise NotImplementedError

    def registrar_mudanca_andamento(self, posicao_beats: float, delta_bpm: int) -> None:
        raise NotImplementedError

    def get_mudancas_andamento(self) -> list[MudancaAndamento]:
        """Mudanças ordenadas por posição (vale para TODAS as vozes)."""
        raise NotImplementedError

    def bpm_em(self, posicao_beats: float) -> int:
        """BPM efetivo num ponto: bpm_inicial + deltas anteriores, limitado
        a [BPM_MINIMO, BPM_MAXIMO]."""
        raise NotImplementedError

    def duracao_total_beats(self) -> float:
        """Duração da voz mais longa (incluindo atrasos)."""
        raise NotImplementedError

    def esta_vazia(self) -> bool:
        """True se nenhuma voz tem eventos."""
        raise NotImplementedError
