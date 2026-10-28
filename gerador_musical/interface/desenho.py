"""NOVO (Fase 3): ferramentas para desenhar as telas do Figma num Canvas.

Separado de estilo.py, que ficou só com o tema (cores, fonte, escala e
estilos de texto).

Como funciona:
  - Cada tela é um Desenho (um tk.Canvas) do tamanho do frame no Figma.
  - Posição e tamanho de cada coisa são uma Caixa, com os mesmos X, Y, W e
    H do painel de propriedades do Figma (bad smell "Lista de Parâmetros
    Longa": antes eram quatro números soltos em cada método).
  - O tkinter não tem cantos arredondados: botões, pílulas e painéis são
    polígonos desenhados no Canvas, e o clique é ligado com tag_bind.
  - ICONES guarda os ícones, desenhados numa grade 24x24.
"""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from typing import Callable

from gerador_musical.interface.estilo import ESCURO, ESTILO_BOTAO, ESTILO_ROTULO, FUNDO, PAINEL, EstiloTexto, fonte, px


# Ícones de linha numa grade 24x24 (mesmo traço dos ícones usados no Figma).
# ("linha", pontos...) | ("circulo", cx, cy, raio) | ("arco", cx, cy, raio, início, extensão)
ICONES = {
    "upload": [("linha", (3, 15), (3, 21), (21, 21), (21, 15)),
               ("linha", (7, 8), (12, 3), (17, 8)), ("linha", (12, 3), (12, 15))],
    "nuvem": [("arco", 18, 14, 5, -61.4, 151.4), ("linha", (18, 9), (16.7, 9)),
              ("arco", 9, 11, 8, 14.5, 207), ("linha", (8, 16), (12, 12), (16, 16)),
              ("linha", (12, 12), (12, 21))],
    "alto_falante": [("linha", (0, 8.5), (7, 8.5), (24, 0), (24, 24), (7, 15.5), (0, 15.5), (0, 8.5))],
    "tocar": [("circulo", 12, 12, 10), ("linha", (10, 8), (16, 12), (10, 16), (10, 8))],
    "pausar": [("circulo", 12, 12, 10), ("linha", (10, 9), (10, 15)), ("linha", (14, 9), (14, 15))],
}


@dataclass(frozen=True)
class Caixa:
    """Retângulo do Figma: posição e tamanho em px do Figma. Objeto de valor.

    Agrupa x, y, largura e altura, que antes iam soltos para quase todos os
    métodos de Desenho (refatoração "Introduzir Objeto-Parâmetro").

    Attributes:
        x: esquerda.
        y: topo.
        largura: largura.
        altura: altura.
    """

    x: float
    y: float
    largura: float
    altura: float

    @property
    def centro(self) -> tuple[float, float]:
        """Ponto do meio da caixa, em px do Figma."""
        return self.x + self.largura / 2, self.y + self.altura / 2

    def em_pixels(self) -> tuple[int, int, int, int]:
        """Devolve (esquerda, topo, direita, base) já convertidos por px()."""
        return px(self.x), px(self.y), px(self.x + self.largura), px(self.y + self.altura)

    def ponto_da_grade(self, a: float, b: float, divisoes: int = 24) -> tuple[int, int]:
        """Converte um ponto de uma grade divisoes x divisoes dentro da caixa em pixels.

        Args:
            a: coluna na grade (0 = esquerda da caixa).
            b: linha na grade (0 = topo da caixa).
            divisoes: tamanho da grade (os ícones usam 24x24).
        """
        return px(self.x + a * self.largura / divisoes), px(self.y + b * self.altura / divisoes)

    def quadrado_da_grade(self, cx: float, cy: float, raio: float) -> tuple[int, int, int, int]:
        """Cantos, em pixels, do quadrado que envolve um círculo da grade 24x24.

        É o formato que create_oval e create_arc pedem.

        Args:
            cx: coluna do centro na grade.
            cy: linha do centro na grade.
            raio: raio, em unidades da grade.
        """
        return (*self.ponto_da_grade(cx - raio, cy - raio), *self.ponto_da_grade(cx + raio, cy + raio))

    def expandida(self, margem_x: float, margem_y: float) -> Caixa:
        """Devolve uma caixa maior, com a margem dada em cada lado."""
        return Caixa(self.x - margem_x, self.y - margem_y,
                     self.largura + 2 * margem_x, self.altura + 2 * margem_y)


