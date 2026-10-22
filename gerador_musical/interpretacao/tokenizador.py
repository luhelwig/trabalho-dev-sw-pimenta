"""NOVA (Fase 2): quebra UMA linha do texto em tokens."""

from gerador_musical.interpretacao.tokens import Token


class Tokenizador:
    """Só reconhece a forma (sintaxe); não sabe o que cada token faz.

    Gramática de uma linha (informal):

        linha  := atraso? unidade*
        atraso := '[' dígitos ']' ' '?          (só no início da linha)
        nota   := [A-G] ('#' | 'b')? (':' [1-7])?
        outro  := qualquer caractere            -> Token CARACTERE

    Casos a decidir (TODO, registrar como suposição):
      - "Bb" é Si bemol (sim, pela gramática acima); "b" sozinho é pausa.
      - "A:" sem dígito, ou "A:9": erro ou nota com duração padrão + ':' e '9'
        como caracteres soltos?
      - Pausas (a–h minúsculas) aceitam ":n"? Ex.: "c:2".
    """

    def tokenizar(self, linha: str) -> list[Token]:
        raise NotImplementedError

    def _ler_atraso(self, linha: str) -> tuple[Token | None, int]:
        """Se a linha começa com "[n]", devolve (token ATRASO, posição
        seguinte, já pulando o espaço). Senão, (None, 0)."""
        raise NotImplementedError

    def _ler_nota(self, linha: str, posicao: int) -> tuple[Token, int]:
        """Lê letra + acidente + duração a partir de `posicao`.
        Devolve o token e a posição do próximo caractere."""
        raise NotImplementedError

    def _ler_acidente(self, linha: str, posicao: int) -> tuple[str, int]:
        raise NotImplementedError

    def _ler_duracao(self, linha: str, posicao: int) -> tuple[str, int]:
        """Lê ":n" se existir. Devolve ("", posicao) se não houver."""
        raise NotImplementedError

    def _ler_caractere(self, linha: str, posicao: int) -> tuple[Token, int]:
        raise NotImplementedError
