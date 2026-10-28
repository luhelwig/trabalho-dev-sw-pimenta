"""NOVA (Fase 3): fachada das configurações iniciais usada pelo painel da tela principal.

Extraída do ControladorAplicacao (bad smell "Classe Grande"): ele tinha 23
métodos públicos, misturando o fluxo da música com o ajuste de parâmetros.
"""

from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CatalogoInstrumentos, Instrumento


class ControladorConfiguracao:
    """Ponto de contato entre o painel de configurações e os valores iniciais.

    O painel lê e altera o BPM e os parâmetros iniciais de cada voz por aqui,
    sem conhecer a ConfiguracaoInicial. A validação dos limites continua na
    ConfiguracaoInicial, que lança ValueError fora deles.
    """

    def __init__(self, configuracao: ConfiguracaoInicial, catalogo: CatalogoInstrumentos) -> None:
        """Recebe as dependências prontas.

        Args:
            configuracao: valores iniciais (a mesma instância usada pelo Parser).
            catalogo: instrumentos exibidos na tela.
        """
        self._configuracao = configuracao
        self._catalogo = catalogo

    def listar_instrumentos(self) -> list[Instrumento]:
        """Devolve os instrumentos do catálogo, para a lista da tela."""
        return self._catalogo.listar()

    def get_bpm(self) -> int:
        """Devolve o BPM inicial."""
        return self._configuracao.get_bpm_inicial()

    def set_bpm(self, bpm: int) -> None:
        """Altera o BPM inicial.

        Raises:
            ValueError: fora de [BPM_MINIMO, BPM_MAXIMO].
        """
        self._configuracao.set_bpm_inicial(bpm)

    def get_instrumento_voz(self, indice_voz: int) -> int:
        """Devolve o instrumento inicial (programa MIDI) da voz."""
        return self._configuracao.get_instrumento_inicial(indice_voz)

    def set_instrumento_voz(self, indice_voz: int, programa: int) -> None:
        """Altera o instrumento inicial da voz.

        Args:
            indice_voz: número da voz.
            programa: programa MIDI.

        Raises:
            ValueError: programa fora de 0–127.
        """
        self._configuracao.set_instrumento_inicial(indice_voz, programa)

    def get_oitava_voz(self, indice_voz: int) -> int:
        """Devolve a oitava inicial da voz."""
        return self._configuracao.get_oitava_inicial(indice_voz)

    def set_oitava_voz(self, indice_voz: int, oitava: int) -> None:
        """Altera a oitava inicial da voz.

        Args:
            indice_voz: número da voz.
            oitava: nova oitava.

        Raises:
            ValueError: fora de [OITAVA_MINIMA, OITAVA_MAXIMA].
        """
        self._configuracao.set_oitava_inicial(indice_voz, oitava)

    def get_volume_voz(self, indice_voz: int) -> int:
        """Devolve o volume inicial da voz."""
        return self._configuracao.get_volume_inicial(indice_voz)

    def set_volume_voz(self, indice_voz: int, volume: int) -> None:
        """Altera o volume inicial da voz.

        Args:
            indice_voz: número da voz.
            volume: novo volume.

        Raises:
            ValueError: fora de 0–127.
        """
        self._configuracao.set_volume_inicial(indice_voz, volume)
