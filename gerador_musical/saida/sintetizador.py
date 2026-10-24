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
        self.partitura = partitura
        midi = mido.MidiFile(type=1, ticks_per_beat=self.TICKS_POR_BEAT)
        midi.tracks.append(self._criar_trilha_andamento(partitura))
        for voz in partitura.get_vozes():
            midi.tracks.append(self._criar_trilha_voz(voz))
        return midi

    def _criar_trilha_andamento(self, partitura: Partitura) -> mido.MidiTrack:
        """set_tempo usa microssegundos por beat: mido.bpm2tempo(bpm).
        Mensagens em MIDI usam tempo DELTA (ticks desde a anterior)."""
        trilha = mido.MidiTrack()
        trilha.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(partitura.get_bpm_inicial()), time=0))
        tick_anterior = 0
        for mudanca in partitura.get_mudancas_andamento():
            tick = self.beats_para_ticks(mudanca.posicao_beats)
            bpm = partitura.bpm_em(mudanca.posicao_beats)
            trilha.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=tick - tick_anterior))
            tick_anterior = tick
        return trilha

    def _criar_trilha_voz(self, voz: Voz) -> mido.MidiTrack:
        """Atraso inicial + program_change sempre que o instrumento mudar
        + mensagens de cada evento."""
        trilha = mido.MidiTrack()
        canal = voz.canal_midi()
        espera = self.beats_para_ticks(voz.get_atraso())
        instrumento = None
        for evento in voz.get_eventos():
            if evento.eh_pausa():
                espera += self.beats_para_ticks(evento.duracao_em_beats())
                continue
            if evento.instrumento != instrumento:
                trilha.append(mido.Message("program_change", program=evento.instrumento, channel=canal, time=espera))
                espera = 0
                instrumento = evento.instrumento
            note_on, note_off = self.gerar_mensagens(evento, canal)
            trilha.append(note_on.copy(time=espera))
            trilha.append(note_off)
            espera = 0
        return trilha

    def gerar_mensagens(self, evento: EventoMusical, canal: int) -> list[mido.Message]:
        """Nota -> note_on + note_off (velocity = volume).
        Pausa -> nenhuma mensagem; só avança o tempo da próxima."""
        altura = evento.altura_midi()
        ticks = self.beats_para_ticks(evento.duracao_em_beats())
        return [
            mido.Message("note_on", note=altura, velocity=evento.volume, channel=canal, time=0),
            mido.Message("note_off", note=altura, velocity=0, channel=canal, time=ticks),
        ]
    def beats_para_ticks(self, beats: float) -> int:
        return round(beats * self.TICKS_POR_BEAT)
