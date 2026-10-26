"""NOVA (Fase 2): resultado da interpretação — todas as vozes + andamento."""

from dataclasses import dataclass
from gerador_musical.musica.voz import Voz
from gerador_musical.musica.limites import BPM_MAXIMO, BPM_MINIMO

@dataclass(frozen=True)
class MudancaAndamento:
    """Um '>' ou '<' lido numa voz, posicionado no tempo da música.

    Guarda o DELTA e não o BPM final: as linhas são lidas uma de cada vez,
    então só dá para saber o BPM real em cada ponto depois de ordenar as
    mudanças de todas as vozes (ver Partitura.bpm_em). Objeto imutável.

    Attributes:
        posicao_beats: momento da mudança, em beats desde o início.
        delta_bpm: quanto o BPM muda (+10 ou -10).
    """

    posicao_beats: float
    delta_bpm: int


class Partitura:
    """Representação completa da música, independente de texto e de MIDI.

    Attributes:
        bpm_inicial: BPM com que a música começa.
        vozes: uma Voz por linha do texto.
        mudancas_andamento: mudanças de BPM de todas as vozes.
    """

    def __init__(self, bpm_inicial: int) -> None:
        """Cria uma partitura vazia.

        Args:
            bpm_inicial: BPM com que a música começa.
        """
        self.bpm_inicial: int = bpm_inicial
        self.vozes: list[Voz] = []
        self.mudancas_andamento: list[MudancaAndamento] = []

    def adicionar_voz(self, voz: Voz) -> None:
        """Acrescenta uma voz à partitura."""
        self.vozes.append(voz)

    def get_vozes(self) -> list[Voz]:
        """Devolve uma cópia da lista de vozes."""
        return list(self.vozes)

    def numero_de_vozes(self) -> int:
        """Devolve quantas vozes a partitura tem."""
        return len(self.vozes)

    def get_bpm_inicial(self) -> int:
        """Devolve o BPM com que a música começa."""
        return self.bpm_inicial

    def registrar_mudanca_andamento(self, posicao_beats: float, delta_bpm: int) -> None:
        """Registra uma mudança de andamento (chamado pela RegraAndamento).

        Args:
            posicao_beats: momento da mudança, em beats.
            delta_bpm: quanto o BPM muda.
        """
        self.mudancas_andamento.append(MudancaAndamento(posicao_beats, delta_bpm))

    def get_mudancas_andamento(self) -> list[MudancaAndamento]:
        """Devolve as mudanças de andamento ordenadas por posição.

        Vale para TODAS as vozes: uma mudança lida em qualquer linha muda o
        andamento da música inteira.
        """
        return sorted(self.mudancas_andamento, key=lambda m: m.posicao_beats)

    def bpm_em(self, posicao_beats: float) -> int:
        """Calcula o BPM efetivo num ponto da música.

        Começa no BPM inicial e soma, em ordem, os deltas das mudanças até a
        posição, limitando a [BPM_MINIMO, BPM_MAXIMO] a cada passo.

        Args:
            posicao_beats: ponto da música, em beats.

        Returns:
            O BPM naquele ponto.
        """
        bpm = self.bpm_inicial
        for m in self.get_mudancas_andamento():
            if m.posicao_beats > posicao_beats:
                break
            else:
                bpm = min(max(bpm + m.delta_bpm, BPM_MINIMO), BPM_MAXIMO)
        return bpm

    def duracao_total_beats(self) -> float:
        """Devolve a duração da voz mais longa, em beats (0 sem vozes)."""
        return max((v.duracao_total_beats() for v in self.vozes), default=0)


    def esta_vazia(self) -> bool:
        """Diz se nenhuma voz tem eventos."""
        return all(v.esta_vazia() for v in self.vozes)
