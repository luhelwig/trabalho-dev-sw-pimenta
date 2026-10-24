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
        self.eventos.append(evento)

    def get_eventos(self) -> list[EventoMusical]:
        return list(self.eventos)

    def set_atraso(self, beats: float) -> None:
        """Atraso de entrada vindo de "[n]" no início da linha.

        Raises:
            ValueError: atraso negativo.
        """
        if beats < 0:
            raise ValueError("atraso negativo.")
        else:
            self.atraso_beats = beats

    def get_atraso(self) -> float:
        return self.atraso_beats

    def posicao_atual_beats(self) -> float:
        """Onde a voz está agora: atraso + soma das durações já adicionadas.

        Usada para posicionar mudanças de andamento ('>' / '<') no tempo.
        """
        return self.atraso_beats + sum(e.duracao_em_beats() for e in self.eventos)

    def duracao_total_beats(self) -> float:
        return self.posicao_atual_beats()

    def ultima_nota(self) -> EventoMusical | None:
        """Último evento do tipo nota (para a regra de repetir nota)."""
        for evento in reversed(self.eventos):
            if evento.eh_nota():
                return evento
        return None

    def canal_midi(self) -> int:
        """Canal MIDI da voz, pulando o canal de percussão (9)."""
        canal = self.indice % 15
        if canal < self.CANAL_PERCUSSAO_MIDI:
            return canal
        else:
            return canal + 1

    def esta_vazia(self) -> bool:
        return not self.eventos
