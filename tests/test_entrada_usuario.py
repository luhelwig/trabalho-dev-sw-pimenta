"""Testes de EntradaUsuario e ArquivoTexto (use o fixture tmp_path do pytest)."""

import pytest


def test_texto_so_com_espacos_esta_vazio():
    pytest.skip("TODO")


def test_caracteres_de_outro_alfabeto_sao_formato_invalido():
    """Ex.: "A:3 Ж" ou "C:2 日" -> eh_formato_valido() == False."""
    pytest.skip("TODO")


def test_acentos_do_portugues_sao_validos():
    pytest.skip("TODO")


def test_carregar_arquivo_preenche_conteudo(tmp_path):
    pytest.skip("TODO")


def test_carregar_arquivo_que_nao_e_txt_gera_erro(tmp_path):
    pytest.skip("TODO")


def test_salvar_sem_caminho_sobrescreve_original(tmp_path):
    pytest.skip("TODO")


def test_salvar_sem_caminho_e_sem_origem_gera_erro():
    pytest.skip("TODO")


def test_foi_modificado():
    pytest.skip("TODO")
