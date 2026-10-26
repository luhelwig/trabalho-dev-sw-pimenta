"""Testes do Tokenizador: como cada linha é quebrada em tokens."""

import pytest
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.interpretacao.tokens import TipoToken
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import Acidente, NotaMusical

def tokenizar(linha):
    """Atalho: tokeniza uma linha com um Tokenizador novo."""
    return Tokenizador().tokenizar(linha)

def test_linha_vazia_gera_lista_vazia():
    assert tokenizar("") == []



def test_nota_sem_duracao():
    """"A" -> 1 token NOTA, letra A, NATURAL, duracao None."""
    [t] = tokenizar("A")
    assert t.nota == NotaMusical("A")
    assert t.duracao is None


def test_nota_com_duracao():
    """"A:3" -> NOTA, duracao SEMINIMA, lexema "A:3"."""
    [t] = tokenizar("A:3")
    assert t.duracao is Duracao.SEMINIMA
    assert t.lexema == "A:3"


def test_nota_com_sustenido_e_duracao():
    """"C#:3" -> NOTA C, SUSTENIDO, SEMINIMA."""
    [t] = tokenizar("C#:3")
    assert t.nota == NotaMusical("C", Acidente.SUSTENIDO)


def test_nota_com_bemol():
    """"Eb:2" -> NOTA E, BEMOL, MINIMA."""
    [t] = tokenizar("Eb:2")
    assert t.nota == NotaMusical("E", Acidente.BEMOL)
    assert t.duracao is Duracao.MINIMA


def test_b_minusculo_sozinho_e_caractere():
    """"b" (sem nota antes) -> CARACTERE 'b' (vira pausa nas regras)."""
    [t] = tokenizar("b")
    assert t.tipo is TipoToken.CARACTERE


def test_atraso_no_inicio_da_linha():
    """"[4] C:2" -> ATRASO(valor=4), NOTA C (o espaço após ']' é consumido)."""
    tokens = tokenizar("[4] C:2")
    assert [t.tipo for t in tokens] == [TipoToken.ATRASO, TipoToken.NOTA]
    assert tokens[0].valor == 4

def test_colchete_fora_do_inicio_nao_e_atraso():
    """"C [4]" -> nenhum token ATRASO."""
    assert all(t.tipo is not TipoToken.ATRASO for t in tokenizar("C [4]"))


def test_digito_solto_vira_caractere():
    """"A 2" -> NOTA, CARACTERE ' ', CARACTERE '2'."""
    assert [t.lexema for t in tokenizar("A 2")] == ["A", " ", "2"]


def test_duracao_invalida():
    """"A:9" -> comportamento decidido pelo grupo (erro ou caracteres soltos)."""
    assert [t.lexema for t in tokenizar("A:9")] == ["A", ":", "9"]


def test_exemplo_do_enunciado():
    tokens = tokenizar("[4] C:2 D:2 E:3")
    assert [t.lexema for t in tokens] == ["[4]", "C:2", " ", "D:2", " ", "E:3"]