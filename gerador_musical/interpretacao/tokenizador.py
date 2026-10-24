"""NOVA (Fase 2): quebra UMA linha do texto em tokens."""


import re

from gerador_musical.interpretacao.tokens import TipoToken, Token
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import Acidente, NotaMusical

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

    PADRAO_ATRASO = re.compile(r"\[(\d+)\] ?")
    PADRAO_DURACAO = re.compile(r":([1-7])")

    def tokenizar(self, linha: str) -> list[Token]:
        tokens = []
        atraso, pos = self._ler_atraso(linha)
        if atraso is not None:
            tokens.append(atraso)
        while pos < len(linha):
            if NotaMusical.eh_letra_de_nota(linha[pos]):
                token, pos = self._ler_nota(linha, pos)
            else:
                token, pos = self._ler_caractere(linha, pos)
            tokens.append(token)
        return tokens

    def _ler_atraso(self, linha: str) -> tuple[Token | None, int]:
        """Se a linha começa com "[n]", devolve (token ATRASO, posição
        seguinte, já pulando o espaço). Senão, (None, 0)."""
        m = self.PADRAO_ATRASO.match(linha)
        if not m:
            return None, 0
        return Token(TipoToken.ATRASO, m.group(0).strip(), 0, valor=int(m.group(1))), m.end()

    def _ler_nota(self, linha: str, posicao: int) -> tuple[Token, int]:
        """Lê letra + acidente + duração a partir de `posicao`.
        Devolve o token e a posição do próximo caractere."""
        letra = linha[posicao]
        acidente, p = self._ler_acidente(linha, posicao+1)
        digito, p = self._ler_duracao(linha, p)
        token = Token(
            TipoToken.NOTA,
            lexema=linha[posicao:p],
            coluna=posicao,
            nota=NotaMusical(letra, Acidente.from_caractere(acidente)),
            duracao=Duracao.from_identificador(int(digito)) if digito else None,
        )
        return token, p

    def _ler_acidente(self, linha: str, posicao: int) -> tuple[str, int]:
        c = linha[posicao:posicao + 1]
        if Acidente.eh_acidente(c):
            return c, posicao + 1
        else:
            return "", posicao

    def _ler_duracao(self, linha: str, posicao: int) -> tuple[str, int]:
        """Lê ":n" se existir. Devolve ("", posicao) se não houver."""
        m = self.PADRAO_DURACAO.match(linha, posicao)
        if m:
            return m.group(1), m.end()
        return "", posicao


    def _ler_caractere(self, linha: str, posicao: int) -> tuple[Token, int]:
        return Token(TipoToken.CARACTERE, linha[posicao], posicao), posicao + 1
