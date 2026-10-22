"""Classe EntradaUsuario (Fase 1, estendida na Fase 2)."""

from pathlib import Path

from gerador_musical.entrada.arquivo_texto import ArquivoTexto


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
        raise NotImplementedError

    def set_conteudo(self, texto: str) -> None:
        """Atualiza o texto (chamado quando o usuário edita o campo)."""
        raise NotImplementedError

    def esta_vazio(self) -> bool:
        """True se o conteúdo é vazio ou só tem espaços/quebras de linha."""
        raise NotImplementedError

    def eh_formato_valido(self) -> bool:
        """True se todos os caracteres pertencem ao alfabeto aceito.

        Requisito: mostrar "formato incorreto" para caracteres de outros
        alfabetos. TODO (decisão do grupo): definir o alfabeto aceito
        (ex.: ASCII imprimível + acentos do português + '\\n').
        """
        raise NotImplementedError

    def carregar_arquivo(self, caminho: Path) -> None:
        """Lê o .txt (via ArquivoTexto), põe no conteúdo e guarda o caminho."""
        raise NotImplementedError

    # ---- NOVO (Fase 2) --------------------------------------------------

    def salvar_arquivo(self, caminho: Path | None = None) -> Path:
        """Grava o conteúdo atual.

        Sem `caminho`, sobrescreve o arquivo de origem (Mudança 1).
        Devolve o caminho efetivamente gravado.

        Raises:
            ArquivoInvalidoErro: sem caminho e o texto não veio de arquivo.
        """
        raise NotImplementedError

    def foi_modificado(self) -> bool:
        """True se o conteúdo mudou desde o último carregar/salvar."""
        raise NotImplementedError

    def veio_de_arquivo(self) -> bool:
        raise NotImplementedError

    def limpar(self) -> None:
        """Esvazia o conteúdo e esquece o arquivo de origem (nova composição)."""
        raise NotImplementedError
