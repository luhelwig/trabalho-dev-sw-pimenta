"""Testes do Tokenizador. Cada stub descreve o comportamento esperado;
substitua o pytest.skip pelo teste de verdade."""

import pytest


def test_linha_vazia_gera_lista_vazia():
    pytest.skip("TODO")


def test_nota_sem_duracao():
    """"A" -> 1 token NOTA, letra A, NATURAL, duracao None."""
    pytest.skip("TODO")


def test_nota_com_duracao():
    """"A:3" -> NOTA, duracao SEMINIMA, lexema "A:3"."""
    pytest.skip("TODO")


def test_nota_com_sustenido_e_duracao():
    """"C#:3" -> NOTA C, SUSTENIDO, SEMINIMA."""
    pytest.skip("TODO")


def test_nota_com_bemol():
    """"Eb:2" -> NOTA E, BEMOL, MINIMA."""
    pytest.skip("TODO")


def test_b_minusculo_sozinho_e_caractere():
    """"b" (sem nota antes) -> CARACTERE 'b' (vira pausa nas regras)."""
    pytest.skip("TODO")


def test_atraso_no_inicio_da_linha():
    """"[4] C:2" -> ATRASO(valor=4), NOTA C (o espaço após ']' é consumido)."""
    pytest.skip("TODO")


def test_colchete_fora_do_inicio_nao_e_atraso():
    """"C [4]" -> nenhum token ATRASO."""
    pytest.skip("TODO")


def test_digito_solto_vira_caractere():
    """"A 2" -> NOTA, CARACTERE ' ', CARACTERE '2'."""
    pytest.skip("TODO")


def test_duracao_invalida():
    """"A:9" -> comportamento decidido pelo grupo (erro ou caracteres soltos)."""
    pytest.skip("TODO")
