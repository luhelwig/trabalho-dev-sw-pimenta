"""Janela raiz e navegação entre as telas do croqui."""

import tkinter as tk
from tkinter import messagebox
from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.interface import estilo
from gerador_musical.interface.tela_carregamento import TelaCarregamento
from gerador_musical.interface.tela_principal import TelaPrincipal
from gerador_musical.interface.tela_reproducao import TelaReproducao

class App(tk.Tk):
    """Guarda as três telas e mostra uma de cada vez.

    Telas (croqui): "principal", "carregamento", "reproducao".
    """

    TITULO = "Gerador de Música a partir de Texto"

    def __init__(self, controlador: ControladorAplicacao) -> None:
        estilo.preparar_sistema()        # antes de criar a janela (fonte e nitidez no Windows)
        super().__init__()
        estilo.preparar(self)            # escolhe a fonte e calcula a escala
        self.controlador: ControladorAplicacao = controlador
        self._telas: dict[str, tk.Frame] = {}

    def construir(self) -> None:
        """Cria as telas (TelaPrincipal, TelaCarregamento, TelaReproducao)
        no mesmo lugar (grid) e mostra a principal."""
        self.title(self.TITULO)
        self.configure(bg=estilo.FUNDO)
        self.resizable(False, False)     # o layout segue as medidas do Figma
        for nome, Tela in (("principal", TelaPrincipal), ("carregamento", TelaCarregamento),
                           ("reproducao", TelaReproducao)):
            tela = Tela(self)
            tela.grid(row=0, column=0)
            tela.construir()
            self._telas[nome] = tela
        self.mostrar_tela("principal")

    def mostrar_tela(self, nome: str) -> None:
        """Mostra só a tela `nome`. A janela assume o tamanho dela, como no
        Figma (cada frame tem uma altura)."""
        for tela in self._telas.values():
            tela.grid_remove()
        self._telas[nome].grid()

    def tela(self, nome: str) -> tk.Frame:
        """Acesso a uma tela (ex.: carregamento entrega o texto à principal)."""
        return self._telas[nome]

    def mostrar_erro(self, mensagem: str) -> None:
        """messagebox.showerror — usado para "texto vazio", "formato incorreto"..."""
        messagebox.showerror("Erro", mensagem)

    def mostrar_info(self, mensagem: str) -> None:
        messagebox.showinfo(self.TITULO, mensagem)
