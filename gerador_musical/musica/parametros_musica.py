"""Classe ParametrosMusica (Fase 1, adaptada na Fase 2).

MUDANÇA EM RELAÇÃO À FASE 1: agora existe UM ParametrosMusica POR VOZ,
porque oitava, volume e instrumento são próprios de cada linha.
O BPM saiu daqui: ele é global (vive em ConfiguracaoInicial/Partitura).
"""


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
        raise NotImplementedError

    def reset_volume(self) -> None:
        raise NotImplementedError

    def get_volume(self) -> int:
        raise NotImplementedError

    # ---- Oitava ---------------------------------------------------------

    def incrementar_oitava(self) -> None:
        """Comando '?': sobe uma oitava em relação à atual.

        Regra da Fase 1: se não puder subir (passa de OITAVA_MAXIMA),
        volta à oitava padrão da voz.
        """
        raise NotImplementedError

    def decrementar_oitava(self) -> None:
        """NOVO — comando 'V': desce uma oitava.

        TODO (decisão do grupo): o que fazer abaixo de OITAVA_MINIMA
        (sugestão: simétrico ao incrementar — volta à padrão).
        """
        raise NotImplementedError

    def reset_oitava(self) -> None:
        raise NotImplementedError

    def get_oitava(self) -> int:
        raise NotImplementedError

    # ---- Instrumento ----------------------------------------------------

    def set_instrumento(self, midi: int) -> None:
        """Troca o instrumento atual (programa MIDI 0–127).

        TODO (decisão do grupo): o que fazer com valor fora de 0–127
        (ex.: regra do dígito par somando além de 127).
        """
        raise NotImplementedError

    def get_instrumento(self) -> int:
        raise NotImplementedError

    def reset_instrumento(self) -> None:
        """NOVO — volta ao instrumento inicial da voz."""
        raise NotImplementedError

    # ---- Geral ----------------------------------------------------------

    def resetar(self) -> None:
        """NOVO — volta volume, oitava e instrumento aos valores iniciais."""
        raise NotImplementedError