def _contorno_arredondado(esquerda: int, topo: int, direita: int, base: int, raio: int) -> list[float]:
    """Pontos de um retângulo cujos cantos são quartos de círculo (de 15 em 15 graus)."""
    pontos = []
    cantos = ((direita - raio, topo + raio, -90), (direita - raio, base - raio, 0),
              (esquerda + raio, base - raio, 90), (esquerda + raio, topo + raio, 180))
    for cx, cy, angulo_inicial in cantos:               # sentido horário, começando no topo-direita
        for passo in range(7):                          # 0°, 15°, ..., 90° de cada canto
            angulo = math.radians(angulo_inicial + 15 * passo)
            pontos += [cx + raio * math.cos(angulo), cy + raio * math.sin(angulo)]
    return pontos


class Desenho(tk.Canvas):
    """Canvas que recebe medidas do Figma. Cada tela desenha nele."""

    def __init__(self, mestre: tk.Misc, largura: float, altura: float) -> None:
        """Cria o Canvas com o tamanho do frame do Figma convertido por px().

        Args:
            mestre: widget onde o Canvas fica (a tela).
            largura: largura do frame no Figma.
            altura: altura do frame no Figma.
        """
        super().__init__(mestre, width=px(largura), height=px(altura), bg=FUNDO, highlightthickness=0, bd=0)
        self._contador_tags = 0

    # ---- Formas -------------------------------------------------------------

    def retangulo(self, caixa: Caixa, cor: str, raio: float = 0, tags: str | tuple = ()) -> int:
        """Desenha um retângulo de cantos arredondados (raio 0 = cantos retos).

        Args:
            caixa: posição e tamanho, em px do Figma.
            cor: cor de preenchimento e de contorno.
            raio: raio dos cantos em px do Figma.
            tags: tags do tkinter (para agrupar itens clicáveis).

        Returns:
            O id do item no Canvas.
        """
        esquerda, topo, direita, base = caixa.em_pixels()
        if px(raio) == 0:
            return self.create_rectangle(esquerda, topo, direita, base, fill=cor, outline=cor, tags=tags)
        pontos = _contorno_arredondado(esquerda, topo, direita, base, px(raio))
        return self.create_polygon(pontos, fill=cor, outline=cor, tags=tags)

    def circulo(self, caixa: Caixa, cor: str, tags: str | tuple = ()) -> int:
        """Desenha um círculo (ou elipse) preenchido dentro da caixa.

        Args:
            caixa: quadrado que contém o círculo, em px do Figma.
            cor: cor do círculo.
            tags: tags do tkinter.

        Returns:
            O id do item no Canvas.
        """
        return self.create_oval(*caixa.em_pixels(), fill=cor, outline=cor, tags=tags)

    def texto(self, x: float, y: float, texto: str, estilo: EstiloTexto = ESTILO_ROTULO,
              tags: str | tuple = ()) -> int:
        """Escreve um texto na fonte do tema.

        Args:
            x: posição horizontal, em px do Figma.
            y: posição vertical, em px do Figma.
            texto: o que escrever.
            estilo: tamanho, cor e âncora (ver ESTILO_*).
            tags: tags do tkinter.

        Returns:
            O id do item no Canvas (para trocar o texto depois com itemconfig).
        """
        return self.create_text(px(x), px(y), text=texto, fill=estilo.cor, font=fonte(estilo.tamanho),
                                anchor=estilo.ancora, tags=tags)

    def icone(self, nome: str, caixa: Caixa, cor: str, espessura: float = 3.5, tags: str | tuple = ()) -> None:
        """Desenha um ícone de ICONES dentro de uma caixa do Figma.

        Fase 3: antes um if/else testava o tipo de cada parte ("linha",
        "circulo" ou "arco"). Agora uma tabela liga cada tipo ao método que o
        desenha; um tipo novo é só um método novo e uma linha da tabela

        Args:
            nome: chave em ICONES ("upload", "nuvem", "alto_falante", "tocar", "pausar").
            caixa: onde o ícone fica, em px do Figma.
            cor: cor do traço.
            espessura: espessura do traço em px do Figma.
            tags: tags do tkinter.
        """
        desenhar = {"linha": self._parte_linha, "circulo": self._parte_circulo, "arco": self._parte_arco}
        opcoes = {"width": max(1, px(espessura)), "tags": tags}
        for tipo, *dados in ICONES[nome]:
            desenhar[tipo](caixa, dados, cor, opcoes)

    def _parte_linha(self, caixa: Caixa, pontos: list, cor: str, opcoes: dict) -> None:
        """Parte ("linha", pontos...) de um ícone: uma linha ligando os pontos da grade.

        Args:
            caixa: onde o ícone fica.
            pontos: pares (coluna, linha) na grade 24x24.
            cor: cor do traço.
            opcoes: espessura e tags.
        """
        coordenadas = [c for a, b in pontos for c in caixa.ponto_da_grade(a, b)]
        self.create_line(coordenadas, fill=cor, capstyle="round", joinstyle="round", **opcoes)

    def _parte_circulo(self, caixa: Caixa, dados: list, cor: str, opcoes: dict) -> None:
        """Parte ("circulo", cx, cy, raio) de um ícone: só o contorno.

        Args:
            caixa: onde o ícone fica.
            dados: centro e raio na grade 24x24.
            cor: cor do traço.
            opcoes: espessura e tags.
        """
        cx, cy, raio = dados
        self.create_oval(*caixa.quadrado_da_grade(cx, cy, raio), outline=cor, **opcoes)

    def _parte_arco(self, caixa: Caixa, dados: list, cor: str, opcoes: dict) -> None:
        """Parte ("arco", cx, cy, raio, início, extensão) de um ícone; ângulos em graus.

        Args:
            caixa: onde o ícone fica.
            dados: centro e raio na grade 24x24, ângulo inicial e extensão.
            cor: cor do traço.
            opcoes: espessura e tags.
        """
        cx, cy, raio, inicio, extensao = dados
        self.create_arc(*caixa.quadrado_da_grade(cx, cy, raio), start=inicio, extent=extensao,
                        style="arc", outline=cor, **opcoes)

    def pintar(self, item: int, cor: str) -> None:
        """Troca a cor de uma forma (ex.: aba de voz selecionada).

        Args:
            item: id do item no Canvas.
            cor: nova cor de preenchimento e de contorno.
        """
        self.itemconfig(item, fill=cor, outline=cor)

    def widget(self, caixa: Caixa, widget: tk.Widget) -> int:
        """Coloca um widget do tkinter (ex.: tk.Text) na posição do Figma.

        Args:
            caixa: posição e tamanho, em px do Figma.
            widget: o widget a posicionar.

        Returns:
            O id da janela no Canvas.
        """
        return self.create_window(px(caixa.x), px(caixa.y), window=widget, anchor="nw",
                                  width=px(caixa.largura), height=px(caixa.altura))

    # ---- Cliques ------------------------------------------------------------

    def nova_tag(self) -> str:
        """Gera um nome único para agrupar os itens de um botão (fundo + texto + ícone)."""
        self._contador_tags += 1
        return f"clicavel{self._contador_tags}"

    def tornar_clicavel(self, tag: str, comando: Callable[[], None]) -> None:
        """Liga o clique nos itens da tag a um comando e mostra a "mãozinha".

        Args:
            tag: tag dos itens clicáveis.
            comando: função chamada no clique, sem argumentos.
        """
        self.tag_bind(tag, "<Button-1>", lambda evento: comando())
        self.tag_bind(tag, "<Enter>", lambda evento: self.config(cursor="hand2"))
        self.tag_bind(tag, "<Leave>", lambda evento: self.config(cursor=""))

    def botao(self, caixa: Caixa, texto: str, comando: Callable[[], None], cor: str = ESCURO,
              raio: float = 22) -> tuple[int, int]:
        """Desenha um botão arredondado com texto creme no meio.

        cor=ESCURO é o botão principal; cor=FUNDO é a pílula secundária.

        Args:
            caixa: posição e tamanho, em px do Figma.
            texto: rótulo do botão.
            comando: função chamada no clique.
            cor: cor do fundo.
            raio: raio dos cantos.

        Returns:
            (id do fundo, id do texto), para mudar a cor ou o texto depois.
        """
        tag = self.nova_tag()
        fundo = self.retangulo(caixa, cor, raio=raio, tags=tag)
        rotulo = self.texto(*caixa.centro, texto, ESTILO_BOTAO, tags=tag)
        self.tornar_clicavel(tag, comando)
        return fundo, rotulo


