"""NOVA (Fase 2, Mudança 4): uma voz = uma linha do texto."""

from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.parametros_musica import ParametrosMusica


class Voz:
    """Sequência de eventos de uma linha, com seus próprios parâmetros.

    A voz de índice i é a linha i do texto (V0 = primeira linha).

    Attributes:
        indice: número da voz (linha do texto, começando em 0).
        parametros: parâmetros de instrumento, oitava e volume da voz.
        atraso_beats: silêncio antes da primeira nota, vindo de "[n]".
        eventos: notas e pausas, na ordem em que foram lidas.
        CANAL_PERCUSSAO_MIDI: canal reservado para bateria no General MIDI (9).
    """

    CANAL_PERCUSSAO_MIDI = 9  # canal 10 do GM é bateria: não usar para vozes

    def __init__(self, indice: int, parametros: ParametrosMusica) -> None:
        """Cria uma voz vazia, sem atraso.

        Args:
            indice: número da voz (linha do texto).
            parametros: parâmetros iniciais da voz.
        """
        self.indice: int = indice
        self.parametros: ParametrosMusica = parametros
        self.atraso_beats: float = 0.0
        self.eventos: list[EventoMusical] = []

    def adicionar_evento(self, evento: EventoMusical) -> None:
        """Acrescenta um evento (nota ou pausa) no fim da voz."""
        self.eventos.append(evento)

    def get_eventos(self) -> list[EventoMusical]:
        """Devolve uma cópia da lista de eventos."""
        return list(self.eventos)

    def set_atraso(self, beats: float) -> None:
        """Define o atraso de entrada vindo de "[n]" no início da linha.

        Args:
            beats: atraso em beats.

        Raises:
            ValueError: atraso negativo.
        """
        if beats < 0:
            raise ValueError("atraso negativo.")
        else:
            self.atraso_beats = beats

    def get_atraso(self) -> float:
        """Devolve o atraso de entrada em beats."""
        return self.atraso_beats

    def posicao_atual_beats(self) -> float:
        """Devolve onde a voz está agora: atraso + soma das durações.

        Usada para posicionar no tempo as mudanças de andamento ('>' e '<').
        """
        return self.atraso_beats + sum(e.duracao_em_beats() for e in self.eventos)

    def duracao_total_beats(self) -> float:
        """Devolve a duração total da voz em beats, contando o atraso."""
        return self.posicao_atual_beats()

    def ultima_nota(self) -> EventoMusical | None:
        """Devolve o último evento do tipo nota, ou None se não houver."""
        for evento in reversed(self.eventos):
            if evento.eh_nota():
                return evento
        return None

    def canal_midi(self) -> int:
        """Devolve o canal MIDI da voz, pulando o canal de percussão (9).

        Vozes 0–8 usam os canais 0–8; vozes 9–14 usam os canais 10–15; depois
        o ciclo recomeça.

        Returns:
            Canal MIDI de 0 a 15, nunca 9.
        """
        canal = self.indice % 15
        if canal < self.CANAL_PERCUSSAO_MIDI:
            return canal
        else:
            return canal + 1

    def esta_vazia(self) -> bool:
        """Diz se a voz não tem nenhum evento."""
        return not self.eventos
