"""Tema visual da interface, copiado do croqui no Figma.

Como funciona:
  - Cada tela é um Canvas (classe Desenho) do tamanho do frame no Figma.
  - As medidas no código são as do Figma (em px) e passam por px(), que
    multiplica pela escala. Assim dá para conferir cada número no painel
    de propriedades do Figma.
  - A escala é calculada uma vez, para a tela mais alta caber no monitor.
  - O tkinter não tem cantos arredondados: botões, pílulas e painéis são
    desenhados no Canvas, e o clique é ligado com tag_bind.

Constantes: as cores do Figma (FUNDO, CARTAO, PAINEL, ESCURO, VERMELHO),
a fonte (Micro 5, com Courier New de reserva), os tamanhos de texto
(TITULO, TEXTO) e ICONES, os ícones desenhados numa grade 24x24.
"""

from __future__ import annotations

import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from typing import Callable

# ---- Cores (iguais às do Figma) -------------------------------------------
FUNDO = "#467385"      # fundo da janela, pílulas e textos secundários
CARTAO = "#a4cbd2"     # cartão azul-claro com cantos arredondados
PAINEL = "#ffe7cf"     # painéis creme e texto dos botões
ESCURO = "#071f36"     # títulos e botões principais
VERMELHO = "#900b09"   # ícone de upload

# ---- Fonte ------------------------------------------------------------------
FAMILIA = "Micro 5"                 # fonte pixelada do Figma (Google Fonts, licença OFL)
FAMILIA_RESERVA = "Courier New"     # usada se a Micro 5 não puder ser carregada
ARQUIVO_FONTE = Path(__file__).parent / "recursos" / "Micro5-Regular.ttf"
TITULO = 78                         # tamanhos de fonte usados no Figma (px)
TEXTO = 65

# ---- Escala -----------------------------------------------------------------
ALTURA_REFERENCIA = 1232    # altura da tela mais alta (principal, já com a Fase 2)
FRACAO_DO_MONITOR = 0.85    # a tela mais alta ocupa 85% da altura livre do monitor
MARGEM_MONITOR = 140        # barra de tarefas + barra de título da janela

_escala = 0.6
_familia = FAMILIA_RESERVA
_fator_fonte = 0.6          # Courier é mais larga que a Micro 5


def preparar_sistema() -> None:
    """Prepara o sistema operacional. Chamar ANTES de criar a janela.

    Carrega a fonte do arquivo .ttf só para este programa (ninguém precisa
    instalar) e, no Windows, deixa o texto nítido com zoom de tela (125%,
    150%).
    """
    if sys.platform == "win32":
        _preparar_windows()
    else:
        _carregar_fonte_fontconfig()


def _preparar_windows() -> None:
    """Windows: ativa o modo de alta resolução e registra a fonte só neste processo."""
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    if ARQUIVO_FONTE.exists():
        FR_PRIVATE = 0x10
        ctypes.windll.gdi32.AddFontResourceExW(str(ARQUIVO_FONTE), FR_PRIVATE, 0)


def _carregar_fonte_fontconfig() -> None:
    """Linux: registra o .ttf no fontconfig, que é onde o tkinter procura fontes.

    Se a biblioteca fontconfig não existir ou algo falhar, o programa segue
    com a fonte reserva.
    """
    import ctypes
    import ctypes.util
    biblioteca = ctypes.util.find_library("fontconfig")
    if biblioteca is None or not ARQUIVO_FONTE.exists():
        return
    try:
        fontconfig = ctypes.CDLL(biblioteca)
        fontconfig.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fontconfig.FcConfigAppFontAddFile(None, str(ARQUIVO_FONTE).encode())
    except (OSError, AttributeError):
        pass


def preparar(janela: tk.Tk) -> None:
    """Escolhe a fonte e calcula a escala. Chamar logo DEPOIS de criar a janela.

    Usa a Micro 5 se ela estiver disponível (senão, Courier New um pouco
    menor) e calcula a escala para a tela mais alta ocupar
    FRACAO_DO_MONITOR da altura livre do monitor.

    Args:
        janela: janela principal do tkinter.
    """
    global _escala, _familia, _fator_fonte
    if FAMILIA in tkfont.families(janela):
        _familia, _fator_fonte = FAMILIA, 1.0
    else:
        print(f"Aviso: fonte '{FAMILIA}' não encontrada em {ARQUIVO_FONTE}; "
              f"usando {FAMILIA_RESERVA}.", file=sys.stderr)
    altura_livre = janela.winfo_screenheight() - MARGEM_MONITOR
    _escala = FRACAO_DO_MONITOR * altura_livre / ALTURA_REFERENCIA


def px(medida: float) -> int:
    """Converte uma medida do Figma para pixels na tela.

    Args:
        medida: medida em px do Figma.

    Returns:
        round(medida * escala).
    """
    return round(medida * _escala)


