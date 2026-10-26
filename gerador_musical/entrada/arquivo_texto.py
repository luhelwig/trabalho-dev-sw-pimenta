"""NOVA (Fase 2, Mudança 1): leitura e gravação de arquivos .txt."""

from pathlib import Path
from gerador_musical.excecoes import ArquivoInvalidoErro


class ArquivoTexto:
    """Responsável apenas pela leitura e gravação de arquivos de texto.

    Separado de EntradaUsuario para que "o que é um texto válido" não se
    misture com "como ler/gravar no disco" (Responsabilidade Única). Também
    facilita os testes: EntradaUsuario pode receber um ArquivoTexto falso.

    Attributes:
        EXTENSAO_ACEITA: extensão dos arquivos aceitos (".txt").
        CODIFICACAO: codificação usada para ler e gravar ("utf-8").
    """

    EXTENSAO_ACEITA = ".txt"
    CODIFICACAO = "utf-8"

    def ler(self, caminho: Path) -> str:
        """Lê um arquivo .txt e devolve seu conteúdo.

        Tenta UTF-8; se o arquivo foi salvo em outra codificação (comum no
        Windows), lê como latin-1.

        Args:
            caminho: arquivo a ler.

        Returns:
            O texto do arquivo.

        Raises:
            ArquivoInvalidoErro: arquivo inexistente ou sem extensão .txt.
        """
        if not self.eh_arquivo_txt(caminho):
            raise ArquivoInvalidoErro(f"Não é um arquivo .txt válido: {caminho}")
        try:
            return caminho.read_text(encoding=self.CODIFICACAO)
        except UnicodeDecodeError:
            return caminho.read_text(encoding="latin-1")

    def salvar(self, caminho: Path, conteudo: str) -> None:
        """Grava o texto em UTF-8, substituindo o arquivo se ele já existir.

        Args:
            caminho: arquivo de destino.
            conteudo: texto a gravar.
        """
        caminho.write_text(conteudo, encoding=self.CODIFICACAO)

    def eh_arquivo_txt(self, caminho: Path) -> bool:
        """Diz se o caminho existe, é um arquivo e termina em .txt.

        Args:
            caminho: caminho a conferir.
        """
        return caminho.is_file() and caminho.suffix.lower() == self.EXTENSAO_ACEITA
