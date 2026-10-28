"""Tela de carregamento do croqui: escolher um .txt e voltar."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING

from gerador_musical.excecoes import GeradorMusicalErro
from gerador_musical.interface import estilo
from gerador_musical.interface.estilo import Caixa

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaCarregamento(tk.Frame):
    """Frame "upload botton" do Figma: área "buscar arquivo..." + "voltar".

    Ao escolher um .txt válido, o texto vai para o campo da tela principal e
    o usuário volta para ela.
    """

    LARGURA, ALTURA = 813, 527

    def __init__(self, app: App) -> None:
        """Cria a tela, ainda sem widgets (eles nascem em construir()).

        Args:
            app: janela principal.
        """
        super().__init__(app, bg=estilo.FUNDO)
        self.app: App = app
        self.desenho: estilo.Desenho | None = None

    def construir(self) -> None:
        """Desenha o cartão, a área "buscar arquivo..." e o botão "voltar"."""
        d = self.desenho = estilo.Desenho(self, self.LARGURA, self.ALTURA)
        d.pack()
        d.retangulo(Caixa(25, 19, 764, 486), estilo.CARTAO, raio=57)
        d.texto(407, 19, "gerador de música", estilo.ESTILO_TITULO)
        d.texto(50, 167, "upload:")
        d.retangulo(Caixa(50, 232, 715, 249), estilo.PAINEL, raio=25)

        tag = d.nova_tag()                       # nuvem + texto: um clique só
        d.retangulo(Caixa(70, 262, 500, 120), estilo.PAINEL, tags=tag)
        d.icone("nuvem", Caixa(88, 275, 96, 93), estilo.FUNDO, tags=tag)
        d.texto(208, 287, "buscar arquivo...", estilo.ESTILO_SECUNDARIO, tags=tag)
        d.tornar_clicavel(tag, self._ao_procurar_arquivo)

        d.botao(Caixa(599, 393, 153, 76), "voltar", self._ao_voltar)

    def _ao_procurar_arquivo(self) -> None:
        """Clique em "buscar arquivo...": abre o diálogo e carrega o .txt escolhido."""
        nome = filedialog.askopenfilename(filetypes=[("Texto", "*.txt")])
        if not nome:                            # usuário cancelou
            return
        self.carregar(Path(nome))

    def carregar(self, caminho: Path) -> None:
        """Carrega o arquivo e entrega o texto à tela principal.

        Separado do diálogo para poder ser testado sem abrir janela. Em erro,
        mostra a mensagem e continua nesta tela.

        Args:
            caminho: arquivo .txt escolhido.
        """
        try:
            texto = self.app.controlador.carregar_arquivo(caminho)
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.tela("principal").set_texto(texto)
        self._ao_voltar()

    def _ao_voltar(self) -> None:
        """Volta para a tela principal."""
        self.app.mostrar_tela("principal")
