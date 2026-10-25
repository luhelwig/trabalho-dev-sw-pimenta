"""Tela de carregamento do croqui: escolher um .txt e voltar."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING

from gerador_musical.excecoes import GeradorMusicalErro
from gerador_musical.interface import estilo

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaCarregamento(tk.Frame):
    """Frame "upload botton" do Figma: área "buscar arquivo..." + "voltar".

    Ao escolher um .txt válido, o texto vai para o campo da tela principal
    e o usuário volta para ela.
    """

    LARGURA, ALTURA = 813, 527

    def __init__(self, app: App) -> None:
        super().__init__(app, bg=estilo.FUNDO)
        self.app: App = app
        self.desenho: estilo.Desenho | None = None

    def construir(self) -> None:
        d = self.desenho = estilo.Desenho(self, self.LARGURA, self.ALTURA)
        d.pack()
        d.retangulo(25, 19, 764, 486, 57, estilo.CARTAO)
        d.texto(407, 19, "gerador de música", estilo.TITULO, ancora="n")
        d.texto(50, 167, "upload:")
        d.retangulo(50, 232, 715, 249, 25, estilo.PAINEL)

        tag = d.nova_tag()                       # nuvem + texto: um clique só
        d.retangulo(70, 262, 500, 120, 0, estilo.PAINEL, tags=tag)
        d.icone("nuvem", 88, 275, 96, 93, estilo.FUNDO, tags=tag)
        d.texto(208, 287, "buscar arquivo...", cor=estilo.FUNDO, tags=tag)
        d.tornar_clicavel(tag, self._ao_procurar_arquivo)

        d.botao(599, 393, 153, 76, "voltar", self._ao_voltar)

    def _ao_procurar_arquivo(self) -> None:
        nome = filedialog.askopenfilename(filetypes=[("Texto", "*.txt")])
        if not nome:                            # usuário cancelou
            return
        self.carregar(Path(nome))

    def carregar(self, caminho: Path) -> None:
        """Carrega o arquivo e entrega o texto à tela principal.
        Separado do diálogo para poder ser testado sem abrir janela."""
        try:
            texto = self.app.controlador.carregar_arquivo(caminho)
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.tela("principal").set_texto(texto)
        self._ao_voltar()

    def _ao_voltar(self) -> None:
        self.app.mostrar_tela("principal")
