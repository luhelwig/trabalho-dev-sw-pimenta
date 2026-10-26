"""Testes de EntradaUsuario e ArquivoTexto (usa a fixture tmp_path do pytest)."""

import pytest
from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.excecoes import ArquivoInvalidoErro


def test_texto_so_com_espacos_esta_vazio():
    entrada = EntradaUsuario()
    entrada.set_conteudo("  \n ")
    assert entrada.esta_vazio()


def test_caracteres_de_outro_alfabeto_sao_formato_invalido():
    """Ex.: "A:3 Ж" ou "C:2 日" -> eh_formato_valido() == False."""
    entrada = EntradaUsuario()
    entrada.set_conteudo("A:3 Ж")  # letra do alfabeto cirílico
    assert entrada.eh_formato_valido() is False


def test_acentos_do_portugues_sao_validos():
    entrada = EntradaUsuario()
    entrada.set_conteudo("Canção de ninar")
    assert entrada.eh_formato_valido() is True


def test_carregar_arquivo_preenche_conteudo(tmp_path):
    arquivo = tmp_path / "musica.txt"
    arquivo.write_text("A:3", encoding="utf-8")
    entrada = EntradaUsuario()
    entrada.carregar_arquivo(arquivo)
    assert entrada.get_conteudo() == "A:3"
    assert entrada.veio_de_arquivo()


def test_carregar_arquivo_que_nao_e_txt_gera_erro(tmp_path):
    arquivo = tmp_path / "musica.mid"
    arquivo.write_text("x")
    with pytest.raises(ArquivoInvalidoErro):
        EntradaUsuario().carregar_arquivo(arquivo)


def test_salvar_sem_caminho_sobrescreve_original(tmp_path):
    arquivo = tmp_path / "musica.txt"
    arquivo.write_text("A:3", encoding="utf-8")
    entrada = EntradaUsuario()
    entrada.carregar_arquivo(arquivo)
    entrada.set_conteudo("C:2")
    entrada.salvar_arquivo()
    assert arquivo.read_text(encoding="utf-8") == "C:2"


def test_salvar_sem_caminho_e_sem_origem_gera_erro():
    entrada = EntradaUsuario()
    entrada.set_conteudo("A:3")  # digitado, não veio de arquivo
    with pytest.raises(ArquivoInvalidoErro):
        entrada.salvar_arquivo()


def test_foi_modificado():
    entrada = EntradaUsuario()
    entrada.set_conteudo("A")
    assert entrada.foi_modificado()
    entrada.limpar()
    assert not entrada.foi_modificado()
