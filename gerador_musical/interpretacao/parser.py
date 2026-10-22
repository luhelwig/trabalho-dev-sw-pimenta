"""Classe Parser (Fase 1, adaptada na Fase 2)."""

from gerador_musical.interpretacao.contexto import ContextoInterpretacao
from gerador_musical.interpretacao.regras.mapeamento import Mapeamento
from gerador_musical.interpretacao.tokens import Token
from gerador_musical.interpretacao.tokenizador import Tokenizador
from gerador_musical.musica.configuracao_inicial import ConfiguracaoInicial
from gerador_musical.musica.partitura import Partitura
from gerador_musical.musica.voz import Voz


class Parser:
    """Transforma o texto em Partitura.

    Duas etapas separadas (já existiam na Fase 1):
      1. texto_to_token: texto -> tokens de cada linha (só sintaxe)
      2. token_to_partitura: tokens -> Partitura (aplica o Mapeamento)

    Guardar os tokens permite atender "alterar parâmetros e reproduzir de
    novo sem reinterpretar o texto": muda a ConfiguracaoInicial e chama
    só a etapa 2.

    O Parser não conhece nenhuma regra específica: quem decide o que cada
    token faz é o Mapeamento (aberto/fechado).
    """

    def __init__(
        self,
        tokenizador: Tokenizador,
        mapeamento: Mapeamento,
        configuracao: ConfiguracaoInicial,
    ) -> None:
        self.texto: str = ""
        self.tokens: list[list[Token]] = []  # uma lista de tokens por linha/voz
        self.partitura: Partitura | None = None
        self._tokenizador = tokenizador
        self._mapeamento = mapeamento
        self._configuracao = configuracao

    def interpretar(self, texto: str) -> Partitura:
        """NOVO — atalho: texto_to_token + token_to_partitura."""
        raise NotImplementedError

    def texto_to_token(self, texto: str) -> list[list[Token]]:
        """Separa o texto em linhas e tokeniza cada uma. Guarda em self.tokens."""
        raise NotImplementedError

    def token_to_partitura(self, tokens: list[list[Token]] | None = None) -> Partitura:
        """Monta a Partitura a partir dos tokens (padrão: self.tokens).

        Cria uma Voz por linha com os parâmetros iniciais vindos de
        ConfiguracaoInicial.criar_parametros(indice).
        """
        raise NotImplementedError

    def _separar_linhas(self, texto: str) -> list[str]:
        """Quebra em linhas (aceitar '\\n' e '\\r\\n').

        TODO (decisão do grupo): linha em branco vira voz silenciosa
        (mantém a numeração V0, V1...) ou é descartada? E linhas além de 4:
        ciclam (requisitos) ou são recusadas ("NESTE TRABALHO, 4 vozes")?
        """
        raise NotImplementedError

    def _interpretar_linha(self, indice: int, tokens: list[Token], partitura: Partitura) -> Voz:
        """Aplica o mapeamento a cada token de uma linha e devolve a Voz."""
        raise NotImplementedError

    def _aplicar(self, token: Token, contexto: ContextoInterpretacao) -> None:
        raise NotImplementedError
