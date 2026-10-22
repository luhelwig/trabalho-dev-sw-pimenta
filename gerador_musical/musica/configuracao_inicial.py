"""NOVA (Fase 2): valores iniciais da música, configuráveis pela interface."""

from gerador_musical.musica.parametros_musica import ParametrosMusica


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
        # TODO: preencher com a tabela acima (um valor por voz do ciclo).
        self._instrumentos: list[int] = []
        self._oitavas: list[int] = []
        self._volumes: list[int] = []

    @classmethod
    def padrao(cls) -> "ConfiguracaoInicial":
        """Configuração com os valores padrão dos requisitos.

        TODO (decisão do grupo): BPM inicial padrão (ex.: 120).
        """
        raise NotImplementedError

    # ---- BPM (global) ---------------------------------------------------

    def get_bpm_inicial(self) -> int:
        raise NotImplementedError

    def set_bpm_inicial(self, bpm: int) -> None:
        """Raises: ValueError fora de [BPM_MINIMO, BPM_MAXIMO]."""
        raise NotImplementedError

    # ---- Por voz --------------------------------------------------------

    def get_instrumento_inicial(self, indice_voz: int) -> int:
        """Instrumento inicial da voz, ciclando a cada TAMANHO_DO_CICLO vozes."""
        raise NotImplementedError

    def set_instrumento_inicial(self, indice_voz: int, programa: int) -> None:
        raise NotImplementedError

    def get_oitava_inicial(self, indice_voz: int) -> int:
        raise NotImplementedError

    def set_oitava_inicial(self, indice_voz: int, oitava: int) -> None:
        raise NotImplementedError

    def get_volume_inicial(self, indice_voz: int) -> int:
        raise NotImplementedError

    def set_volume_inicial(self, indice_voz: int, volume: int) -> None:
        raise NotImplementedError

    def criar_parametros(self, indice_voz: int) -> ParametrosMusica:
        """Fábrica: ParametrosMusica novo com os valores iniciais da voz."""
        raise NotImplementedError

    def restaurar_padroes(self) -> None:
        """Desfaz as alterações feitas pelo usuário."""
        raise NotImplementedError

    def _indice_no_ciclo(self, indice_voz: int) -> int:
        raise NotImplementedError
