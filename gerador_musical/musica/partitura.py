"""NOVA (Fase 2): resultado da interpretação — todas as vozes + andamento."""

from dataclasses import dataclass
from gerador_musical.musica.voz import Voz
from gerador_musical.musica.limites import BPM_MAXIMO, BPM_MINIMO

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
        self.vozes.append(voz)

    def get_vozes(self) -> list[Voz]:
        return list(self.vozes)

    def numero_de_vozes(self) -> int:
        return len(self.vozes)

    def get_bpm_inicial(self) -> int:
        return self.bpm_inicial

    def registrar_mudanca_andamento(self, posicao_beats: float, delta_bpm: int) -> None:
        self.mudancas_andamento.append(MudancaAndamento(posicao_beats, delta_bpm))

    def get_mudancas_andamento(self) -> list[MudancaAndamento]:
        """Mudanças ordenadas por posição (vale para TODAS as vozes)."""
        return sorted(self.mudancas_andamento, key=lambda m: m.posicao_beats)

    def bpm_em(self, posicao_beats: float) -> int:
        """BPM efetivo num ponto: bpm_inicial + deltas anteriores, limitado
        a [BPM_MINIMO, BPM_MAXIMO]."""
        bpm = self.bpm_inicial
        for m in self.get_mudancas_andamento():
            if m.posicao_beats > posicao_beats:
                break
            else:
                bpm = min(max(bpm + m.delta_bpm, BPM_MINIMO), BPM_MAXIMO)
        return bpm

    def duracao_total_beats(self) -> float:
        """Duração da voz mais longa (incluindo atrasos)."""
        return max((v.duracao_total_beats() for v in self.vozes), default=0)


    def esta_vazia(self) -> bool:
        """True se nenhuma voz tem eventos."""
        return all(v.esta_vazia() for v in self.vozes)
