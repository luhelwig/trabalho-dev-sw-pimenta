"""Janela raiz e navegação entre as telas do croqui."""

import tkinter as tk
from tkinter import messagebox
from gerador_musical.aplicacao.controlador import ControladorAplicacao
from gerador_musical.aplicacao.controlador_configuracao import ControladorConfiguracao
from gerador_musical.interface import estilo
from gerador_musical.interface.tela_carregamento import TelaCarregamento
from gerador_musical.interface.tela_principal import TelaPrincipal
from gerador_musical.interface.tela_reproducao import TelaReproducao

class App(tk.Tk):
    """Janela principal: guarda as três telas e mostra uma de cada vez.

    Telas (croqui): "principal", "carregamento", "reproducao".

    Attributes:
        controlador: fachada do fluxo da música (texto, geração, reprodução).
        controlador_configuracao: fachada das configurações iniciais (painel).
    """

    TITULO = "Gerador de Música a partir de Texto"

    def __init__(self, controlador: ControladorAplicacao,
                 controlador_configuracao: ControladorConfiguracao) -> None:
        """Prepara o tema, cria a janela e guarda os controladores.

        Args:
            controlador: fachada do fluxo da música.
            controlador_configuracao: fachada das configurações iniciais.
        """
        estilo.preparar_sistema()        # antes de criar a janela (fonte e nitidez no Windows)
        super().__init__()
        estilo.preparar(self)            # escolhe a fonte e calcula a escala
        self.controlador: ControladorAplicacao = controlador
        self.controlador_configuracao: ControladorConfiguracao = controlador_configuracao
        self._telas: dict[str, tk.Frame] = {}

    def construir(self) -> None:
        """Cria as três telas no mesmo lugar (grid) e mostra a principal.

        A janela tem tamanho fixo, porque o layout segue as medidas do Figma.
        """
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
        """Mostra só a tela `nome`; a janela assume o tamanho dela.

        Args:
            nome: "principal", "carregamento" ou "reproducao".
        """
        for tela in self._telas.values():
            tela.grid_remove()
        self._telas[nome].grid()

    def tela(self, nome: str) -> tk.Frame:
        """Dá acesso a uma tela (ex.: o carregamento entrega o texto à principal).

        Args:
            nome: nome da tela.

        Returns:
            O Frame da tela.
        """
        return self._telas[nome]

    def mostrar_erro(self, mensagem: str) -> None:
        """Mostra uma caixa de erro (ex.: "texto vazio", "formato incorreto").

        Args:
            mensagem: texto da mensagem.
        """
        messagebox.showerror("Erro", mensagem)

    def mostrar_info(self, mensagem: str) -> None:
        """Mostra uma caixa de informação (ex.: onde o arquivo foi salvo).

        Args:
            mensagem: texto da mensagem.
        """
        messagebox.showinfo(self.TITULO, mensagem)
