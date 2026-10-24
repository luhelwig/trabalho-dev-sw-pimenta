"""Classe ParametrosMusica (Fase 1, adaptada na Fase 2).

MUDANÇA EM RELAÇÃO À FASE 1: agora existe UM ParametrosMusica POR VOZ,
porque oitava, volume e instrumento são próprios de cada linha.
O BPM saiu daqui: ele é global (vive em ConfiguracaoInicial/Partitura).
"""

from gerador_musical.musica.limites import OITAVA_MAXIMA, OITAVA_MINIMA, PROGRAMA_MIDI_MAXIMO, PROGRAMA_MIDI_MINIMO, VOLUME_MAXIMO

class ParametrosMusica:
    """Estado mutável dos parâmetros de UMA voz durante a interpretação.

    "padrao"/"inicial" = valor com que a voz começou (vem de
    ConfiguracaoInicial); "atual" = valor depois dos comandos do texto.
    """

    def __init__(self, instrumento_inicial: int, oitava_padrao: int, volume_padrao: int) -> None:
        self.instrumento_inicial: int = instrumento_inicial
        self.instrumento_atual: int = instrumento_inicial
        self.oitava_padrao: int = oitava_padrao
        self.oitava_atual: int = oitava_padrao
        self.volume_padrao: int = volume_padrao
        self.volume_atual: int = volume_padrao

    # ---- Volume ---------------------------------------------------------

    def dobrar_volume(self) -> None:
        """Dobra o volume; se passar de VOLUME_MAXIMO, fica no máximo."""
        self.volume_atual = min((self.volume_atual * 2), VOLUME_MAXIMO)

    def reset_volume(self) -> None:
        self.volume_atual = self.volume_padrao

    def get_volume(self) -> int:
        return self.volume_atual

    # ---- Oitava ---------------------------------------------------------

    def incrementar_oitava(self) -> None:
        """Comando '?': sobe uma oitava em relação à atual.

        Regra da Fase 1: se não puder subir (passa de OITAVA_MAXIMA),
        volta à oitava padrão da voz.
        """
        if self.oitava_atual + 1 > OITAVA_MAXIMA:
            self.reset_oitava()
        else:
            self.oitava_atual += 1


    def decrementar_oitava(self) -> None:
        """NOVO — comando 'V': desce uma oitava.

        TODO (decisão do grupo): o que fazer abaixo de OITAVA_MINIMA
        (sugestão: simétrico ao incrementar — volta à padrão).
        """
        if self.oitava_atual - 1 < OITAVA_MINIMA:
            self.reset_oitava()
        else:
            self.oitava_atual -= 1

    def reset_oitava(self) -> None:
        self.oitava_atual = self.oitava_padrao

    def get_oitava(self) -> int:
        return self.oitava_atual

    # ---- Instrumento ----------------------------------------------------

    def set_instrumento(self, midi: int) -> None:
        """Troca o instrumento atual (programa MIDI 0–127)."""
        if midi < PROGRAMA_MIDI_MINIMO or midi > PROGRAMA_MIDI_MAXIMO:
            raise ValueError(f"Instrumento fora de 0–127: {midi}")
        self.instrumento_atual = midi

    def get_instrumento(self) -> int:
        return self.instrumento_atual

    def reset_instrumento(self) -> None:
        """NOVO — volta ao instrumento inicial da voz."""
        self.instrumento_atual = self.instrumento_inicial

    # ---- Geral ----------------------------------------------------------

    def resetar(self) -> None:
        """NOVO — volta volume, oitava e instrumento aos valores iniciais."""
        self.reset_instrumento()
        self.reset_oitava()
        self.reset_volume()
