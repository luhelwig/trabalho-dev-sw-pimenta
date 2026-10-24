"""Testes do modelo musical: Duracao, NotaMusical, ParametrosMusica,
ConfiguracaoInicial e Partitura."""

import pytest
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical, Acidente
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CRAVO, FAGOTE, ORGAO_DE_IGREJA, PIANO, CatalogoInstrumentos
from gerador_musical.musica.parametros_musica import ParametrosMusica

# ---- Duracao / NotaMusical ---------------------------------------------


@pytest.mark.parametrize("identificador, esperado", [
    (1, Duracao.SEMIBREVE), (3, Duracao.SEMINIMA), (7, Duracao.SEMIFUSA),
])
def test_duracao_from_identificador(identificador, esperado):
    assert Duracao.from_identificador(identificador) is esperado

@pytest.mark.parametrize("identificador", [0, 8])
def test_identificador_invalido(identificador):
    with pytest.raises(ValueError):
        Duracao.from_identificador(identificador)

def test_cada_duracao_vale_metade_da_anterior():
    figuras = list(Duracao)
    for i in range(len(figuras) - 1):
        assert figuras[i + 1].em_beats() == figuras[i].em_beats() / 2

def test_do_central_e_60():
    """NotaMusical('C').altura_midi(4) == 60."""
    assert NotaMusical("C").altura_midi(4) == 60


def test_la_4_e_69():
    """NotaMusical('A').altura_midi(4) == 69."""
    assert NotaMusical("A").altura_midi(4) == 69


def test_sustenido_sobe_e_bemol_desce_um_semitom():
    assert NotaMusical("C", Acidente.SUSTENIDO).altura_midi(4) == 61
    assert NotaMusical("E", Acidente.BEMOL).altura_midi(4) == 63


# ---- ParametrosMusica ---------------------------------------------------


def test_dobrar_volume():
    """40 -> 80."""
    p = ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=40)
    p.dobrar_volume()
    assert p.get_volume() == 80


def test_dobrar_volume_satura_em_127():
    """100 -> 127."""
    p = ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=100)
    p.dobrar_volume()
    assert p.get_volume() == 127


def test_incrementar_oitava_alem_do_maximo_volta_para_padrao():
    p = ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=100)
    for _ in range(4):
        p.incrementar_oitava()
    assert p.get_oitava() == 8
    p.incrementar_oitava()
    assert p.get_oitava() == 4


def test_decrementar_oitava():
    p = ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=100)
    p.decrementar_oitava()
    assert p.get_oitava() == 3


def test_reset_instrumento_volta_ao_inicial():
    p = ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=100)
    p.set_instrumento(14)
    p.reset_instrumento()
    assert p.get_instrumento() == 0


# ---- ConfiguracaoInicial ----------------------------------------------


def test_padroes_por_voz():
    """V0..V3: oitavas 6,5,4,3; volumes 100,80,60,40; Cravo, Órgão, Piano, Fagote."""
    pytest.skip("TODO")


def test_voz_4_cicla_para_padroes_da_voz_0():
    pytest.skip("TODO")


def test_alteracao_do_usuario_aparece_em_criar_parametros():
    pytest.skip("TODO")


# ---- Partitura ----------------------------------------------------------


def test_bpm_em_acumula_mudancas_anteriores_a_posicao():
    """bpm_inicial 120; +10 em 4 beats; -10 em 8 beats.
    bpm_em(0)=120, bpm_em(5)=130, bpm_em(9)=120."""
    pytest.skip("TODO")


def test_bpm_em_respeita_limites():
    pytest.skip("TODO")


def test_duracao_total_considera_atraso():
    pytest.skip("TODO")
