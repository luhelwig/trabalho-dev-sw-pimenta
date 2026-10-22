"""NOVA (Fase 2): fachada usada pela interface."""

from pathlib import Path

from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CatalogoInstrumentos, Instrumento
from gerador_musical.saida.exportador import Exportador
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador


class ControladorAplicacao:
    """Único ponto de contato entre a interface e o resto do sistema.

    As telas só chamam métodos daqui e tratam GeradorMusicalErro para
    mostrar mensagens. Assim, trocar a interface (tkinter -> web, por
    exemplo) não exige mexer na interpretação (requisito não-funcional).

    Todas as dependências chegam prontas pelo construtor (montadas em
    main.criar_aplicacao), o que permite testar com versões falsas.
    """

    def __init__(
        self,
        entrada: EntradaUsuario,
        parser: Parser,
        configuracao: ConfiguracaoInicial,
        sintetizador: Sintetizador,
        player: Player,
        exportador: Exportador,
        catalogo: CatalogoInstrumentos,
    ) -> None:
        self._entrada = entrada
        self._parser = parser
        self._configuracao = configuracao
        self._sintetizador = sintetizador
        self._player = player
        self._exportador = exportador
        self._catalogo = catalogo

    # ---- Texto ----------------------------------------------------------

    def atualizar_texto(self, texto: str) -> None:
        raise NotImplementedError

    def carregar_arquivo(self, caminho: Path) -> str:
        """Carrega o .txt e devolve o texto para a tela exibir no campo."""
        raise NotImplementedError

    def salvar_texto(self, caminho: Path | None = None) -> Path:
        """Salva o texto (sobrescreve o original se veio de arquivo)."""
        raise NotImplementedError

    def texto_veio_de_arquivo(self) -> bool:
        raise NotImplementedError

    def limpar(self) -> None:
        """Nova composição: para a música, esvazia o texto e a partitura."""
        raise NotImplementedError

    # ---- Geração --------------------------------------------------------

    def gerar_musica(self) -> None:
        """Valida a entrada, interpreta, sintetiza e carrega no Player.

        Raises:
            TextoVazioErro, FormatoInvalidoErro
        """
        raise NotImplementedError

    def regerar_com_novos_parametros(self) -> None:
        """Usa os tokens já lidos (Parser.token_to_partitura), sem
        reinterpretar o texto, aplicando a ConfiguracaoInicial atual."""
        raise NotImplementedError

    def musica_foi_gerada(self) -> bool:
        raise NotImplementedError

    # ---- Reprodução -----------------------------------------------------

    def tocar(self) -> None:
        raise NotImplementedError

    def pausar(self) -> None:
        raise NotImplementedError

    def retomar(self) -> None:
        raise NotImplementedError

    def parar(self) -> None:
        raise NotImplementedError

    def reproducao_terminou(self) -> bool:
        raise NotImplementedError

    # ---- Exportação -----------------------------------------------------

    def exportar_midi(self, destino: Path | None = None) -> Path:
        """Raises: MusicaNaoGeradaErro"""
        raise NotImplementedError

    # ---- Configuração (bloco de parâmetros da tela principal) -----------

    def listar_instrumentos(self) -> list[Instrumento]:
        raise NotImplementedError

    def get_bpm(self) -> int:
        raise NotImplementedError

    def set_bpm(self, bpm: int) -> None:
        raise NotImplementedError

    def get_instrumento_voz(self, indice_voz: int) -> int:
        raise NotImplementedError

    def set_instrumento_voz(self, indice_voz: int, programa: int) -> None:
        raise NotImplementedError

    def get_oitava_voz(self, indice_voz: int) -> int:
        raise NotImplementedError

    def set_oitava_voz(self, indice_voz: int, oitava: int) -> None:
        raise NotImplementedError

    def get_volume_voz(self, indice_voz: int) -> int:
        raise NotImplementedError

    def set_volume_voz(self, indice_voz: int, volume: int) -> None:
        raise NotImplementedError
