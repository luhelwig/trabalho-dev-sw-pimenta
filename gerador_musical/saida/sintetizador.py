"""Classe Sintetizador (Fase 1, adaptada na Fase 2)."""

import mido

from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


class Sintetizador:
    """Converte uma Partitura em um arquivo MIDI em memória (mido.MidiFile).

    Formato: MIDI tipo 1 (várias trilhas tocando juntas):
      - trilha 0: só andamento (set_tempo inicial + um por MudancaAndamento);
      - trilha i+1: voz i, no canal voz.canal_midi().

    O tempo das mensagens MIDI é DELTA: ticks desde a mensagem anterior da
    mesma trilha. Pausas não geram mensagem; só atrasam a próxima.

    Mudanças em relação à Fase 1: gerar_onda(evento) virou
    gerar_mensagens(evento, canal), porque com MIDI não geramos forma de
    onda, e sim mensagens note_on/note_off; e exportar o arquivo saiu daqui
    para o ExportadorMidi (outra responsabilidade).

    Attributes:
        TICKS_POR_BEAT: resolução do arquivo MIDI (480 ticks por beat).
    """

    TICKS_POR_BEAT = 480

    def gerar_musica(self, partitura: Partitura) -> mido.MidiFile:
        """Converte a partitura em MIDI tipo 1.

        Args:
            partitura: música interpretada.

        Returns:
            MidiFile com a trilha de andamento e uma trilha por voz.
        """
        midi = mido.MidiFile(type=1, ticks_per_beat=self.TICKS_POR_BEAT)
        midi.tracks.append(self._criar_trilha_andamento(partitura))
        for voz in partitura.get_vozes():
            midi.tracks.append(self._criar_trilha_voz(voz))
        return midi

    def _criar_trilha_andamento(self, partitura: Partitura) -> mido.MidiTrack:
        """Cria a trilha 0, só com mensagens set_tempo.

        set_tempo usa microssegundos por beat (mido.bpm2tempo(bpm)), e o time
        de cada mensagem é o delta em ticks desde a anterior.

        Args:
            partitura: música interpretada.

        Returns:
            A trilha de andamento.
        """
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
        """Cria a trilha de uma voz.

        Começa com o atraso da voz, emite program_change sempre que o
        instrumento muda e note_on/note_off para cada nota. Pausas só acumulam
        espera; se a voz termina com pausas, um end_of_track segura a trilha até
        o fim do silêncio.

        Args:
            voz: voz a converter.

        Returns:
            A trilha da voz.
        """
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
        if espera > 0:  # pausas no fim da voz: segura o fim da trilha
            trilha.append(mido.MetaMessage("end_of_track", time=espera))
        return trilha

    def gerar_mensagens(self, evento: EventoMusical, canal: int) -> list[mido.Message]:
        """Gera as mensagens MIDI de uma nota (velocity = volume).

        Args:
            evento: evento do tipo nota.
            canal: canal MIDI da voz.

        Returns:
            [note_on com time=0, note_off com time = duração em ticks].
        """
        altura = evento.altura_midi()
        ticks = self.beats_para_ticks(evento.duracao_em_beats())
        return [
            mido.Message("note_on", note=altura, velocity=evento.volume, channel=canal, time=0),
            mido.Message("note_off", note=altura, velocity=0, channel=canal, time=ticks),
        ]
    def beats_para_ticks(self, beats: float) -> int:
        """Converte beats em ticks MIDI inteiros (beats * TICKS_POR_BEAT)."""
        return round(beats * self.TICKS_POR_BEAT)
