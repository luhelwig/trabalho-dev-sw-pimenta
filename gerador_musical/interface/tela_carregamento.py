"""Tela de carregamento do croqui: escolher um .txt e voltar."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaCarregamento(tk.Frame):
    """Layout minimalista: área de busca de arquivo + botão "voltar".

    Ao escolher um .txt válido, o texto vai para o campo da tela principal
    e o usuário volta para ela.
    """

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self.app: App = app

    def construir(self) -> None:
        raise NotImplementedError

    def _ao_procurar_arquivo(self) -> None:
        """filedialog.askopenfilename(filetypes=[("Texto", "*.txt")]),
        controlador.carregar_arquivo, tela principal.set_texto, voltar."""
        raise NotImplementedError

    def _ao_voltar(self) -> None:
        raise NotImplementedError