class Deslizador:
    """Barra de volume do Figma: trilho fino + bolinha escura que se arrasta.

    Attributes:
        DIAMETRO: diâmetro da bolinha em px do Figma.
        AREA_DE_CLIQUE: margem (x, y) em volta do trilho que também aceita clique.
    """

    DIAMETRO = 24
    AREA_DE_CLIQUE = (15, 20)

    def __init__(self, desenho: Desenho, trilho: Caixa, minimo: int, maximo: int,
                 comando: Callable[[int], None]) -> None:
        """Desenha o deslizador e liga clique e arrasto.

        Args:
            desenho: Canvas onde desenhar.
            trilho: posição e tamanho do trilho, em px do Figma.
            minimo: valor na ponta esquerda.
            maximo: valor na ponta direita.
            comando: função chamada com o novo valor quando o usuário arrasta.
        """
        self.desenho = desenho
        self.trilho = trilho
        self.minimo, self.maximo = minimo, maximo
        self.comando = comando
        tag = desenho.nova_tag()
        desenho.retangulo(trilho.expandida(*self.AREA_DE_CLIQUE), PAINEL, tags=tag)
        desenho.retangulo(trilho, FUNDO, raio=trilho.altura / 2, tags=tag)
        self.bolinha = desenho.create_oval(0, 0, 0, 0, fill=ESCURO, outline=ESCURO, tags=tag)
        desenho.tag_bind(tag, "<Button-1>", self._ao_arrastar)
        desenho.tag_bind(tag, "<B1-Motion>", self._ao_arrastar)
        desenho.tag_bind(tag, "<Enter>", lambda evento: desenho.config(cursor="hand2"))
        desenho.tag_bind(tag, "<Leave>", lambda evento: desenho.config(cursor=""))

    def set(self, valor: int) -> None:
        """Move a bolinha para a posição do valor (não chama o comando).

        Args:
            valor: valor entre mínimo e máximo (fora disso, a bolinha fica na ponta).
        """
        fracao = min(1.0, max(0.0, (valor - self.minimo) / (self.maximo - self.minimo)))
        _, centro_y = self.trilho.centro
        x = self.trilho.x + fracao * self.trilho.largura - self.DIAMETRO / 2
        bolinha = Caixa(x, centro_y - self.DIAMETRO / 2, self.DIAMETRO, self.DIAMETRO)
        self.desenho.coords(self.bolinha, *bolinha.em_pixels())

    def _ao_arrastar(self, evento: tk.Event) -> None:
        """Converte a posição do mouse em valor, move a bolinha e chama o comando.

        Args:
            evento: clique ou movimento do mouse (usa evento.x).
        """
        esquerda, _, direita, _ = self.trilho.em_pixels()
        fracao = min(1.0, max(0.0, (evento.x - esquerda) / (direita - esquerda)))
        valor = round(self.minimo + fracao * (self.maximo - self.minimo))
        self.set(valor)
        self.comando(valor)
