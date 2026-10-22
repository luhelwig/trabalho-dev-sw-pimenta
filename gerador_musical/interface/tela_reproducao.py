"""Tela de reprodução do croqui: tocar, pausar/retomar, parar, salvar MIDI."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaReproducao(tk.Frame):
    """Só aparece depois de gerar com sucesso.

    Layout (croqui): mensagem "música gerada!", botão "tocar", grupo de
    exportação ("baixar MIDI"), botão "voltar" (ajustar parâmetros e
    gerar de novo sem redigitar o texto).

    NOVO: "pausar/retomar" e "parar" (requisito de interromper e retomar)
    e aviso de conclusão quando a música termina.
    """

    INTERVALO_VERIFICACAO_MS = 200

    def __init__(self, app: App) -> None:
        super().__init__(app)
        self.app: App = app

    def construir(self) -> None:
        raise NotImplementedError

    def _ao_tocar(self) -> None:
        """Toca e agenda _verificar_fim com app.after(...)."""
        raise NotImplementedError

    def _ao_pausar_ou_retomar(self) -> None:
        raise NotImplementedError

    def _ao_parar(self) -> None:
        raise NotImplementedError

    def _ao_baixar_midi(self) -> None:
        """controlador.exportar_midi() e mostrar onde o arquivo foi salvo."""
        raise NotImplementedError

    def _ao_voltar(self) -> None:
        raise NotImplementedError

    def _verificar_fim(self) -> None:
        """Se a música terminou, mostra a mensagem de conclusão;
        senão, reagenda a si mesmo (não bloqueia a interface)."""
        raise NotImplementedError
