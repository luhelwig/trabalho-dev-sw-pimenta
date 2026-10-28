"""Classe ParametrosMusica (Fase 1, adaptada na Fase 2).

Mudança em relação à Fase 1: agora existe um ParametrosMusica por voz,
porque oitava, volume e instrumento são próprios de cada linha. O BPM
saiu daqui: ele é global (fica em ConfiguracaoInicial e Partitura).
"""

from gerador_musical.musica.limites import OITAVA_MAXIMA, OITAVA_MINIMA, PROGRAMA_MIDI_MAXIMO, PROGRAMA_MIDI_MINIMO, VOLUME_MAXIMO

class ParametrosMusica:
    """Estado dos parâmetros de UMA voz enquanto o texto é interpretado.

    "padrao"/"inicial" é o valor com que a voz começou (vem da
    ConfiguracaoInicial); "atual" é o valor depois dos comandos do texto.

    Attributes:
        instrumento_inicial: programa MIDI com que a voz começou.
        instrumento_atual: programa MIDI em uso.
        oitava_padrao: oitava com que a voz começou.
        oitava_atual: oitava em uso.
        volume_padrao: volume com que a voz começou.
        volume_atual: volume em uso (0–127).
    """

    def __init__(self, instrumento_inicial: int, oitava_padrao: int, volume_padrao: int) -> None:
        """Cria os parâmetros com os valores atuais iguais aos iniciais.

        Args:
            instrumento_inicial: programa MIDI inicial (0–127).
            oitava_padrao: oitava inicial (0–8).
            volume_padrao: volume inicial (0–127).
        """
        self.instrumento_inicial: int = instrumento_inicial
        self.instrumento_atual: int = instrumento_inicial
        self.oitava_padrao: int = oitava_padrao
        self.oitava_atual: int = oitava_padrao
        self.volume_padrao: int = volume_padrao
        self.volume_atual: int = volume_padrao

    # ---- Volume ---------------------------------------------------------

    def dobrar_volume(self) -> None:
        """Comando espaço: dobra o volume, sem passar de VOLUME_MAXIMO (127)."""
        self.volume_atual = min((self.volume_atual * 2), VOLUME_MAXIMO)

    def reset_volume(self) -> None:
        """Volta o volume ao valor inicial da voz."""
        self.volume_atual = self.volume_padrao

    def get_volume(self) -> int:
        """Devolve o volume atual (0–127)."""
        return self.volume_atual

    # ---- Oitava ---------------------------------------------------------

    def incrementar_oitava(self) -> None:
        """Comando '?': sobe uma oitava.

        Se passar de OITAVA_MAXIMA, volta à oitava padrão da voz (regra da
        Fase 1).
        """
        if self.oitava_atual + 1 > OITAVA_MAXIMA:
            self.reset_oitava()
        else:
            self.oitava_atual += 1


    def decrementar_oitava(self) -> None:
        """NOVO — comando 'V': desce uma oitava.

        Se ficar abaixo de OITAVA_MINIMA, volta à oitava padrão da voz
        (decisão do grupo, simétrica ao incrementar).
        """
        if self.oitava_atual - 1 < OITAVA_MINIMA:
            self.reset_oitava()
        else:
            self.oitava_atual -= 1

    def reset_oitava(self) -> None:
        """Volta a oitava ao valor inicial da voz."""
        self.oitava_atual = self.oitava_padrao

    def get_oitava(self) -> int:
        """Devolve a oitava atual."""
        return self.oitava_atual

    # ---- Instrumento ----------------------------------------------------

    def set_instrumento(self, midi: int) -> None:
        """Troca o instrumento atual.

        Args:
            midi: programa MIDI do novo instrumento.

        Raises:
            ValueError: programa fora de 0–127.
        """
        if midi < PROGRAMA_MIDI_MINIMO or midi > PROGRAMA_MIDI_MAXIMO:
            raise ValueError(f"Instrumento fora de 0–127: {midi}")
        self.instrumento_atual = midi

    def get_instrumento(self) -> int:
        """Devolve o programa MIDI do instrumento atual."""
        return self.instrumento_atual

    def somar_ao_instrumento(self, quantidade: int) -> None:
        """NOVO (Fase 3) — soma ao instrumento atual; passando de 127, recomeça do 0.

        Antes essa conta ficava na RegraInstrumentoSomaDigito, que pegava o
        instrumento daqui, fazia a conta e devolvia (bad smell "Inveja de
        Recursos"). Quem conhece o limite 0–127 é esta classe.

        Args:
            quantidade: valor a somar (os dígitos pares do texto).
        """
        self.instrumento_atual = (self.instrumento_atual + quantidade) % (PROGRAMA_MIDI_MAXIMO + 1)

    def reset_instrumento(self) -> None:
        """NOVO — volta ao instrumento inicial da voz."""
        self.instrumento_atual = self.instrumento_inicial

    # ---- Geral ----------------------------------------------------------

    def resetar(self) -> None:
        """NOVO — volta volume, oitava e instrumento aos valores iniciais."""
        self.reset_instrumento()
        self.reset_oitava()
        self.reset_volume()
