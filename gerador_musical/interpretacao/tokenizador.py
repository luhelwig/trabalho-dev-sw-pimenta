"""NOVA (Fase 2): quebra UMA linha do texto em tokens."""


import re

from gerador_musical.interpretacao.tokens import TipoToken, Token
from gerador_musical.musica.duracao import Duracao
from gerador_musical.musica.nota_musical import Acidente, NotaMusical

class Tokenizador:
    """Reconhece só a forma (sintaxe); não sabe o que cada token faz.

    Gramática de uma linha (informal):

        linha  := atraso? unidade*
        atraso := '[' dígitos ']' ' '?          (só no início da linha)
        nota   := [A-G] ('#' | 'b')? (':' [1-7])?
        outro  := qualquer caractere            -> token CARACTERE

    Decisões do grupo: "Bb" é Si bemol, mas um "b" sozinho é caractere (vira
    pausa); "A:9" (ou "A:" sem dígito) vira a nota A com duração padrão, e
    ':' e '9' viram caracteres soltos; pausas não aceitam ":n". O
    Tokenizador nunca falha: o que ele não reconhece vira CARACTERE.

    Attributes:
        PADRAO_ATRASO: expressão regular de "[n]" mais um espaço opcional.
        PADRAO_DURACAO: expressão regular de ":n", com n de 1 a 7.
    """

    PADRAO_ATRASO = re.compile(r"\[(\d+)\] ?")
    PADRAO_DURACAO = re.compile(r":([1-7])")

    def tokenizar(self, linha: str) -> list[Token]:
        """Quebra uma linha em tokens, da esquerda para a direita.

        Lê o atraso (se houver) e depois, a cada posição, uma nota (se o
        caractere for A–G) ou um caractere isolado. Cada leitura devolve o token
        e a próxima posição, por isso "C#:3" vira um token só.

        Args:
            linha: uma linha do texto (uma voz).

        Returns:
            Os tokens na ordem em que aparecem.
        """
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
        """Lê "[n]" se a linha começar com ele.

        Args:
            linha: linha inteira.

        Returns:
            (token ATRASO, posição seguinte já pulando o espaço) ou (None, 0).
        """
        m = self.PADRAO_ATRASO.match(linha)
        if not m:
            return None, 0
        return Token(TipoToken.ATRASO, m.group(0).strip(), 0, valor=int(m.group(1))), m.end()

    def _ler_nota(self, linha: str, posicao: int) -> tuple[Token, int]:
        """Lê letra + acidente + duração a partir de `posicao`.

        Args:
            linha: linha inteira.
            posicao: posição da letra da nota.

        Returns:
            (token NOTA, posição do próximo caractere).
        """
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
        """Lê '#' ou 'b' logo depois da letra, se houver.

        Args:
            linha: linha inteira.
            posicao: posição logo depois da letra.

        Returns:
            (acidente lido ou "", próxima posição).
        """
        c = linha[posicao:posicao + 1]
        if Acidente.eh_acidente(c):
            return c, posicao + 1
        else:
            return "", posicao

    def _ler_duracao(self, linha: str, posicao: int) -> tuple[str, int]:
        """Lê ":n" (n de 1 a 7), se houver.

        Args:
            linha: linha inteira.
            posicao: posição logo depois da letra e do acidente.

        Returns:
            (dígito lido, posição seguinte) ou ("", posicao) se não houver.
        """
        m = self.PADRAO_DURACAO.match(linha, posicao)
        if m:
            return m.group(1), m.end()
        return "", posicao


    def _ler_caractere(self, linha: str, posicao: int) -> tuple[Token, int]:
        """Cria um token CARACTERE com um único caractere.

        Args:
            linha: linha inteira.
            posicao: posição do caractere.

        Returns:
            (token CARACTERE, posicao + 1).
        """
        return Token(TipoToken.CARACTERE, linha[posicao], posicao), posicao + 1
