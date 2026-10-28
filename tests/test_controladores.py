"""Testes dos dois controladores (fachadas usadas pela interface).

NOVO na Fase 3: depois de separar o ControladorConfiguracao do
ControladorAplicacao, estes testes garantem que nada mudou para as telas.
Usam o backend falso do tests/conftest.py, então rodam sem som.
"""

import mido
import pytest

from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.aplicacao.controlador_configuracao import ControladorConfiguracao
from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.excecoes import FormatoInvalidoErro, MusicaNaoGeradaErro, TextoVazioErro
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CatalogoInstrumentos
from gerador_musical.saida.exportador import ExportadorMidi
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador


@pytest.fixture
def configuracao():
    """ConfiguracaoInicial padrão, compartilhada pelos dois controladores."""
    return ConfiguracaoInicial.padrao()


@pytest.fixture
def controlador(configuracao, backend, tmp_path):
    """ControladorAplicacao montado como no main, mas com backend falso e pasta temporária."""
    parser = Parser(Tokenizador(), Mapeamento.padrao(), configuracao)
    return ControladorAplicacao(
        entrada=EntradaUsuario(), parser=parser, sintetizador=Sintetizador(),
        player=Player(backend), exportador=ExportadorMidi(tmp_path),
    )


@pytest.fixture
def controlador_configuracao(configuracao):
    """ControladorConfiguracao com o catálogo padrão."""
    return ControladorConfiguracao(configuracao, CatalogoInstrumentos.padrao())


# ---- ControladorConfiguracao ------------------------------------------


def test_configuracao_lista_os_instrumentos_do_catalogo(controlador_configuracao):
    assert len(controlador_configuracao.listar_instrumentos()) == 30


def test_configuracao_altera_os_valores_da_voz(controlador_configuracao, configuracao):
    controlador_configuracao.set_bpm(140)
    controlador_configuracao.set_volume_voz(1, 90)
    controlador_configuracao.set_oitava_voz(1, 6)
    controlador_configuracao.set_instrumento_voz(1, 40)
    assert configuracao.get_bpm_inicial() == 140
    assert controlador_configuracao.get_volume_voz(1) == 90
    assert controlador_configuracao.get_oitava_voz(1) == 6
    assert controlador_configuracao.get_instrumento_voz(1) == 40


@pytest.mark.parametrize("alteracao", [
    lambda c: c.set_bpm(1000),
    lambda c: c.set_volume_voz(0, 200),
    lambda c: c.set_oitava_voz(0, 9),
    lambda c: c.set_instrumento_voz(0, 128),
])
def test_configuracao_fora_do_limite_gera_value_error(controlador_configuracao, alteracao):
    with pytest.raises(ValueError):
        alteracao(controlador_configuracao)


# ---- ControladorAplicacao ---------------------------------------------


def test_texto_vazio_gera_erro(controlador):
    controlador.atualizar_texto("   ")
    with pytest.raises(TextoVazioErro):
        controlador.gerar_musica()


def test_caracteres_de_outro_alfabeto_geram_formato_incorreto(controlador):
    controlador.atualizar_texto("Привет")
    with pytest.raises(FormatoInvalidoErro):
        controlador.gerar_musica()


def test_exportar_sem_gerar_gera_erro(controlador):
    with pytest.raises(MusicaNaoGeradaErro):
        controlador.exportar_midi()


def test_gerar_tocar_e_exportar(controlador, backend, tmp_path):
    controlador.atualizar_texto("C:1D:1E:1")
    controlador.gerar_musica()
    controlador.tocar()
    caminho = controlador.exportar_midi()
    assert controlador.musica_foi_gerada()
    assert backend.chamadas[-1] == "tocar"
    assert caminho.parent == tmp_path and caminho.exists()


def test_regerar_usa_a_configuracao_nova(controlador, controlador_configuracao):
    """O que o painel muda vale ao regerar, sem reinterpretar o texto."""
    controlador.atualizar_texto("C:1D:1")
    controlador.gerar_musica()
    controlador_configuracao.set_bpm(200)
    controlador.regerar_com_novos_parametros()
    midi = mido.MidiFile(controlador.exportar_midi())
    assert midi.tracks[0][0].tempo == mido.bpm2tempo(200)


def test_limpar_para_a_musica_e_esquece_o_texto(controlador, backend):
    controlador.atualizar_texto("C:1")
    controlador.gerar_musica()
    controlador.limpar()
    assert not controlador.musica_foi_gerada()
    assert backend.chamadas[-1] == "parar"
