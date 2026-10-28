"""Tela principal do croqui: texto + configurações + gerar/limpar."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING

from gerador_musical.excecoes import GeradorMusicalErro
from gerador_musical.interface import estilo
from gerador_musical.interface.estilo import Caixa
from gerador_musical.interface.painel_configuracoes import PainelConfiguracoes

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaPrincipal(tk.Frame):
    """Frame "Pagina inicial" do Figma. Medidas em px do Figma (ver estilo.py).

    Layout: botão de upload (canto superior esquerdo), campo de texto (cada
    linha é uma voz), painel de configurações e os botões "gerar música" e
    "limpar".

    NOVO na Fase 2, no mesmo estilo: abas de voz v0–v3 no painel e a pílula
    "salvar texto" ao lado de "texto de entrada:" (Mudança 1).

    Fase 3: o painel de configurações virou a classe PainelConfiguracoes
    (bad smell "Classe Grande"); esta tela cuida do texto e dos botões.

    Attributes:
        campo_texto: campo onde o usuário digita.
        painel: painel de configurações (voz, volume, bpm, instrumento, oitava).
    """

    LARGURA, ALTURA = 813, 1232   # frame do Figma (1157) + 75 px da linha "voz:"

    def __init__(self, app: App) -> None:
        """Cria a tela, ainda sem widgets (eles nascem em construir()).

        Args:
            app: janela principal.
        """
        super().__init__(app, bg=estilo.FUNDO)
        self.app: App = app
        self.desenho: estilo.Desenho | None = None
        self.campo_texto: tk.Text | None = None
        self.painel: PainelConfiguracoes | None = None
        self._texto_gerado: str | None = None   # texto da última geração

    def construir(self) -> None:
        """Desenha a tela inteira: cabeçalho, campo de texto, painel e botões."""
        self.desenho = estilo.Desenho(self, self.LARGURA, self.ALTURA)
        self.desenho.pack()
        self._construir_cabecalho()
        self._construir_campo_texto()
        self.painel = PainelConfiguracoes(self.desenho, self.app.controlador_configuracao)
        self.painel.construir()
        self._construir_botoes()

    # ---- Construção -----------------------------------------------------

    def _construir_cabecalho(self) -> None:
        """Cartão azul-claro, botão redondo de upload e título."""
        d = self.desenho
        d.retangulo(Caixa(24, 21, 764, self.ALTURA - 57), estilo.CARTAO, raio=57)
        tag = d.nova_tag()
        d.circulo(Caixa(52, 51, 70, 70), estilo.PAINEL, tags=tag)
        d.icone("upload", Caixa(66, 64, 42, 43), estilo.VERMELHO, tags=tag)
        d.tornar_clicavel(tag, self._ao_abrir_carregamento)
        d.texto(406, 21, "gerador de música", estilo.ESTILO_TITULO)

    def _construir_campo_texto(self) -> None:
        """Rótulo, pílula "salvar texto" e o campo de texto com a dica "digite aqui...".

        O campo usa wrap="none" (cada linha é uma voz e não pode quebrar sozinha)
        e undo=True (Ctrl+Z).
        """
        d = self.desenho
        d.texto(55, 153, "texto de entrada:")
        d.botao(Caixa(479, 162, 288, 47), "salvar texto", self._ao_salvar_texto, cor=estilo.FUNDO, raio=23)

        d.retangulo(Caixa(52, 221, 715, 223), estilo.PAINEL, raio=25)
        self.campo_texto = tk.Text(
            d, wrap="none", undo=True, bd=0, highlightthickness=0, font=estilo.fonte(46),
            bg=estilo.PAINEL, fg=estilo.ESCURO, insertbackground=estilo.ESCURO,
            selectbackground=estilo.FUNDO, selectforeground=estilo.PAINEL,
        )
        d.widget(Caixa(66, 231, 687, 203), self.campo_texto)

        # "digite aqui..." aparece no canto de baixo enquanto o campo está vazio
        self.dica = tk.Label(self.campo_texto, text="digite aqui...", bd=0, font=estilo.fonte(),
                             bg=estilo.PAINEL, fg=estilo.FUNDO, cursor="xterm")
        self.dica.bind("<Button-1>", lambda evento: self.campo_texto.focus_set())
        self.campo_texto.bind("<<Modified>>", self._ao_modificar_texto)
        self._atualizar_dica()

    def _construir_botoes(self) -> None:
        """Botões "gerar música" e "limpar", fixos embaixo."""
        d = self.desenho
        d.botao(Caixa(66, 1077, 307, 76), "gerar música", self._ao_gerar)
        d.botao(Caixa(594, 1077, 158, 76), "limpar", self._ao_limpar)

    # ---- Eventos --------------------------------------------------------

    def _ao_abrir_carregamento(self) -> None:
        """Clique no botão de upload: mostra a tela de carregamento."""
        self.app.mostrar_tela("carregamento")

    def _ao_gerar(self) -> None:
        """Clique em "gerar música": gera e, se der certo, vai para a reprodução.

        Se o texto é o mesmo da última geração, só os parâmetros mudaram: regera
        sem reinterpretar o texto (requisito). Em GeradorMusicalErro, mostra a
        mensagem e continua nesta tela.
        """
        texto = self.get_texto()
        try:
            if texto == self._texto_gerado and self.app.controlador.musica_foi_gerada():
                self.app.controlador.regerar_com_novos_parametros()
            else:
                self.app.controlador.atualizar_texto(texto)
                self.app.controlador.gerar_musica()
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        self._texto_gerado = texto
        self.app.mostrar_tela("reproducao")

    def _ao_limpar(self) -> None:
        """Clique em "limpar": esvazia o campo e o texto guardado no controlador."""
        self.app.controlador.limpar()
        self.set_texto("")
        self._texto_gerado = None

    def _ao_salvar_texto(self) -> None:
        """Clique em "salvar texto".

        Se o texto veio de um arquivo, salva por cima dele; senão, abre o
        diálogo "salvar como". Mostra onde salvou ou o erro.
        """
        self.app.controlador.atualizar_texto(self.get_texto())
        try:
            if self.app.controlador.texto_veio_de_arquivo():
                caminho = self.app.controlador.salvar_texto()
            else:
                nome = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt")])
                if not nome:                    # usuário cancelou
                    return
                caminho = self.app.controlador.salvar_texto(Path(nome))
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.mostrar_info(f"Texto salvo em {caminho}")

    def _ao_modificar_texto(self, evento: tk.Event) -> None:
        """Evento <<Modified>> do campo: rearma o evento e atualiza a dica.

        Args:
            evento: evento do tkinter (não usado).
        """
        self.campo_texto.edit_modified(False)   # rearma o evento <<Modified>>
        self._atualizar_dica()

    def _atualizar_dica(self) -> None:
        """Mostra "digite aqui..." só quando o campo está vazio."""
        if self.get_texto():
            self.dica.place_forget()
        else:
            self.dica.place(relx=0, rely=1, anchor="sw")

    # ---- Usado por outras telas -----------------------------------------

    def set_texto(self, texto: str) -> None:
        """Troca todo o conteúdo do campo (chamado após carregar um .txt).

        Args:
            texto: novo conteúdo.
        """
        self.campo_texto.delete("1.0", "end")
        self.campo_texto.insert("1.0", texto)

    def get_texto(self) -> str:
        """Devolve o conteúdo do campo, sem a quebra de linha extra do tkinter."""
        return self.campo_texto.get("1.0", "end-1c")   # "end" traria um \n a mais
