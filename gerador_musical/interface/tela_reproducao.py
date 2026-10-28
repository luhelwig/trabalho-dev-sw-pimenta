"""Tela de reprodução do croqui: tocar, pausar/retomar, parar e salvar MIDI."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import TYPE_CHECKING

from gerador_musical.excecoes import GeradorMusicalErro
from gerador_musical.interface import estilo
from gerador_musical.interface.estilo import Caixa, EstiloTexto

if TYPE_CHECKING:
    from gerador_musical.interface.app import App


class TelaReproducao(tk.Frame):
    """Frame "Gerador de musica" do Figma. Só aparece depois de gerar.

    Layout: "música gerada!", botão "baixar midi" (vai para Downloads),
    pílula "salvar como..." (escolher onde), botão de play e "voltar"
    (ajustar parâmetros e gerar de novo sem redigitar o texto).

    NOVO na Fase 2 (requisito de interromper e retomar): o play vira
    pausar/retomar enquanto toca, pílula "parar", estado no canto
    ("tocando...", "pausada", "fim") e aviso quando a música termina.

    Attributes:
        INTERVALO_VERIFICACAO_MS: de quanto em quanto tempo conferir se a
            música acabou.
    """

    INTERVALO_VERIFICACAO_MS = 200
    LARGURA, ALTURA = 813, 586
    TAG_ICONE_PLAY = "icone_play"

    def __init__(self, app: App) -> None:
        """Cria a tela parada, ainda sem widgets (eles nascem em construir()).

        Args:
            app: janela principal.
        """
        super().__init__(app, bg=estilo.FUNDO)
        self.app: App = app
        self.desenho: estilo.Desenho | None = None
        self._tocando: bool = False
        self._pausado: bool = False
        self._id_verificacao: str | None = None

    def construir(self) -> None:
        """Desenha a tela: estado, "baixar midi", "salvar como...", play, "parar" e "voltar"."""
        d = self.desenho = estilo.Desenho(self, self.LARGURA, self.ALTURA)
        d.pack()
        d.retangulo(Caixa(24, 21, 764, 545), estilo.CARTAO, raio=57)
        d.texto(406, 21, "gerador de música", estilo.ESTILO_TITULO)
        d.texto(55, 153, "música gerada!")
        self.rotulo_estado = d.texto(757, 160, "", EstiloTexto(50, estilo.FUNDO, "ne"))
        d.retangulo(Caixa(49, 234, 715, 298), estilo.PAINEL, raio=25)

        d.botao(Caixa(66, 261, 265, 76), "baixar midi", self._ao_baixar_midi)
        d.botao(Caixa(74, 361, 324, 47), "salvar como...", self._ao_salvar_midi_como, cor=estilo.FUNDO, raio=23)

        # círculo e pílula fazem a mesma coisa: tocar / pausar / retomar
        self._tag_play = d.nova_tag()
        d.circulo(Caixa(74, 435, 70, 70), estilo.ESCURO, tags=self._tag_play)
        d.tornar_clicavel(self._tag_play, self._ao_tocar_ou_pausar)
        _, self.rotulo_play = d.botao(Caixa(163, 439, 180, 58), "", self._ao_tocar_ou_pausar, cor=estilo.FUNDO, raio=29)
        d.botao(Caixa(357, 439, 130, 58), "parar", self._ao_parar, cor=estilo.FUNDO, raio=29)

        d.botao(Caixa(581, 433, 158, 76), "voltar", self._ao_voltar)
        self._mostrar_estado("pronta para tocar")

    # ---- Eventos --------------------------------------------------------

    def _ao_tocar_ou_pausar(self) -> None:
        """Botão de play: parada -> toca; tocando -> pausa; pausada -> retoma."""
        if self._tocando:
            self._ao_pausar_ou_retomar()
        else:
            self._ao_tocar()

    def _ao_tocar(self) -> None:
        """Toca e agenda _verificar_fim com after(), sem travar a janela.

        Em GeradorMusicalErro (ex.: computador sem som MIDI), mostra a mensagem.
        """
        try:
            self.app.controlador.tocar()
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        ja_estava_verificando = self._tocando
        self._tocando = True
        self._pausado = False
        self._mostrar_estado("tocando...")
        if not ja_estava_verificando:           # evita duas verificações em paralelo
            self._id_verificacao = self.after(self.INTERVALO_VERIFICACAO_MS, self._verificar_fim)

    def _ao_pausar_ou_retomar(self) -> None:
        """Alterna entre pausar e retomar (só se estiver tocando)."""
        if not self._tocando:
            return
        if self._pausado:
            self.app.controlador.retomar()
        else:
            self.app.controlador.pausar()
        self._pausado = not self._pausado
        self._mostrar_estado("pausada" if self._pausado else "tocando...")

    def _ao_parar(self) -> None:
        """Para a música e zera os estados."""
        if self._id_verificacao is not None:    # cancela a verificação agendada
            self.after_cancel(self._id_verificacao)
            self._id_verificacao = None
        self.app.controlador.parar()
        self._tocando = False
        self._pausado = False
        self._mostrar_estado("parada")

    def _ao_baixar_midi(self) -> None:
        """Clique em "baixar midi": salva em Downloads com o nome padrão."""
        self._exportar_midi(None)

    def _ao_salvar_midi_como(self) -> None:
        """Clique em "salvar como...": deixa o usuário escolher pasta e nome."""
        nome = filedialog.asksaveasfilename(defaultextension=".mid", filetypes=[("MIDI", "*.mid")])
        if not nome:                            # usuário cancelou
            return
        self._exportar_midi(Path(nome))

    def _exportar_midi(self, destino: Path | None) -> None:
        """Exporta o MIDI e mostra onde salvou, ou o erro.

        Args:
            destino: caminho escolhido; None para Downloads com o nome padrão.
        """
        try:
            caminho = self.app.controlador.exportar_midi(destino)
        except GeradorMusicalErro as erro:
            self.app.mostrar_erro(str(erro))
            return
        self.app.mostrar_info(f"MIDI salvo em {caminho}")

    def _ao_voltar(self) -> None:
        """Para a música e volta para a tela principal."""
        self._ao_parar()
        self._mostrar_estado("pronta para tocar")
        self.app.mostrar_tela("principal")

    def _verificar_fim(self) -> None:
        """Confere se a música acabou; se não, agenda a si mesma de novo.

        Quando acaba, mostra "fim" e avisa o usuário. Usar after() em vez de um
        laço while mantém a janela respondendo enquanto a música toca.
        """
        self._id_verificacao = None             # este agendamento já disparou
        if not self._tocando:
            return
        if self.app.controlador.reproducao_terminou():
            self._ao_parar()
            self._mostrar_estado("fim")
            self.app.mostrar_info("Fim da música.")
        else:
            self._id_verificacao = self.after(self.INTERVALO_VERIFICACAO_MS, self._verificar_fim)

    # ---- Aparência ------------------------------------------------------

    def _mostrar_estado(self, texto: str) -> None:
        """Escreve o estado no canto e ajusta o botão de play.

        O texto vira "tocar", "pausar" ou "retomar", e o ícone vira play ou
        pausa.

        Args:
            texto: estado a mostrar (ex.: "tocando...").
        """
        d = self.desenho
        d.itemconfig(self.rotulo_estado, text=texto)
        tocando_agora = self._tocando and not self._pausado
        if tocando_agora:
            acao = "pausar"
        elif self._pausado:
            acao = "retomar"
        else:
            acao = "tocar"
        d.itemconfig(self.rotulo_play, text=acao)
        d.delete(self.TAG_ICONE_PLAY)
        d.icone("pausar" if tocando_agora else "tocar", Caixa(81, 442, 55, 55), estilo.PAINEL,
                tags=(self._tag_play, self.TAG_ICONE_PLAY))
