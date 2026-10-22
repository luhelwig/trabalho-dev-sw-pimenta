"""Regras que afetam a música inteira (todas as vozes)."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import RegraPorCaractere
from gerador_musical.interpretacao.tokens import Token


class RegraAndamento(RegraPorCaractere):
    """'>' acelera (+10 BPM) e '<' desacelera (-10 BPM), para todas as vozes.

    Registra uma MudancaAndamento na Partitura na posição atual da voz
    (contexto.posicao_atual_beats()). Não altera BPM diretamente.
    """

    def __init__(self, caracteres: str, delta_bpm: int) -> None:
        super().__init__(caracteres)
        self.delta_bpm: int = delta_bpm

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError
