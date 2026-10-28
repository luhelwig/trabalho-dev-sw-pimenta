"""NOVA (Fase 3): painel de configurações da tela principal.

Extraído da TelaPrincipal (bad smell "Classe Grande"): a tela tinha 25
métodos e 15 atributos, misturando o campo de texto com todos os
controles de parâmetros. Agora a tela cuida do texto e dos botões, e este
painel cuida das abas de voz, volume, bpm, instrumento e oitava.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from gerador_musical.aplicacao.controlador_configuracao import ControladorConfiguracao
from gerador_musical.interface import estilo
from gerador_musical.interface.estilo import Caixa


class PainelConfiguracoes:
    """Bloco "configurações:" do Figma, desenhado no Canvas da tela principal.

    Volume, instrumento e oitava valem para a voz selecionada (abas v0–v3);
    o bpm vale para a música toda. Os valores são lidos e alterados pelo
    ControladorConfiguracao. Medidas em px do Figma (ver estilo.py).

    Attributes:
        voz_selecionada: número da voz cujos valores aparecem nos controles.
        NUMERO_DE_VOZES: abas mostradas (v0 a v3).
        VOLUME_MAXIMO: fim do deslizador de volume (decisão do grupo: 100).
        PASSO_BPM: quanto cada clique em '-' ou '+' muda o bpm.
        ITENS_POR_COLUNA: itens por coluna na lista de instrumentos.
    """

    NUMERO_DE_VOZES = 4
    VOLUME_MAXIMO = 100
    PASSO_BPM = 10
    ITENS_POR_COLUNA = 10

    def __init__(self, desenho: estilo.Desenho, configuracao: ControladorConfiguracao) -> None:
        """Guarda onde desenhar e com quem falar (os controles nascem em construir()).

        Args:
            desenho: Canvas da tela principal.
            configuracao: fachada das configurações iniciais.
        """
        self.desenho = desenho
        self.configuracao = configuracao
        self.voz_selecionada: int = 0
        self._abas_voz: list[int] = []
        self._nome_por_programa: dict[int, str] = {}

    def construir(self) -> None:
        """Desenha o painel e preenche os controles com os valores da v0."""
        d = self.desenho
        d.texto(52, 454, "configurações:")
        d.retangulo(Caixa(52, 525, 715, 646), estilo.PAINEL, raio=25)
        self._construir_seletor_voz(74, 535)
        self._construir_volume(74, 610)
        self.rotulo_bpm = self._construir_contador(74, 728, "bpm:", self._ao_mudar_bpm, self.PASSO_BPM)
        self._construir_instrumento(74, 838)
        self.rotulo_oitava = self._construir_contador(74, 936, "oitava:", self._ao_mudar_oitava, 1)
        self.selecionar_voz(0)

    # ---- Construção -----------------------------------------------------

    def _construir_seletor_voz(self, x: float, y: float) -> None:
        """Abas v0–v3; a selecionada fica escura.

        Args:
            x: esquerda do rótulo "voz:", em px do Figma.
            y: topo do rótulo, em px do Figma.
        """
        d = self.desenho
        d.texto(x, y, "voz:", estilo.ESTILO_SECUNDARIO)
        for i in range(self.NUMERO_DE_VOZES):
            fundo, _ = d.botao(Caixa(x + 110 + i * 87, y + 9, 75, 47), f"v{i}",
                               lambda i=i: self.selecionar_voz(i), cor=estilo.FUNDO, raio=23)
            self._abas_voz.append(fundo)

    def _construir_volume(self, x: float, y: float) -> None:
        """Rótulo, valor numérico, ícone de alto-falante e deslizador de 0 a VOLUME_MAXIMO.

        Args:
            x: esquerda do rótulo, em px do Figma.
            y: topo do rótulo, em px do Figma.
        """
        d = self.desenho
        d.texto(x, y, "volume:", estilo.ESTILO_SECUNDARIO)
        self.rotulo_volume = d.texto(723, y, "", estilo.ESTILO_SECUNDARIO.com(ancora="ne"))
        d.icone("alto_falante", Caixa(x + 6.5, y + 60, 32, 62), estilo.FUNDO, espessura=3)
        self.deslizador_volume = estilo.Deslizador(d, Caixa(122, y + 89, 601, 7), 0, self.VOLUME_MAXIMO,
                                                   self._ao_mudar_volume)

    def _construir_contador(self, x: float, y: float, titulo: str,
                            ao_mudar: Callable[[int], None], passo: int) -> int:
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
        d.texto(x, y, titulo, estilo.ESTILO_SECUNDARIO)
        topo = y + 62
        d.retangulo(Caixa(x, topo, 190, 47), estilo.FUNDO, raio=23)
        valor = d.texto(x + 16, topo + 23.5, "", estilo.ESTILO_VALOR)
        for simbolo, centro, delta in (("-", x + 128, -passo), ("+", x + 165, +passo)):
            tag = d.nova_tag()
            d.retangulo(Caixa(centro - 17, topo + 4, 34, 39), estilo.FUNDO, tags=tag)   # área de clique
            d.texto(centro, topo + 23.5, simbolo, estilo.ESTILO_BOTAO, tags=tag)
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
        d.texto(x, y, "instrumento:", estilo.ESTILO_SECUNDARIO)
        pilula = Caixa(x - 1, y + 62, 473, 47)
        _, meio = pilula.centro
        tag = d.nova_tag()
        d.retangulo(pilula, estilo.FUNDO, raio=23, tags=tag)
        self.rotulo_instrumento = d.texto(x + 13, meio, "", estilo.ESTILO_VALOR, tags=tag)
        d.texto(x + 445, meio, "v", estilo.ESTILO_BOTAO, tags=tag)
        d.tornar_clicavel(tag, self._ao_abrir_lista_instrumentos)
        self._posicao_lista = (pilula.x, pilula.y + pilula.altura)

        instrumentos = self.configuracao.listar_instrumentos()
        self._nome_por_programa = {i.programa: i.nome.lower() for i in instrumentos}
        self.menu_instrumentos = tk.Menu(d, tearoff=False, bd=0, font=estilo.fonte(46),
                                         bg=estilo.PAINEL, fg=estilo.ESCURO,
                                         activebackground=estilo.FUNDO, activeforeground=estilo.PAINEL)
        for n, (programa, nome) in enumerate(self._nome_por_programa.items()):
            nova_coluna = n > 0 and n % self.ITENS_POR_COLUNA == 0
            self.menu_instrumentos.add_command(label=nome, columnbreak=nova_coluna,
                                               command=lambda p=programa: self._ao_escolher_instrumento(p))

    # ---- Eventos --------------------------------------------------------

    def selecionar_voz(self, indice: int) -> None:
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
        d, configuracao, i = self.desenho, self.configuracao, self.voz_selecionada
        d.itemconfig(self.rotulo_bpm, text=str(configuracao.get_bpm()))
        d.itemconfig(self.rotulo_oitava, text=str(configuracao.get_oitava_voz(i)))
        volume = configuracao.get_volume_voz(i)
        self.deslizador_volume.set(volume)
        d.itemconfig(self.rotulo_volume, text=str(volume))
        programa = configuracao.get_instrumento_voz(i)
        d.itemconfig(self.rotulo_instrumento, text=self._nome_por_programa.get(programa, f"programa {programa}"))

    def _alterar(self, alteracao: Callable[[], None]) -> None:
        """Aplica uma alteração e atualiza a tela; fora do limite (ValueError), ignora o clique.

        Parte comum de bpm e oitava (antes o mesmo try/except aparecia duas vezes).

        Args:
            alteracao: função que chama um set_ do controlador.
        """
        try:
            alteracao()
        except ValueError:
            return
        self._atualizar_controles()

    def _ao_mudar_bpm(self, delta: int) -> None:
        """Clique em '-' ou '+' do bpm.

        Args:
            delta: quanto somar ao BPM (+10 ou -10).
        """
        configuracao = self.configuracao
        self._alterar(lambda: configuracao.set_bpm(configuracao.get_bpm() + delta))

    def _ao_mudar_oitava(self, delta: int) -> None:
        """Clique em '-' ou '+' da oitava da voz selecionada.

        Args:
            delta: quanto somar à oitava (+1 ou -1).
        """
        configuracao, i = self.configuracao, self.voz_selecionada
        self._alterar(lambda: configuracao.set_oitava_voz(i, configuracao.get_oitava_voz(i) + delta))

    def _ao_mudar_volume(self, valor: int) -> None:
        """Chamado pelo deslizador: salva o volume da voz e atualiza o número.

        Args:
            valor: novo volume (0 a VOLUME_MAXIMO).
        """
        self.configuracao.set_volume_voz(self.voz_selecionada, valor)
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
        self._alterar(lambda: self.configuracao.set_instrumento_voz(self.voz_selecionada, programa))
