"""NOVA (Fase 2): leitura e gravação de arquivos .txt (Mudança 1)."""

from pathlib import Path


class ArquivoTexto:
    """Responsável apenas pelo I/O de arquivos de texto.

    Separado de EntradaUsuario para que a regra "o que é um texto válido"
    não se misture com "como ler/gravar no disco" (SRP). Também facilita
    testes: EntradaUsuario pode receber um ArquivoTexto falso.
    """

    EXTENSAO_ACEITA = ".txt"
    CODIFICACAO = "utf-8"

    def ler(self, caminho: Path) -> str:
        """Lê o arquivo e devolve seu conteúdo.

        Raises:
            ArquivoInvalidoErro: arquivo inexistente, sem extensão .txt
                ou que não pode ser decodificado.
        """
        raise NotImplementedError

    def salvar(self, caminho: Path, conteudo: str) -> None:
        """Grava `conteudo` em `caminho`, substituindo o arquivo existente."""
        raise NotImplementedError

    def eh_arquivo_txt(self, caminho: Path) -> bool:
        """True se o caminho existe, é arquivo e tem extensão .txt."""
        raise NotImplementedError
