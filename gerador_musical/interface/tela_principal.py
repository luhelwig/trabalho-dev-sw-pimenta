"""Tela principal do croqui: texto + configurações + gerar/limpar."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING

from gerador_musical.excecoes import GeradorMusicalErro
from gerador_musical.interface import estilo

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaPrincipal(tk.Frame):
    """Frame "Pagina inicial" do Figma. Medidas em px do Figma (ver estilo.py).

    Layout: botão de upload (canto superior esquerdo), campo de texto (cada
    linha é uma voz), painel de configurações (volume, bpm, instrumento,
    oitava) e os botões "gerar música" e "limpar".

    NOVO na Fase 2, no mesmo estilo:
      - abas de voz v0–v3 no topo do painel: volume, instrumento e oitava
        valem para a voz selecionada (o bpm vale para a música toda);
      - pílula "salvar texto" ao lado de "texto de entrada:" (Mudança 1).

    Attributes:
        voz_selecionada: número da voz cujos valores aparecem nos controles.
        campo_texto: campo onde o usuário digita.
    """

    NUMERO_DE_VOZES = 4
    PASSO_BPM = 10
    ITENS_POR_COLUNA = 10         # lista de instrumentos em colunas, para não sair da tela
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
        self.voz_selecionada: int = 0
        self._texto_gerado: str | None = None   # texto da última geração

    def construir(self) -> None:
        """Desenha a tela inteira e preenche os controles com os valores da v0."""
        self.desenho = estilo.Desenho(self, self.LARGURA, self.ALTURA)
        self.desenho.pack()
        self._construir_cabecalho()
        self._construir_campo_texto()
        self._construir_bloco_configuracao()
        self._construir_botoes()
        self._ao_trocar_voz(0)                   # preenche os controles com a v0

    # ---- Construção -----------------------------------------------------

    def _construir_cabecalho(self) -> None:
        """Cartão azul-claro, botão redondo de upload e título."""
        d = self.desenho
        d.retangulo(24, 21, 764, self.ALTURA - 57, 57, estilo.CARTAO)
        tag = d.nova_tag()
        d.circulo(52, 51, 70, estilo.PAINEL, tags=tag)
        d.icone("upload", 66, 64, 42, 43, estilo.VERMELHO, tags=tag)
        d.tornar_clicavel(tag, self._ao_abrir_carregamento)
        d.texto(406, 21, "gerador de música", estilo.TITULO, ancora="n")

    def _construir_campo_texto(self) -> None:
        """Rótulo, pílula "salvar texto" e o campo de texto com a dica "digite aqui...".

        O campo usa wrap="none" (cada linha é uma voz e não pode quebrar sozinha)
        e undo=True (Ctrl+Z).
        """
        d = self.desenho
        d.texto(55, 153, "texto de entrada:")
        d.botao(479, 162, 288, 47, "salvar texto", self._ao_salvar_texto, cor=estilo.FUNDO, raio=23)

        d.retangulo(52, 221, 715, 223, 25, estilo.PAINEL)
        self.campo_texto = tk.Text(
            d, wrap="none", undo=True, bd=0, highlightthickness=0, font=estilo.fonte(46),
            bg=estilo.PAINEL, fg=estilo.ESCURO, insertbackground=estilo.ESCURO,
            selectbackground=estilo.FUNDO, selectforeground=estilo.PAINEL,
        )
        d.widget(66, 231, 687, 203, self.campo_texto)

        # "digite aqui..." aparece no canto de baixo enquanto o campo está vazio
        self.dica = tk.Label(self.campo_texto, text="digite aqui...", bd=0, font=estilo.fonte(),
                             bg=estilo.PAINEL, fg=estilo.FUNDO, cursor="xterm")
        self.dica.bind("<Button-1>", lambda evento: self.campo_texto.focus_set())
        self.campo_texto.bind("<<Modified>>", self._ao_modificar_texto)
        self._atualizar_dica()

    def _construir_bloco_configuracao(self) -> None:
        """Painel de configurações: voz, volume, bpm, instrumento e oitava."""
        d = self.desenho
        d.texto(52, 454, "configurações:")
        d.retangulo(52, 525, 715, 646, 25, estilo.PAINEL)
        self._construir_seletor_voz(74, 535)
        self._construir_volume(74, 610)
        self.rotulo_bpm = self._construir_contador(74, 728, "bpm:", self._ao_mudar_bpm, self.PASSO_BPM)
        self._construir_instrumento(74, 838)
        self.rotulo_oitava = self._construir_contador(74, 936, "oitava:", self._ao_mudar_oitava, 1)

    def _construir_seletor_voz(self, x: float, y: float) -> None:
        """Abas v0–v3; a selecionada fica escura.

        Args:
            x: esquerda do rótulo "voz:", em px do Figma.
            y: topo do rótulo, em px do Figma.
        """
        d = self.desenho
        d.texto(x, y, "voz:", cor=estilo.FUNDO)
        self._abas_voz: list[int] = []
        for i in range(self.NUMERO_DE_VOZES):
            fundo, _ = d.botao(x + 110 + i * 87, y + 9, 75, 47, f"v{i}",
                               lambda i=i: self._ao_trocar_voz(i), cor=estilo.FUNDO, raio=23)
            self._abas_voz.append(fundo)

    def _construir_volume(self, x: float, y: float) -> None:
        """Rótulo, valor numérico, ícone de alto-falante e deslizador de 0 a 127.

        Args:
            x: esquerda do rótulo, em px do Figma.
            y: topo do rótulo, em px do Figma.
        """
        d = self.desenho
        d.texto(x, y, "volume:", cor=estilo.FUNDO)
        self.rotulo_volume = d.texto(723, y, "", cor=estilo.FUNDO, ancora="ne")
        d.icone("alto_falante", x + 6.5, y + 60, 32, 62, estilo.FUNDO, espessura=3)
        self.deslizador_volume = estilo.Deslizador(d, 122, y + 89, 601, 0, 127, self._ao_mudar_volume)

    def _construir_contador(self, x: float, y: float, titulo: str, ao_mudar, passo: int) -> int:
        """Rótulo + pílula "valor  - +" (usado no bpm e na oitava).

        Args:
            x: esquerda, em px do Figma.
            y: topo do rótulo, em px do Figma.
            titulo: texto do rótulo (ex.: "bpm:").
            ao_mudar: função chamada com +passo ou -passo.
            passo: quanto cada clique em '-' ou '+' muda o valor.

        Returns:
            O id do texto do valor, para atualizar depois.
        """
        d = self.desenho
        d.texto(x, y, titulo, cor=estilo.FUNDO)
        topo = y + 62
        d.retangulo(x, topo, 190, 47, 23, estilo.FUNDO)
        valor = d.texto(x + 16, topo + 23.5, "", cor=estilo.PAINEL, ancora="w")
        for simbolo, centro, delta in (("-", x + 128, -passo), ("+", x + 165, +passo)):
            tag = d.nova_tag()
            d.retangulo(centro - 17, topo + 4, 34, 39, 0, estilo.FUNDO, tags=tag)   # área de clique
            d.texto(centro, topo + 23.5, simbolo, cor=estilo.PAINEL, ancora="center", tags=tag)
            d.tornar_clicavel(tag, lambda delta=delta: ao_mudar(delta))
        return valor

    def _construir_instrumento(self, x: float, y: float) -> None:
        """Pílula com o instrumento da voz; ao clicar abre a lista (tk.Menu).

        A lista mostra os instrumentos do catálogo em colunas de
        ITENS_POR_COLUNA itens.

        Args:
            x: esquerda do rótulo, em px do Figma.
            y: topo do rótulo, em px do Figma.
        """
        d = self.desenho
        d.texto(x, y, "instrumento:", cor=estilo.FUNDO)
        topo = y + 62
        tag = d.nova_tag()
        d.retangulo(x - 1, topo, 473, 47, 23, estilo.FUNDO, tags=tag)
        self.rotulo_instrumento = d.texto(x + 13, topo + 23.5, "", cor=estilo.PAINEL, ancora="w", tags=tag)
        d.texto(x + 445, topo + 23.5, "v", cor=estilo.PAINEL, ancora="center", tags=tag)
        d.tornar_clicavel(tag, self._ao_abrir_lista_instrumentos)
        self._posicao_lista = (x - 1, topo + 47)

        self._nome_por_programa = {i.programa: i.nome.lower() for i in self.app.controlador.listar_instrumentos()}
        self.menu_instrumentos = tk.Menu(self, tearoff=False, bd=0, font=estilo.fonte(46),
                                         bg=estilo.PAINEL, fg=estilo.ESCURO,
                                         activebackground=estilo.FUNDO, activeforeground=estilo.PAINEL)
        for n, (programa, nome) in enumerate(self._nome_por_programa.items()):
            nova_coluna = n > 0 and n % self.ITENS_POR_COLUNA == 0
            self.menu_instrumentos.add_command(label=nome, columnbreak=nova_coluna,
                                               command=lambda p=programa: self._ao_escolher_instrumento(p))

    def _construir_botoes(self) -> None:
        """Botões "gerar música" e "limpar", fixos embaixo."""
        d = self.desenho
        d.botao(66, 1077, 307, 76, "gerar música", self._ao_gerar)
        d.botao(594, 1077, 158, 76, "limpar", self._ao_limpar)

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

    def _ao_trocar_voz(self, indice: int) -> None:
        """Seleciona a voz, pinta a aba e mostra os valores dela nos controles.

        Args:
            indice: número da voz (0 a 3).
        """
        self.voz_selecionada = indice
        for i, aba in enumerate(self._abas_voz):
            self.desenho.pintar(aba, estilo.ESCURO if i == indice else estilo.FUNDO)
        self._atualizar_controles()

    def _atualizar_controles(self) -> None:
        """Copia do controlador para a tela os valores da voz selecionada."""
        d, controlador, i = self.desenho, self.app.controlador, self.voz_selecionada
        d.itemconfig(self.rotulo_bpm, text=str(controlador.get_bpm()))
        d.itemconfig(self.rotulo_oitava, text=str(controlador.get_oitava_voz(i)))
        volume = controlador.get_volume_voz(i)
        self.deslizador_volume.set(volume)
        d.itemconfig(self.rotulo_volume, text=str(volume))
        programa = controlador.get_instrumento_voz(i)
        d.itemconfig(self.rotulo_instrumento, text=self._nome_por_programa.get(programa, f"programa {programa}"))

    def _ao_mudar_bpm(self, delta: int) -> None:
        """Clique em '-' ou '+' do bpm. Fora do limite, o clique é ignorado.

        Args:
            delta: quanto somar ao BPM (+10 ou -10).
        """
        controlador = self.app.controlador
        try:
            controlador.set_bpm(controlador.get_bpm() + delta)
        except ValueError:
            return                              # fora do limite: ignora
        self._atualizar_controles()

    def _ao_mudar_oitava(self, delta: int) -> None:
        """Clique em '-' ou '+' da oitava da voz selecionada. Fora do limite, ignora.

        Args:
            delta: quanto somar à oitava (+1 ou -1).
        """
        controlador = self.app.controlador
        i = self.voz_selecionada
        try:
            controlador.set_oitava_voz(i, controlador.get_oitava_voz(i) + delta)
        except ValueError:
            return
        self._atualizar_controles()

    def _ao_mudar_volume(self, valor: int) -> None:
        """Chamado pelo deslizador: salva o volume da voz e atualiza o número.

        Args:
            valor: novo volume (0–127).
        """
        self.app.controlador.set_volume_voz(self.voz_selecionada, valor)
        self.desenho.itemconfig(self.rotulo_volume, text=str(valor))

    def _ao_abrir_lista_instrumentos(self) -> None:
        """Abre a lista de instrumentos logo abaixo da pílula."""
        x, y = self._posicao_lista
        self.menu_instrumentos.tk_popup(self.desenho.winfo_rootx() + estilo.px(x),
                                        self.desenho.winfo_rooty() + estilo.px(y))

    def _ao_escolher_instrumento(self, programa: int) -> None:
        """Item da lista escolhido: salva o instrumento da voz selecionada.

        Args:
            programa: programa MIDI escolhido.
        """
        self.app.controlador.set_instrumento_voz(self.voz_selecionada, programa)
        self._atualizar_controles()

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
