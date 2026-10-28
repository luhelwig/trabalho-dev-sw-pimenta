"""Tema visual da interface, copiado do croqui no Figma: cores, fonte, escala e estilos de texto.

Como funciona:
  - As medidas no código são as do Figma (em px) e passam por px(), que
    multiplica pela escala. Assim dá para conferir cada número no painel
    de propriedades do Figma.
  - A escala é calculada uma vez, para a tela mais alta caber no monitor.
  - O desenho em si (Canvas, botões, ícones, deslizador) fica em desenho.py.

Constantes: as cores do Figma (FUNDO, CARTAO, PAINEL, ESCURO, VERMELHO),
a fonte (Micro 5, com Courier New de reserva), os tamanhos de texto
(TITULO, TEXTO) e os estilos de texto prontos (ESTILO_*).

Fase 3: este arquivo juntava cinco assuntos (fonte do sistema, escala,
estilos de texto, desenho e deslizador) e chegou a quase 500 linhas. As ferramentas
de desenho foram para desenho.py. Tamanho, cor e âncora de um texto
viajam juntos num EstiloTexto, em vez de três parâmetros soltos (bad
smell "Lista de Parâmetros Longa").
"""

from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass, replace
from pathlib import Path
from tkinter import font as tkfont

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


@dataclass(frozen=True)
class EstiloTexto:
    """Tamanho, cor e âncora de um texto. Objeto de valor.

    Attributes:
        tamanho: tamanho da fonte em px do Figma.
        cor: cor do texto.
        ancora: ponto do texto que fica na posição dada: "nw" canto superior
            esquerdo, "n" meio de cima, "center" meio, "w" meio da esquerda,
            "ne" canto superior direito.
    """

    tamanho: float = TEXTO
    cor: str = ESCURO
    ancora: str = "nw"

    def com(self, **mudancas) -> EstiloTexto:
        """Devolve uma cópia com alguns campos trocados, ex.: ESTILO_SECUNDARIO.com(ancora="ne")."""
        return replace(self, **mudancas)


# Estilos de texto usados nas telas (como "classes" de CSS)
ESTILO_TITULO = EstiloTexto(tamanho=TITULO, ancora="n")      # "gerador de música"
ESTILO_ROTULO = EstiloTexto()                                # "texto de entrada:", "upload:"
ESTILO_SECUNDARIO = EstiloTexto(cor=FUNDO)                   # rótulos dentro dos painéis
ESTILO_BOTAO = EstiloTexto(cor=PAINEL, ancora="center")      # texto no meio de botões e pílulas
ESTILO_VALOR = EstiloTexto(cor=PAINEL, ancora="w")           # valor à esquerda de uma pílula
