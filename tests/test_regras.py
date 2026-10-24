"""Testes das regras de mapeamento.

Cada teste recebe um `contexto` novo (fixture do tests/conftest.py):
uma voz com instrumento 6 (Cravo), oitava 6 e volume 40, numa partitura
vazia com BPM 120.
"""

import pytest

from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.regras.regra_mapeamento import RegraPorCaractere
from gerador_musical.interpretacao.regras.regras_eventos import RegraNota, RegraPausa, RegraRepetirOuPausar
from gerador_musical.interpretacao.regras.regras_globais import RegraAndamento
from gerador_musical.interpretacao.regras.regras_voz import (
    RegraAtraso, RegraInstrumentoFixo, RegraInstrumentoSomaDigito, RegraOitava, RegraVolume,
)
from gerador_musical.interpretacao.tokens import TipoToken, Token
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.instrumentos import BANDONEON
from gerador_musical.musica.nota_musical import NotaMusical


def caractere(c):
    """Atalho: cria um token de um caractere solto (comando, pausa, etc.)."""
    return Token(TipoToken.CARACTERE, c, coluna=0)


def nota(letra, duracao=None):
    """Atalho: cria um token de nota, com ou sem duração."""
    return Token(TipoToken.NOTA, letra, coluna=0, nota=NotaMusical(letra), duracao=duracao)


# ---- Regras que geram eventos -------------------------------------------


def test_regra_nota_adiciona_evento_com_parametros_atuais_da_voz(contexto):
    RegraNota().aplicar(nota("A", Duracao.MINIMA), contexto)
    [evento] = contexto.voz.get_eventos()
    assert evento.eh_nota()
    assert evento.volume == 40
    assert evento.instrumento == 6


def test_regra_nota_sem_duracao_usa_duracao_padrao(contexto):
    RegraNota().aplicar(nota("A"), contexto)
    [evento] = contexto.voz.get_eventos()
    assert evento.duracao is Duracao.padrao()


def test_regra_pausa_adiciona_pausa(contexto):
    RegraPausa().aplicar(caractere("a"), contexto)
    [evento] = contexto.voz.get_eventos()
    assert evento.eh_pausa()


def test_repetir_ou_pausar_repete_quando_anterior_era_nota(contexto):
    token_la = nota("A")
    RegraNota().aplicar(token_la, contexto)
    contexto.avancar(token_la)          # o Parser faz isso depois de cada regra
    RegraRepetirOuPausar().aplicar(caractere("H"), contexto)
    eventos = contexto.voz.get_eventos()
    assert len(eventos) == 2
    assert all(e.eh_nota() and e.nota == NotaMusical("A") for e in eventos)


def test_repetir_ou_pausar_pausa_quando_anterior_nao_era_nota(contexto):
    RegraRepetirOuPausar().aplicar(caractere("H"), contexto)
    [evento] = contexto.voz.get_eventos()
    assert evento.eh_pausa()


# ---- Regras que mudam a voz ---------------------------------------------


def test_regra_volume_dobra_volume(contexto):
    RegraVolume().aplicar(caractere(" "), contexto)
    assert contexto.parametros().get_volume() == 80


def test_regra_oitava_sobe_com_interrogacao_e_desce_com_V(contexto):
    RegraOitava("?", +1).aplicar(caractere("?"), contexto)
    assert contexto.parametros().get_oitava() == 7
    RegraOitava("V", -1).aplicar(caractere("V"), contexto)
    assert contexto.parametros().get_oitava() == 6


def test_regra_instrumento_fixo(contexto):
    RegraInstrumentoFixo("!", BANDONEON).aplicar(caractere("!"), contexto)
    assert contexto.parametros().get_instrumento() == BANDONEON


def test_regra_soma_digito_par(contexto):
    RegraInstrumentoSomaDigito().aplicar(caractere("4"), contexto)
    assert contexto.parametros().get_instrumento() == 10      # 6 (Cravo) + 4


def test_regra_atraso_define_atraso_da_voz(contexto):
    RegraAtraso().aplicar(Token(TipoToken.ATRASO, "[4]", 0, valor=4), contexto)
    assert contexto.voz.get_atraso() == 4


# ---- Regra global -------------------------------------------------------


def test_regra_andamento_registra_mudanca_na_posicao_atual(contexto):
    RegraNota().aplicar(nota("C", Duracao.SEMINIMA), contexto)    # ocupa 1 beat
    RegraAndamento(">", +10).aplicar(caractere(">"), contexto)
    [mudanca] = contexto.partitura.get_mudancas_andamento()
    assert mudanca.posicao_beats == 1.0
    assert mudanca.delta_bpm == 10


# ---- Mapeamento ---------------------------------------------------------


def test_mapeamento_usa_regra_padrao_quando_nenhuma_aceita():
    regra = Mapeamento.padrao().encontrar_regra(caractere("H"))
    assert isinstance(regra, RegraRepetirOuPausar)


def test_mapeamento_aceita_regra_nova_sem_mudar_codigo(contexto):
    """Demonstra o Aberto/Fechado: uma regra nova entra sem mexer no Mapeamento."""

    class RegraArroba(RegraPorCaractere):
        def aplicar(self, token, contexto):
            contexto.parametros().dobrar_volume()

    mapeamento = Mapeamento.padrao()
    mapeamento.adicionar_regra(RegraArroba("@"))
    mapeamento.aplicar(caractere("@"), contexto)
    assert contexto.parametros().get_volume() == 80
