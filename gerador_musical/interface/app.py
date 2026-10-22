"""Janela raiz e navegação entre as telas do croqui."""

import tkinter as tk

from gerador_musical.aplicacao.controlador import ControladorAplicacao


class App(tk.Tk):
    """Mantém as três telas empilhadas e mostra uma de cada vez.

    Telas (croqui): "principal", "carregamento", "reproducao".
    """

    TITULO = "Gerador de Música a partir de Texto"

    def __init__(self, controlador: ControladorAplicacao) -> None:
        super().__init__()
        self.controlador: ControladorAplicacao = controlador
        self._telas: dict[str, tk.Frame] = {}

    def construir(self) -> None:
        """Cria as telas (TelaPrincipal, TelaCarregamento, TelaReproducao),
        posiciona todas no mesmo lugar (grid) e mostra a principal."""
        raise NotImplementedError

    def mostrar_tela(self, nome: str) -> None:
        """Traz a tela `nome` para frente (tkraise)."""
        raise NotImplementedError

    def tela(self, nome: str) -> tk.Frame:
        """Acesso a uma tela (ex.: carregamento entrega o texto à principal)."""
        raise NotImplementedError

    def mostrar_erro(self, mensagem: str) -> None:
        """messagebox.showerror — usado para "texto vazio", "formato incorreto"..."""
        raise NotImplementedError

    def mostrar_info(self, mensagem: str) -> None:
        raise NotImplementedError
