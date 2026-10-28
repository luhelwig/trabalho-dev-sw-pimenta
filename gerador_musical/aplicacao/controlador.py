"""NOVA (Fase 2): fachada usada pela interface para texto, geração, reprodução e exportação.

Fase 3 (bad smell "Classe Grande"): os métodos de configuração (BPM e
parâmetros por voz) foram extraídos para ControladorConfiguracao.
"""

from pathlib import Path

from gerador_musical.entrada.entrada_usuario import EntradaUsuario
from gerador_musical.interpretacao.parser import Parser
from gerador_musical.musica.partitura import Partitura
from gerador_musical.saida.exportador import Exportador
from gerador_musical.saida.player import Player
from gerador_musical.saida.sintetizador import Sintetizador
from gerador_musical.excecoes import FormatoInvalidoErro, MusicaNaoGeradaErro, TextoVazioErro


class ControladorAplicacao:
    """Fachada do fluxo da música: texto -> geração -> reprodução -> arquivo.

    As telas só chamam métodos daqui (e do ControladorConfiguracao) e tratam
    GeradorMusicalErro para mostrar mensagens. Assim, trocar a interface
    (tkinter -> web, por exemplo) não exige mexer na interpretação
    (requisito não-funcional).

    Todas as dependências chegam prontas pelo construtor (montadas em
    main.criar_controladores), o que permite testar com versões falsas.
    """

    def __init__(
        self,
        entrada: EntradaUsuario,
        parser: Parser,
        sintetizador: Sintetizador,
        player: Player,
        exportador: Exportador,
    ) -> None:
        """Recebe todas as dependências prontas.

        Args:
            entrada: texto do usuário.
            parser: interpretação do texto (já com a ConfiguracaoInicial).
            sintetizador: conversão da Partitura em MIDI.
            player: reprodução.
            exportador: gravação do arquivo MIDI.
        """
        self._entrada = entrada
        self._parser = parser
        self._sintetizador = sintetizador
        self._player = player
        self._exportador = exportador
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
        self._player.parar()
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
        self._player.tocar()

    def pausar(self) -> None:
        """Pausa a música."""
        self._player.pausar()

    def retomar(self) -> None:
        """Continua a música de onde pausou."""
        self._player.retomar()

    def parar(self) -> None:
        """Para a música."""
        self._player.parar()

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
