"""Testes de integração do Parser (Tokenizador + Mapeamento reais)."""

import pytest


def test_cada_linha_vira_uma_voz():
    """"A:3\\nC:3\\nE:3\\nG:3" -> 4 vozes, V0..V3."""
    pytest.skip("TODO")


def test_vozes_comecam_com_parametros_padrao():
    pytest.skip("TODO")


def test_atraso_de_entrada():
    """"[4] C:2 D:2 E:3" -> voz com atraso 4 beats e 3 notas."""
    pytest.skip("TODO")


def test_andamento_vale_para_todas_as_vozes():
    pytest.skip("TODO")


def test_nota_anterior_nao_atravessa_linhas():
    """"A:3\\nH" -> na voz 1, H é pausa (não repete o Lá da voz 0)."""
    pytest.skip("TODO")


def test_regerar_com_nova_configuracao_sem_retokenizar():
    """Muda o instrumento de V0 na ConfiguracaoInicial e chama só
    token_to_partitura: as notas de V0 saem com o novo instrumento."""
    pytest.skip("TODO")


def test_texto_com_caracteres_inesperados_nao_quebra():
    pytest.skip("TODO")
