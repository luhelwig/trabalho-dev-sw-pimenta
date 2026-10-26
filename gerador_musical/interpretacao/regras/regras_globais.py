"""Regras que afetam a música inteira (todas as vozes)."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.regra_mapeamento import RegraPorCaractere
from gerador_musical.interpretacao.tokens import Token


class RegraAndamento(RegraPorCaractere):
    """'>' acelera (+10 BPM) e '<' desacelera (-10 BPM), para todas as vozes.

    Registra uma MudancaAndamento na Partitura na posição atual da voz. Não
    altera o BPM na hora: quem calcula o BPM de cada ponto é
    Partitura.bpm_em.

    Attributes:
        delta_bpm: quanto o BPM muda.
    """

    def __init__(self, caracteres: str, delta_bpm: int) -> None:
        """Cria a regra.

        Args:
            caracteres: caracteres que disparam a regra ('>' ou '<').
            delta_bpm: quanto o BPM muda (+10 ou -10).
        """
        super().__init__(caracteres)
        self.delta_bpm: int = delta_bpm

    def aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        """Registra a mudança de andamento na posição atual da voz.

        Args:
            token: token CARACTERE.
            contexto: estado da linha.
        """
        contexto.partitura.registrar_mudanca_andamento(contexto.posicao_atual_beats(), self.delta_bpm)
