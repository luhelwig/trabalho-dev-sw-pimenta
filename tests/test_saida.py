"""Testes de Sintetizador, ExportadorMidi e Player.

Para o Player, crie um BackendAudio falso que só registra as chamadas.
"""

import pytest

# ---- Sintetizador -------------------------------------------------------


def test_uma_trilha_de_andamento_mais_uma_por_voz():
    pytest.skip("TODO")


def test_nota_gera_note_on_e_note_off_com_volume_como_velocity():
    pytest.skip("TODO")


def test_troca_de_instrumento_gera_program_change():
    pytest.skip("TODO")


def test_atraso_da_voz_vira_ticks_antes_da_primeira_nota():
    pytest.skip("TODO")


def test_mudanca_de_andamento_gera_set_tempo_na_trilha_0():
    pytest.skip("TODO")


def test_vozes_nao_usam_canal_de_percussao():
    pytest.skip("TODO")


# ---- ExportadorMidi -----------------------------------------------------


def test_exporta_no_diretorio_configurado(tmp_path):
    pytest.skip("TODO")


def test_arquivo_exportado_pode_ser_lido_de_volta(tmp_path):
    """mido.MidiFile(caminho) tem as mesmas trilhas."""
    pytest.skip("TODO")


# ---- Player -------------------------------------------------------------


def test_play_sem_musica_gera_erro():
    pytest.skip("TODO")


def test_play_pausar_retomar_stop_chamam_backend():
    pytest.skip("TODO")


def test_tocar_de_novo_nao_recria_a_musica():
    pytest.skip("TODO")
