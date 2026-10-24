"""NOVA (Fase 2): valores iniciais da música, configuráveis pela interface."""

from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.instrumentos import CRAVO, FAGOTE, ORGAO_DE_IGREJA, PIANO
from gerador_musical.musica.limites import BPM_MAXIMO, BPM_MINIMO, OITAVA_MAXIMA, OITAVA_MINIMA, PROGRAMA_MIDI_MAXIMO, PROGRAMA_MIDI_MINIMO, VOLUME_MAXIMO, VOLUME_MINIMO
BPM_PADRAO = 120
INSTRUMENTOS_PADRAO = (CRAVO, ORGAO_DE_IGREJA, PIANO, FAGOTE)
OITAVAS_PADRAO = (6, 5, 4, 3)
VOLUMES_PADRAO = (100, 80, 60, 40)

class ConfiguracaoInicial:
    """Valores com que a música começa: BPM global + padrões por voz.

    Padrões dos requisitos (a partir de V4 o ciclo se repete):

        voz  oitava  volume  instrumento
        V0   6       100     Cravo
        V1   5       80      Órgão
        V2   4       60      Piano
        V3   3       40      Fagote

    A interface altera ESTA classe (ex.: usuário troca o instrumento de V1
    no dropdown). O Parser só lê dela. Assim, mudar parâmetros não exige
    mudar o processamento do texto (requisito não-funcional).
    """

    TAMANHO_DO_CICLO = 4

    def __init__(self, bpm_inicial: int) -> None:
        self.bpm_inicial: int = bpm_inicial
        self._instrumentos: list[int] = []
        self._oitavas: list[int] = []
        self._volumes: list[int] = []
        self._carregar_padroes()

    def _carregar_padroes(self) -> None:
        """Copia os valores padrão dos requisitos para as listas por voz."""
        self._instrumentos = list(INSTRUMENTOS_PADRAO)
        self._oitavas = list(OITAVAS_PADRAO)
        self._volumes = list(VOLUMES_PADRAO)

    @staticmethod
    def _validar(valor: int, minimo: int, maximo: int, nome: str) -> None:
        """Levanta ValueError se o valor estiver fora de [minimo, maximo]."""
        if not minimo <= valor <= maximo:
            raise ValueError(f"{nome} fora de {minimo}–{maximo}: {valor}")

    @classmethod
    def padrao(cls) -> "ConfiguracaoInicial":
        """Configuração com os valores padrão dos requisitos.
        """
        return cls(BPM_PADRAO)

    # ---- BPM (global) ---------------------------------------------------

    def get_bpm_inicial(self) -> int:
        return self.bpm_inicial

    def set_bpm_inicial(self, bpm: int) -> None:
        """Raises: ValueError fora de [BPM_MINIMO, BPM_MAXIMO]."""
        self._validar(bpm, BPM_MINIMO, BPM_MAXIMO, "BPM")
        self.bpm_inicial = bpm

    # ---- Por voz --------------------------------------------------------

    def get_instrumento_inicial(self, indice_voz: int) -> int:
        """Instrumento inicial da voz, ciclando a cada TAMANHO_DO_CICLO vozes."""
        return self._instrumentos[self._indice_no_ciclo(indice_voz)]

    def set_instrumento_inicial(self, indice_voz: int, programa: int) -> None:
        self._validar(programa, PROGRAMA_MIDI_MINIMO, PROGRAMA_MIDI_MAXIMO, "Instrumento")
        self._instrumentos[self._indice_no_ciclo(indice_voz)] = programa

    def get_oitava_inicial(self, indice_voz: int) -> int:
        return self._oitavas[self._indice_no_ciclo(indice_voz)]

    def set_oitava_inicial(self, indice_voz: int, oitava: int) -> None:
        self._validar(oitava, OITAVA_MINIMA, OITAVA_MAXIMA, "Oitava")
        self._oitavas[self._indice_no_ciclo(indice_voz)] = oitava

    def get_volume_inicial(self, indice_voz: int) -> int:
        return self._volumes[self._indice_no_ciclo(indice_voz)]

    def set_volume_inicial(self, indice_voz: int, volume: int) -> None:
        self._validar(volume, VOLUME_MINIMO, VOLUME_MAXIMO, "Volume")
        self._volumes[self._indice_no_ciclo(indice_voz)] = volume

    def criar_parametros(self, indice_voz: int) -> ParametrosMusica:
        """Fábrica: ParametrosMusica novo com os valores iniciais da voz."""
        return ParametrosMusica(
            self.get_instrumento_inicial(indice_voz),
            self.get_oitava_inicial(indice_voz),
            self.get_volume_inicial(indice_voz),
        )

    def restaurar_padroes(self) -> None:
        """Desfaz as alterações feitas pelo usuário."""
        self._carregar_padroes()

    def _indice_no_ciclo(self, indice_voz: int) -> int:
        return indice_voz % self.TAMANHO_DO_CICLO
