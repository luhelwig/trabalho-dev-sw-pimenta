"""NOVA (Fase 2, Mudança 4): uma voz = uma linha do texto."""

from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica


class Voz:
    """Sequência de eventos de uma linha, com seus próprios parâmetros.

    A voz de índice i é a linha i do texto (V0 = primeira linha).
    """

    CANAL_PERCUSSAO_MIDI = 9  # canal 10 do GM é bateria: não usar para vozes

    def __init__(self, indice: int, parametros: ParametrosMusica) -> None:
        self.indice: int = indice
        self.parametros: ParametrosMusica = parametros
        self.atraso_beats: float = 0.0
        self.eventos: list[EventoMusical] = []

    def adicionar_evento(self, evento: EventoMusical) -> None:
        raise NotImplementedError

    def get_eventos(self) -> list[EventoMusical]:
        raise NotImplementedError

    def set_atraso(self, beats: float) -> None:
        """Atraso de entrada vindo de "[n]" no início da linha.

        Raises:
            ValueError: atraso negativo.
        """
        raise NotImplementedError

    def get_atraso(self) -> float:
        raise NotImplementedError

    def posicao_atual_beats(self) -> float:
        """Onde a voz está agora: atraso + soma das durações já adicionadas.

        Usada para posicionar mudanças de andamento ('>' / '<') no tempo.
        """
        raise NotImplementedError

    def duracao_total_beats(self) -> float:
        raise NotImplementedError

    def ultima_nota(self) -> EventoMusical | None:
        """Último evento do tipo nota (para a regra de repetir nota)."""
        raise NotImplementedError

    def canal_midi(self) -> int:
        """Canal MIDI da voz, pulando o canal de percussão (9)."""
        raise NotImplementedError

    def esta_vazia(self) -> bool:
        raise NotImplementedError
