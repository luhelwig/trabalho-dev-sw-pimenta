"""Classe Sintetizador (Fase 1, adaptada na Fase 2)."""

import mido

from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


class Sintetizador:
    """Converte uma Partitura em um arquivo MIDI em memória (mido.MidiFile).

    Formato sugerido: MIDI tipo 1 (várias trilhas tocando juntas)
      - trilha 0: só andamento (set_tempo inicial + uma por MudancaAndamento);
      - trilha i+1: voz i, no canal voz.canal_midi().

    MUDANÇAS EM RELAÇÃO À FASE 1:
      - gerar_onda(evento) virou gerar_mensagens(evento, canal): com MIDI
        não geramos forma de onda, e sim mensagens note_on/note_off;
      - exportar_midi saiu daqui para ExportadorMidi (gravar arquivo é
        outra responsabilidade e permite novos formatos sem mexer aqui).
    """

    TICKS_POR_BEAT = 480

    def __init__(self) -> None:
        self.partitura: Partitura | None = None

    def gerar_musica(self, partitura: Partitura) -> mido.MidiFile:
        raise NotImplementedError

    def _criar_trilha_andamento(self, partitura: Partitura) -> mido.MidiTrack:
        """set_tempo usa microssegundos por beat: mido.bpm2tempo(bpm).
        Mensagens em MIDI usam tempo DELTA (ticks desde a anterior)."""
        raise NotImplementedError

    def _criar_trilha_voz(self, voz: Voz) -> mido.MidiTrack:
        """Atraso inicial + program_change sempre que o instrumento mudar
        + mensagens de cada evento."""
        raise NotImplementedError

    def gerar_mensagens(self, evento: EventoMusical, canal: int) -> list[mido.Message]:
        """Nota -> note_on + note_off (velocity = volume).
        Pausa -> nenhuma mensagem; só avança o tempo da próxima."""
        raise NotImplementedError

    def beats_para_ticks(self, beats: float) -> int:
        raise NotImplementedError