def fonte(tamanho: float = TEXTO) -> tuple[str, int]:
    """Devolve a fonte do tema num tamanho do Figma.

    Args:
        tamanho: tamanho da fonte em px do Figma (padrão TEXTO = 65).

    Returns:
        (família, -tamanho_em_pixels). No tkinter, tamanho negativo significa
        pixels; positivo seria pontos.
    """
    return (_familia, -max(1, round(px(tamanho) * _fator_fonte)))


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

    def retangulo(self, x: float, y: float, largura: float, altura: float, raio: float, cor: str,
                  tags: str | tuple = ()) -> int:
        """Desenha um retângulo de cantos arredondados.

        É um polígono cujos cantos são quartos de círculo, calculados de 15 em
        15 graus (raio 0 = cantos retos).

        Args:
            x: esquerda, em px do Figma.
            y: topo, em px do Figma.
            largura: largura em px do Figma.
            altura: altura em px do Figma.
            raio: raio dos cantos em px do Figma.
            cor: cor de preenchimento e de contorno.
            tags: tags do tkinter (para agrupar itens clicáveis).

        Returns:
            O id do item no Canvas.
        """
        x1, y1, x2, y2, r = px(x), px(y), px(x + largura), px(y + altura), px(raio)
        if r == 0:
            return self.create_rectangle(x1, y1, x2, y2, fill=cor, outline=cor, tags=tags)
        pontos = []
        cantos = ((x2 - r, y1 + r, -90), (x2 - r, y2 - r, 0), (x1 + r, y2 - r, 90), (x1 + r, y1 + r, 180))
        for cx, cy, angulo_inicial in cantos:               # sentido horário, começando no topo-direita
            for passo in range(7):                          # 0°, 15°, ..., 90° de cada canto
                angulo = math.radians(angulo_inicial + 15 * passo)
                pontos += [cx + r * math.cos(angulo), cy + r * math.sin(angulo)]
        return self.create_polygon(pontos, fill=cor, outline=cor, tags=tags)

    def circulo(self, x: float, y: float, diametro: float, cor: str, tags: str | tuple = ()) -> int:
        """Desenha um círculo preenchido.

        Args:
            x: esquerda, em px do Figma.
            y: topo, em px do Figma.
            diametro: diâmetro em px do Figma.
            cor: cor do círculo.
            tags: tags do tkinter.

        Returns:
            O id do item no Canvas.
        """
        return self.create_oval(px(x), px(y), px(x + diametro), px(y + diametro), fill=cor, outline=cor, tags=tags)

    def texto(self, x: float, y: float, texto: str, tamanho: float = TEXTO, cor: str = ESCURO,
              ancora: str = "nw", tags: str | tuple = ()) -> int:
        """Escreve um texto na fonte do tema.

        Args:
            x: posição horizontal, em px do Figma.
            y: posição vertical, em px do Figma.
            texto: o que escrever.
            tamanho: tamanho da fonte em px do Figma.
            cor: cor do texto.
            ancora: ponto do texto que fica em (x, y): "nw" canto superior
                esquerdo, "center" meio, "ne" canto superior direito...
            tags: tags do tkinter.

        Returns:
            O id do item no Canvas (para trocar o texto depois com itemconfig).
        """
        return self.create_text(px(x), px(y), text=texto, fill=cor, font=fonte(tamanho), anchor=ancora, tags=tags)

    def icone(self, nome: str, x: float, y: float, largura: float, altura: float, cor: str,
              espessura: float = 3.5, tags: str | tuple = ()) -> None:
        """Desenha um ícone de ICONES dentro de uma caixa do Figma.

        Args:
            nome: chave em ICONES ("upload", "nuvem", "alto_falante", "tocar", "pausar").
            x: esquerda da caixa, em px do Figma.
            y: topo da caixa, em px do Figma.
            largura: largura da caixa.
            altura: altura da caixa.
            cor: cor do traço.
            espessura: espessura do traço em px do Figma.
            tags: tags do tkinter.
        """
        def ponto(a: float, b: float) -> tuple[int, int]:
            """Converte um ponto da grade 24x24 do ícone em pixels da tela."""
            return px(x + a * largura / 24), px(y + b * altura / 24)

        traco = max(1, px(espessura))
        for tipo, *dados in ICONES[nome]:
            if tipo == "linha":
                pontos = [c for a, b in dados for c in ponto(a, b)]
                self.create_line(pontos, fill=cor, width=traco, capstyle="round", joinstyle="round", tags=tags)
            elif tipo == "circulo":
                cx, cy, r = dados
                self.create_oval(*ponto(cx - r, cy - r), *ponto(cx + r, cy + r), outline=cor, width=traco, tags=tags)
            else:  # arco
                cx, cy, r, inicio, extensao = dados
                self.create_arc(*ponto(cx - r, cy - r), *ponto(cx + r, cy + r), start=inicio, extent=extensao,
                                style="arc", outline=cor, width=traco, tags=tags)

    def pintar(self, item: int, cor: str) -> None:
        """Troca a cor de uma forma (ex.: aba de voz selecionada).

        Args:
            item: id do item no Canvas.
            cor: nova cor de preenchimento e de contorno.
        """
        self.itemconfig(item, fill=cor, outline=cor)

    def widget(self, x: float, y: float, largura: float, altura: float, widget: tk.Widget) -> int:
        """Coloca um widget do tkinter (ex.: tk.Text) na posição do Figma.

        Args:
            x: esquerda, em px do Figma.
            y: topo, em px do Figma.
            largura: largura em px do Figma.
            altura: altura em px do Figma.
            widget: o widget a posicionar.

        Returns:
            O id da janela no Canvas.
        """
        return self.create_window(px(x), px(y), window=widget, anchor="nw", width=px(largura), height=px(altura))

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

    def botao(self, x: float, y: float, largura: float, altura: float, texto: str,
              comando: Callable[[], None], cor: str = ESCURO, raio: float = 22) -> tuple[int, int]:
        """Desenha um botão arredondado com texto creme no meio.

        cor=ESCURO é o botão principal; cor=FUNDO é a pílula secundária.

        Args:
            x: esquerda, em px do Figma.
            y: topo, em px do Figma.
            largura: largura em px do Figma.
            altura: altura em px do Figma.
            texto: rótulo do botão.
            comando: função chamada no clique.
            cor: cor do fundo.
            raio: raio dos cantos.

        Returns:
            (id do fundo, id do texto), para mudar a cor ou o texto depois.
        """
        tag = self.nova_tag()
        fundo = self.retangulo(x, y, largura, altura, raio, cor, tags=tag)
        rotulo = self.texto(x + largura / 2, y + altura / 2, texto, cor=PAINEL, ancora="center", tags=tag)
        self.tornar_clicavel(tag, comando)
        return fundo, rotulo


