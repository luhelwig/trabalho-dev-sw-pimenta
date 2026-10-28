"""Testes de integração do Parser (Tokenizador + Mapeamento reais)."""

from gerador_musical.interpretacao.parser import Parser
from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial

def criar_parser(configuracao=None):
    """Cria um Parser com as peças reais e a configuração dada (ou a padrão)."""
    configuracao = configuracao or ConfiguracaoInicial.padrao()
    return Parser(Tokenizador(), Mapeamento.padrao(), configuracao)

def test_cada_linha_vira_uma_voz():
    """"A:3\\nC:3\\nE:3\\nG:3" -> 4 vozes, V0..V3."""
    partitura = criar_parser().interpretar("A:3\nC:3\nE:3\nG:3")
    assert partitura.numero_de_vozes() == 4
    assert [voz.indice for voz in partitura.get_vozes()] == [0, 1, 2, 3]


def test_vozes_comecam_com_parametros_padrao():
    partitura = criar_parser().interpretar("A:3\nA:3")
    evento_da_voz_1 = partitura.get_vozes()[1].get_eventos()[0]
    assert evento_da_voz_1.oitava == 5
    assert evento_da_voz_1.volume == 80


def test_atraso_de_entrada():
    """"[4] C:2 D:2 E:3" -> voz com atraso 4 beats e 3 notas."""
    voz = criar_parser().interpretar("[4] C:2 D:2 E:3").get_vozes()[0]
    notas = [evento for evento in voz.get_eventos() if evento.eh_nota()]
    assert voz.get_atraso() == 4
    assert len(notas) == 3


def test_andamento_vale_para_todas_as_vozes():
    partitura = criar_parser().interpretar("A:3 >\nC:1")
    assert partitura.bpm_em(2) == partitura.get_bpm_inicial() + 10

def test_nota_anterior_nao_atravessa_linhas():
    """"A:3\\nH" -> na voz 1, H é pausa (não repete o Lá da voz 0)."""
    [evento] = criar_parser().interpretar("A:3\nH").get_vozes()[1].get_eventos()
    assert evento.eh_pausa()


def test_regerar_com_nova_configuracao_sem_retokenizar():
    """Muda o instrumento de V0 na ConfiguracaoInicial e chama só
    token_to_partitura: as notas de V0 saem com o novo instrumento."""
    configuracao = ConfiguracaoInicial.padrao()
    parser = criar_parser(configuracao)
    parser.interpretar("A:3")
    configuracao.set_instrumento_inicial(0, 40)
    partitura = parser.token_to_partitura()  # sem reler o texto
    assert partitura.get_vozes()[0].get_eventos()[0].instrumento == 40


def test_texto_com_caracteres_inesperados_nao_quebra():
    partitura = criar_parser().interpretar("A:3 @#$%&*()[]{}~^ ção 日本")
    assert partitura.numero_de_vozes() == 1
