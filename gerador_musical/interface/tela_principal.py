"""Tela principal do croqui: texto + parâmetros + gerar/limpar."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaPrincipal(tk.Frame):
    """Layout (croqui):
      - ícone de upload no canto superior esquerdo -> tela de carregamento;
      - campo de texto em destaque (multilinha: cada linha é uma voz);
      - bloco de configurações: BPM (+/-), e por voz: instrumento
        (dropdown), oitava (+/-), volume;
      - botões "gerar música" e "limpar" fixos embaixo.

    NOVO na Fase 2 (atualizar também o croqui no Figma):
      - seletor de voz (V0–V3) no bloco de configurações, pois oitava,
        volume e instrumento agora são por voz;
      - botão "salvar texto" (Mudança 1), habilitado quando o texto
        veio de arquivo e foi modificado.
    """

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self.app: App = app
        self.voz_selecionada: tk.IntVar | None = None
        self.campo_texto: tk.Text | None = None

    def construir(self) -> None:
        raise NotImplementedError

    # ---- Construção -----------------------------------------------------

    def _construir_barra_superior(self) -> None:
        """Botão de upload."""
        raise NotImplementedError

    def _construir_campo_texto(self) -> None:
        raise NotImplementedError

    def _construir_bloco_configuracao(self) -> None:
        raise NotImplementedError

    def _construir_botoes(self) -> None:
        """"gerar música", "limpar", "salvar texto"."""
        raise NotImplementedError

    # ---- Eventos --------------------------------------------------------

    def _ao_abrir_carregamento(self) -> None:
        raise NotImplementedError

    def _ao_gerar(self) -> None:
        """Passa o texto ao controlador, gera; se ok, vai para reprodução.
        Em GeradorMusicalErro, mostra a mensagem."""
        raise NotImplementedError

    def _ao_limpar(self) -> None:
        raise NotImplementedError

    def _ao_salvar_texto(self) -> None:
        raise NotImplementedError

    def _ao_trocar_voz(self) -> None:
        """Atualiza os controles com os valores da voz selecionada."""
        raise NotImplementedError

    def _ao_mudar_bpm(self, delta: int) -> None:
        raise NotImplementedError

    def _ao_mudar_oitava(self, delta: int) -> None:
        raise NotImplementedError

    def _ao_mudar_volume(self, valor: int) -> None:
        raise NotImplementedError

    def _ao_escolher_instrumento(self, nome: str) -> None:
        raise NotImplementedError

    # ---- Usado por outras telas -----------------------------------------

    def set_texto(self, texto: str) -> None:
        """Preenche o campo (chamado após carregar um .txt)."""
        raise NotImplementedError

    def get_texto(self) -> str:
        raise NotImplementedError
