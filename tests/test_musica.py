"""Testes do modelo musical.

Cobre Duracao, NotaMusical, ParametrosMusica, ConfiguracaoInicial,
Partitura e CatalogoInstrumentos.
"""

import pytest
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import NotaMusical, Acidente
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CRAVO, FAGOTE, ORGAO_DE_IGREJA, PIANO, CatalogoInstrumentos
from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.evento_musical import EventoMusical
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz
from gerador_musical.musica import instrumentos


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


def test_somar_ao_instrumento_passa_de_127_e_recomeca_do_0():
    p = ParametrosMusica(instrumento_inicial=126, oitava_padrao=4, volume_padrao=100)
    p.somar_ao_instrumento(4)
    assert p.get_instrumento() == 2


# ---- ConfiguracaoInicial ----------------------------------------------


def test_padroes_por_voz():
    c = ConfiguracaoInicial.padrao()
    assert [c.get_oitava_inicial(i) for i in range(4)] == [6, 5, 4, 3]
    assert [c.get_volume_inicial(i) for i in range(4)] == [100, 80, 60, 40]
    assert [c.get_instrumento_inicial(i) for i in range(4)] == [
        instrumentos.CRAVO,
        instrumentos.ORGAO_DE_IGREJA,
        instrumentos.PIANO,
        instrumentos.FAGOTE,
    ]


def test_voz_4_cicla_para_padroes_da_voz_0():
    c = ConfiguracaoInicial.padrao()
    assert c.get_oitava_inicial(4) == c.get_oitava_inicial(0)
    assert c.get_volume_inicial(4) == c.get_volume_inicial(0)
    assert c.get_instrumento_inicial(4) == c.get_instrumento_inicial(0)


def test_alteracao_do_usuario_aparece_em_criar_parametros():
    c = ConfiguracaoInicial.padrao()
    c.set_instrumento_inicial(1, 40)
    assert c.criar_parametros(1).get_instrumento() == 40


# ---- Partitura ----------------------------------------------------------


def test_bpm_em_acumula_mudancas_anteriores_a_posicao():
    """bpm_inicial 120; +10 em 4 beats; -10 em 8 beats.
    bpm_em(0)=120, bpm_em(5)=130, bpm_em(9)=120."""
    p = Partitura(bpm_inicial=120)
    p.registrar_mudanca_andamento(8, -10)  # fora de ordem de propósito
    p.registrar_mudanca_andamento(4, +10)
    assert p.bpm_em(0) == 120
    assert p.bpm_em(5) == 130
    assert p.bpm_em(9) == 120


def test_catalogo_tem_pelo_menos_25():
    assert len(CatalogoInstrumentos.padrao().listar()) >= 25


def test_catalogo_tem_os_obrigatorios():
    catalogo = CatalogoInstrumentos.padrao()
    obrigatorios = [
        instrumentos.PIANO,
        instrumentos.CRAVO,
        instrumentos.TUBULAR_BELLS,
        instrumentos.ORGAO_DE_IGREJA,
        instrumentos.BANDONEON,
        instrumentos.CORDAS,
        instrumentos.FAGOTE,
        instrumentos.GAITA_DE_FOLES,
        instrumentos.AGOGO,
    ]
    for programa in obrigatorios:
        assert catalogo.contem(programa)


def test_bpm_em_respeita_limites():
    p = Partitura(bpm_inicial=295)
    p.registrar_mudanca_andamento(1, +10)
    p.registrar_mudanca_andamento(2, +10)
    assert p.bpm_em(3) == 300


def test_duracao_total_considera_atraso():
    # Supõe semínima = 1 beat: atraso de 4 + uma semínima = 5 beats.
    voz = Voz(0, ParametrosMusica(instrumento_inicial=0, oitava_padrao=4, volume_padrao=100))
    voz.set_atraso(4)
    voz.adicionar_evento(EventoMusical.criar_pausa(Duracao.SEMINIMA))
    partitura = Partitura(bpm_inicial=120)
    partitura.adicionar_voz(voz)
    assert partitura.duracao_total_beats() == 5