class Deslizador:
    """Barra de volume do Figma: trilho fino + bolinha escura que se arrasta.

    Attributes:
        DIAMETRO: diâmetro da bolinha em px do Figma.
    """

    DIAMETRO = 24

    def __init__(self, desenho: Desenho, x: float, y: float, largura: float, minimo: int, maximo: int,
                 comando: Callable[[int], None]) -> None:
        """Desenha o deslizador e liga clique e arrasto.

        Args:
            desenho: Canvas onde desenhar.
            x: início do trilho, em px do Figma.
            y: topo do trilho, em px do Figma.
            largura: comprimento do trilho.
            minimo: valor na ponta esquerda.
            maximo: valor na ponta direita.
            comando: função chamada com o novo valor quando o usuário arrasta.
        """
        self.desenho = desenho
        self.x, self.largura = x, largura
        self.centro_y = y + 3.5
        self.minimo, self.maximo = minimo, maximo
        self.comando = comando
        tag = desenho.nova_tag()
        desenho.retangulo(x - 15, y - 20, largura + 30, 47, 0, PAINEL, tags=tag)   # área de clique maior
        desenho.retangulo(x, y, largura, 7, 3.5, FUNDO, tags=tag)                  # trilho
        self.bolinha = desenho.create_oval(0, 0, 0, 0, fill=ESCURO, outline=ESCURO, tags=tag)
        desenho.tag_bind(tag, "<Button-1>", self._ao_arrastar)
        desenho.tag_bind(tag, "<B1-Motion>", self._ao_arrastar)
        desenho.tag_bind(tag, "<Enter>", lambda evento: desenho.config(cursor="hand2"))
        desenho.tag_bind(tag, "<Leave>", lambda evento: desenho.config(cursor=""))

    def set(self, valor: int) -> None:
        """Move a bolinha para a posição do valor (não chama o comando).

        Args:
            valor: valor entre mínimo e máximo.
        """
        fracao = min(1.0, max(0.0, (valor - self.minimo) / (self.maximo - self.minimo)))
        cx, r = self.x + fracao * self.largura, self.DIAMETRO / 2
        self.desenho.coords(self.bolinha, px(cx - r), px(self.centro_y - r), px(cx + r), px(self.centro_y + r))

    def _ao_arrastar(self, evento: tk.Event) -> None:
        """Converte a posição do mouse em valor, move a bolinha e chama o comando.

        Args:
            evento: clique ou movimento do mouse (usa evento.x).
        """
        fracao = (evento.x - px(self.x)) / px(self.largura)
        fracao = min(1.0, max(0.0, fracao))
        valor = round(self.minimo + fracao * (self.maximo - self.minimo))
        self.set(valor)
        self.comando(valor)
