"""NOVA (Fase 2): valores iniciais da música, configuráveis pela interface.

Constantes com os padrões dos requisitos: BPM_PADRAO, e por voz
INSTRUMENTOS_PADRAO, OITAVAS_PADRAO e VOLUMES_PADRAO.
"""

from gerador_musical.musica.parametros_musica import ParametrosMusica
from gerador_musical.musica.instrumentos import CRAVO, FAGOTE, ORGAO_DE_IGREJA, PIANO
from gerador_musical.musica.limites import BPM_MAXIMO, BPM_MINIMO, OITAVA_MAXIMA, OITAVA_MINIMA, PROGRAMA_MIDI_MAXIMO, PROGRAMA_MIDI_MINIMO, VOLUME_MAXIMO, VOLUME_MINIMO
BPM_PADRAO = 120
INSTRUMENTOS_PADRAO = (CRAVO, ORGAO_DE_IGREJA, PIANO, FAGOTE)
OITAVAS_PADRAO = (6, 5, 4, 3)
VOLUMES_PADRAO = (100, 80, 60, 40)

class ConfiguracaoInicial:
    """Valores com que a música começa: BPM global + padrões por voz.

    Padrões dos requisitos (a partir da voz 4 o ciclo se repete):

        voz  oitava  volume  instrumento
        V0   6       100     Cravo
        V1   5       80      Órgão de igreja
        V2   4       60      Piano
        V3   3       40      Fagote

    A interface altera esta classe (pelo controlador) e o Parser só lê
    dela. Assim, mudar parâmetros não exige reinterpretar o texto
    (requisito não-funcional).

    Attributes:
        bpm_inicial: BPM com que a música começa.
        TAMANHO_DO_CICLO: quantas vozes têm padrões próprios (4).
    """

    TAMANHO_DO_CICLO = 4

    def __init__(self, bpm_inicial: int) -> None:
        """Cria a configuração com o BPM dado e os padrões por voz.

        Args:
            bpm_inicial: BPM com que a música começa.
        """
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
        """Confere se um valor está dentro do intervalo permitido.

        Args:
            valor: valor a conferir.
            minimo: menor valor aceito.
            maximo: maior valor aceito.
            nome: nome do parâmetro, usado na mensagem de erro.

        Raises:
            ValueError: se o valor estiver fora de [minimo, maximo].
        """
        if not minimo <= valor <= maximo:
            raise ValueError(f"{nome} fora de {minimo}–{maximo}: {valor}")

    @classmethod
    def padrao(cls) -> "ConfiguracaoInicial":
        """Cria a configuração com os valores padrão dos requisitos (BPM 120)."""
        return cls(BPM_PADRAO)

    # ---- BPM (global) ---------------------------------------------------

    def get_bpm_inicial(self) -> int:
        """Devolve o BPM com que a música começa."""
        return self.bpm_inicial

    def set_bpm_inicial(self, bpm: int) -> None:
        """Altera o BPM inicial.

        Args:
            bpm: novo BPM.

        Raises:
            ValueError: fora de [BPM_MINIMO, BPM_MAXIMO].
        """
        self._validar(bpm, BPM_MINIMO, BPM_MAXIMO, "BPM")
        self.bpm_inicial = bpm

    # ---- Por voz --------------------------------------------------------

    def get_instrumento_inicial(self, indice_voz: int) -> int:
        """Devolve o instrumento inicial de uma voz.

        Args:
            indice_voz: número da voz (linha do texto, começando em 0). Cicla a
                cada TAMANHO_DO_CICLO vozes.

        Returns:
            Programa MIDI (0–127).
        """
        return self._instrumentos[self._indice_no_ciclo(indice_voz)]

    def set_instrumento_inicial(self, indice_voz: int, programa: int) -> None:
        """Altera o instrumento inicial de uma voz.

        Args:
            indice_voz: número da voz (cicla a cada 4).
            programa: programa MIDI.

        Raises:
            ValueError: programa fora de 0–127.
        """
        self._validar(programa, PROGRAMA_MIDI_MINIMO, PROGRAMA_MIDI_MAXIMO, "Instrumento")
        self._instrumentos[self._indice_no_ciclo(indice_voz)] = programa

    def get_oitava_inicial(self, indice_voz: int) -> int:
        """Devolve a oitava inicial de uma voz.

        Args:
            indice_voz: número da voz (cicla a cada 4).
        """
        return self._oitavas[self._indice_no_ciclo(indice_voz)]

    def set_oitava_inicial(self, indice_voz: int, oitava: int) -> None:
        """Altera a oitava inicial de uma voz.

        Args:
            indice_voz: número da voz (cicla a cada 4).
            oitava: nova oitava.

        Raises:
            ValueError: fora de [OITAVA_MINIMA, OITAVA_MAXIMA].
        """
        self._validar(oitava, OITAVA_MINIMA, OITAVA_MAXIMA, "Oitava")
        self._oitavas[self._indice_no_ciclo(indice_voz)] = oitava

    def get_volume_inicial(self, indice_voz: int) -> int:
        """Devolve o volume inicial de uma voz.

        Args:
            indice_voz: número da voz (cicla a cada 4).
        """
        return self._volumes[self._indice_no_ciclo(indice_voz)]

    def set_volume_inicial(self, indice_voz: int, volume: int) -> None:
        """Altera o volume inicial de uma voz.

        Args:
            indice_voz: número da voz (cicla a cada 4).
            volume: novo volume.

        Raises:
            ValueError: fora de 0–127.
        """
        self._validar(volume, VOLUME_MINIMO, VOLUME_MAXIMO, "Volume")
        self._volumes[self._indice_no_ciclo(indice_voz)] = volume

    def criar_parametros(self, indice_voz: int) -> ParametrosMusica:
        """Fábrica: cria um ParametrosMusica NOVO com os valores iniciais da voz.

        Por ser um objeto novo a cada chamada, os comandos do texto mudam a
        cópia e nunca alteram a configuração.

        Args:
            indice_voz: número da voz (cicla a cada 4).

        Returns:
            Parâmetros prontos para uma Voz.
        """
        return ParametrosMusica(
            self.get_instrumento_inicial(indice_voz),
            self.get_oitava_inicial(indice_voz),
            self.get_volume_inicial(indice_voz),
        )

    def restaurar_padroes(self) -> None:
        """Desfaz as alterações feitas pelo usuário, voltando aos padrões."""
        self._carregar_padroes()

    def _indice_no_ciclo(self, indice_voz: int) -> int:
        """Converte o número da voz na posição do ciclo (indice_voz % 4)."""
        return indice_voz % self.TAMANHO_DO_CICLO
