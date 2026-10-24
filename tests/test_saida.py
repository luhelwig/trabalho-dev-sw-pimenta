"""Testes de Sintetizador, ExportadorMidi e Player.

Os testes do Player usam o fixture `backend` do tests/conftest.py: um
backend falso que só anota o que foi chamado, então rodam sem som.
"""

import mido
import pytest

from gerador_musical.excecoes import MusicaNaoGeradaErro
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.saida.exportador import ExportadorMidi
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador
from gerador_musical.saida.backend_audio import BackendAudio

def gerar(texto):
    """Atalho: texto -> Partitura -> MidiFile, com as peças reais."""
    parser = Parser(Tokenizador(), Mapeamento.padrao(), ConfiguracaoInicial.padrao())
    return Sintetizador().gerar_musica(parser.interpretar(texto))


def mensagens(trilha, tipo):
    """Só as mensagens de um tipo ("note_on", "program_change"...) de uma trilha."""
    return [m for m in trilha if m.type == tipo]


# ---- Sintetizador (Etapa 8) ---------------------------------------------
# A trilha 0 é a de andamento; a voz 0 fica em midi.tracks[1].


def test_uma_trilha_de_andamento_mais_uma_por_voz():
    midi = gerar("A:3\nC:3")
    assert len(midi.tracks) == 3


def test_nota_gera_note_on_e_note_off_com_volume_como_velocity():
    midi = gerar("C:3")                      # V0: oitava 6, volume 100
    [note_on] = mensagens(midi.tracks[1], "note_on")
    [note_off] = mensagens(midi.tracks[1], "note_off")
    assert note_on.note == 84                # Dó6
    assert note_on.velocity == 100
    assert note_off.time == 480              # 1 beat depois


def test_troca_de_instrumento_gera_program_change():
    midi = gerar("C:3!C:3")                  # "!" troca para Bandoneon
    programas = [m.program for m in mensagens(midi.tracks[1], "program_change")]
    assert programas == [6, 23]              # Cravo, depois Bandoneon


def test_atraso_da_voz_vira_ticks_antes_da_primeira_nota():
    midi = gerar("[2] C:3")
    assert midi.tracks[1][0].time == 960     # 2 beats x 480 ticks


def test_mudanca_de_andamento_gera_set_tempo_na_trilha_0():
    midi = gerar("C:3>C:3")
    tempos = mensagens(midi.tracks[0], "set_tempo")
    assert len(tempos) == 2
    assert tempos[1].tempo == mido.bpm2tempo(130)
    assert tempos[1].time == 480


def test_vozes_nao_usam_canal_de_percussao():
    midi = gerar("\n".join(["C:3"] * 10))    # 10 vozes
    canais = [getattr(m, "channel", None) for trilha in midi.tracks for m in trilha]
    assert 9 not in canais


# ---- ExportadorMidi (Etapa 8) -------------------------------------------


def test_exporta_no_diretorio_configurado(tmp_path):
    caminho = ExportadorMidi(tmp_path).exportar(gerar("C:3"))
    assert caminho.exists()
    assert caminho.parent == tmp_path


def test_arquivo_exportado_pode_ser_lido_de_volta(tmp_path):
    midi = gerar("C:3")
    caminho = ExportadorMidi(tmp_path).exportar(midi)
    assert len(mido.MidiFile(caminho).tracks) == len(midi.tracks)


# ---- Player (Etapa 9) ---------------------------------------------------


def test_play_sem_musica_gera_erro(backend):
    with pytest.raises(MusicaNaoGeradaErro):
        Player(backend).play()


def test_play_pausar_retomar_stop_chamam_backend(backend):
    player = Player(backend)
    player.carregar(gerar("C:3"))            # o carregar chama "parar" primeiro
    player.play()
    player.pausar()
    player.retomar()
    player.stop()
    assert backend.chamadas == ["parar", "carregar", "tocar", "pausar", "retomar", "parar"]


def test_tocar_de_novo_nao_recria_a_musica(backend):
    musica = gerar("C:3")
    player = Player(backend)
    player.carregar(musica)
    player.play()
    player.stop()
    player.play()
    assert player.musica is musica


def test_pausado_nao_conta_como_terminou(backend):
    player = Player(backend)
    player.carregar(gerar("C:3"))
    player.play()
    player.pausar()
    backend.tocando = False                  # o pygame também diz "não tocando" quando pausado
    assert player.terminou() is False
