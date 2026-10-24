"""Classe EntradaUsuario (Fase 1, estendida na Fase 2)."""

from pathlib import Path

from gerador_musical.entrada.arquivo_texto import ArquivoTexto
import string
from gerador_musical.excecoes import ArquivoInvalidoErro

ACENTOS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
ALFABETO_ACEITO = frozenset(string.printable + ACENTOS)

class EntradaUsuario:
    """Guarda o texto que o usuário digitou ou carregou de um .txt.

    Fase 2 (Mudança 1): o texto pode vir do teclado, de um arquivo, ou
    dos dois (carregar e depois editar). Se veio de arquivo e foi editado,
    deve ser possível salvar por cima do original.
    """

    def __init__(self, arquivo_texto: ArquivoTexto | None = None) -> None:
        self.conteudo: str = ""
        # NOVO: lembra de onde o texto veio, para "salvar" sobrescrever o original.
        self.caminho_arquivo: Path | None = None
        self._conteudo_original: str = ""
        self._arquivo_texto: ArquivoTexto = arquivo_texto or ArquivoTexto()

    # ---- Fase 1 ---------------------------------------------------------

    def get_conteudo(self) -> str:
        return self.conteudo

    def set_conteudo(self, texto: str) -> None:
        """Atualiza o texto (chamado quando o usuário edita o campo)."""
        self.conteudo = texto

    def esta_vazio(self) -> bool:
        """True se o conteúdo é vazio ou só tem espaços/quebras de linha."""
        return not self.conteudo.strip()

    def eh_formato_valido(self) -> bool:
        """True se todos os caracteres pertencem ao alfabeto aceito.

        Requisito: mostrar "formato incorreto" para caracteres de outros
        alfabetos. TODO (decisão do grupo): definir o alfabeto aceito
        (ex.: ASCII imprimível + acentos do português + '\\n').
        """
        return all(c in ALFABETO_ACEITO for c in self.conteudo)

    def carregar_arquivo(self, caminho: Path) -> None:
        """Lê o .txt (via ArquivoTexto), põe no conteúdo e guarda o caminho."""
        texto = self._arquivo_texto.ler(caminho)
        self.conteudo = texto
        self._conteudo_original = texto
        self.caminho_arquivo = caminho

    # ---- NOVO (Fase 2) --------------------------------------------------

    def salvar_arquivo(self, caminho: Path | None = None) -> Path:
        """Grava o conteúdo atual.

        Sem `caminho`, sobrescreve o arquivo de origem (Mudança 1).
        Devolve o caminho efetivamente gravado.

        Raises:
            ArquivoInvalidoErro: sem caminho e o texto não veio de arquivo.
        """
        destino = caminho or self.caminho_arquivo
        if destino is None:
            raise ArquivoInvalidoErro("O texto não veio de um arquivo: escolha onde salvar.")
        self._arquivo_texto.salvar(destino, self.conteudo)
        self.caminho_arquivo = destino
        self._conteudo_original = self.conteudo
        return destino

    def foi_modificado(self) -> bool:
        """True se o conteúdo mudou desde o último carregar/salvar."""
        return self.conteudo != self._conteudo_original

    def veio_de_arquivo(self) -> bool:
        return self.caminho_arquivo is not None

    def limpar(self) -> None:
        """Esvazia o conteúdo e esquece o arquivo de origem (nova composição)."""
        self.conteudo = ""
        self._conteudo_original = ""
        self.caminho_arquivo = None
