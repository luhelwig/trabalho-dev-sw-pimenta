"""NOVA (Fase 2): fachada usada pela interface."""

from pathlib import Path

from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.instrumentos import CatalogoInstrumentos, Instrumento
from gerador_musical.musica.partitura import Partitura
from gerador_musical.saida.exportador import Exportador
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador
from gerador_musical.excecoes import FormatoInvalidoErro, MusicaNaoGeradaErro, TextoVazioErro


class ControladorAplicacao:
    """Único ponto de contato entre a interface e o resto do sistema (Fachada).

    As telas só chamam métodos daqui e tratam GeradorMusicalErro para
    mostrar mensagens. Assim, trocar a interface (tkinter -> web, por
    exemplo) não exige mexer na interpretação (requisito não-funcional).

    Todas as dependências chegam prontas pelo construtor (montadas em
    main.criar_controlador), o que permite testar com versões falsas.
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
        """Recebe todas as dependências prontas.

        Args:
            entrada: texto do usuário.
            parser: interpretação do texto.
            configuracao: valores iniciais (a mesma usada pelo Parser).
            sintetizador: conversão da Partitura em MIDI.
            player: reprodução.
            exportador: gravação do arquivo MIDI.
            catalogo: instrumentos exibidos na tela.
        """
        self._entrada = entrada
        self._parser = parser
        self._configuracao = configuracao
        self._sintetizador = sintetizador
        self._player = player
        self._exportador = exportador
        self._catalogo = catalogo
        self._musica = None
    # ---- Texto ----------------------------------------------------------

    def atualizar_texto(self, texto: str) -> None:
        """Repassa o texto do campo da tela para a EntradaUsuario.

        Args:
            texto: conteúdo do campo de texto.
        """
        self._entrada.set_conteudo(texto)

    def carregar_arquivo(self, caminho: Path) -> str:
        """Carrega o .txt e devolve o texto para a tela exibir no campo.

        Args:
            caminho: arquivo .txt escolhido.

        Returns:
            O texto carregado.

        Raises:
            ArquivoInvalidoErro: arquivo inexistente ou que não é .txt.
        """
        self._entrada.carregar_arquivo(caminho)
        return self._entrada.get_conteudo()

    def salvar_texto(self, caminho: Path | None = None) -> Path:
        """Salva o texto (sobrescreve o original se veio de arquivo).

        Args:
            caminho: onde salvar; None para o arquivo de origem.

        Returns:
            O caminho gravado.

        Raises:
            ArquivoInvalidoErro: sem caminho e o texto não veio de arquivo.
        """
        return self._entrada.salvar_arquivo(caminho)

    def texto_veio_de_arquivo(self) -> bool:
        """Diz se o texto atual tem um arquivo de origem."""
        return self._entrada.veio_de_arquivo()

    def limpar(self) -> None:
        """Nova composição: para a música, esvazia o texto e esquece a música."""
        self._player.stop()
        self._entrada.limpar()
        self._musica = None

    # ---- Geração --------------------------------------------------------

    def gerar_musica(self) -> None:
        """Valida a entrada, interpreta, sintetiza e carrega no Player.

        Raises:
            TextoVazioErro: campo vazio ou só com espaços.
            FormatoInvalidoErro: caracteres fora do alfabeto aceito.
        """
        if self._entrada.esta_vazio():
            raise TextoVazioErro("texto vazio")
        if not self._entrada.eh_formato_valido():
            raise FormatoInvalidoErro("formato incorreto")
        partitura = self._parser.interpretar(self._entrada.get_conteudo())
        self._sintetizar_e_carregar(partitura)

    def regerar_com_novos_parametros(self) -> None:
        """Gera de novo sem reinterpretar o texto.

        Usa os tokens já lidos (Parser.token_to_partitura) com a
        ConfiguracaoInicial atual: é o requisito de mudar os parâmetros e tocar
        de novo sem processar o texto outra vez.
        """
        partitura = self._parser.token_to_partitura()
        self._sintetizar_e_carregar(partitura)

    def musica_foi_gerada(self) -> bool:
        """Diz se já existe uma música gerada."""
        return self._musica is not None

    def _sintetizar_e_carregar(self, partitura: Partitura) -> None:
        """Parte comum de gerar e regerar: Partitura -> MIDI -> Player.

        Args:
            partitura: música interpretada.
        """
        self._musica = self._sintetizador.gerar_musica(partitura)
        self._player.carregar(self._musica)
    # ---- Reprodução -----------------------------------------------------

    def tocar(self) -> None:
        """Toca a música do início.

        Raises:
            MusicaNaoGeradaErro: nada foi gerado.
            AudioIndisponivelErro: este computador não consegue tocar MIDI.
        """
        self._player.play()

    def pausar(self) -> None:
        """Pausa a música."""
        self._player.pausar()

    def retomar(self) -> None:
        """Continua a música de onde pausou."""
        self._player.retomar()

    def parar(self) -> None:
        """Para a música."""
        self._player.stop()

    def reproducao_terminou(self) -> bool:
        """Diz se a música terminou sozinha (para o aviso de conclusão)."""
        return self._player.terminou()

    # ---- Exportação -----------------------------------------------------

    def exportar_midi(self, destino: Path | None = None) -> Path:
        """Salva a música em arquivo MIDI.

        Args:
            destino: caminho do arquivo; None para Downloads com o nome padrão.

        Returns:
            Caminho do arquivo gravado.

        Raises:
            MusicaNaoGeradaErro: nada foi gerado ainda.
        """
        if self._musica is None:
            raise MusicaNaoGeradaErro("Gere a música antes de salvar.")
        return self._exportador.exportar(self._musica, destino)

    # ---- Configuração (bloco de parâmetros da tela principal) -----------

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
