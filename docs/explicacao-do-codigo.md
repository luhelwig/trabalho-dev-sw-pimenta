# Explicação do código: Gerador de Música a partir de Texto (Fases 2 e 3)

Este documento explica o código inteiro do projeto: como ele está organizado, o que cada classe e cada função faz, como uma música é gerada do começo ao fim e quais conceitos de Desenvolvimento de Software aparecem em cada parte. A ideia é que qualquer pessoa do grupo consiga ler, entender e explicar o código para o professor.

Sugestão de leitura: comece pelas seções 1 a 3 (visão geral, organização e o caminho de uma música). A seção 4 é a referência, função por função, para consultar quando precisar. A seção 6 liga o código aos conceitos da disciplina, a seção 9 tem perguntas que o professor pode fazer e a seção 10 mostra os bad smells que encontramos na Fase 3 e como cada um foi corrigido.

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Organização em pacotes e camadas](#2-organização-em-pacotes-e-camadas)
3. [O caminho de uma música, passo a passo](#3-o-caminho-de-uma-música-passo-a-passo)
4. [Arquivo por arquivo, função por função](#4-arquivo-por-arquivo-função-por-função)
5. [Testes](#5-testes)
6. [Conceitos de Desenvolvimento de Software no código](#6-conceitos-de-desenvolvimento-de-software-no-código)
7. [Requisitos e onde eles são atendidos](#7-requisitos-e-onde-eles-são-atendidos)
8. [Pontos de atenção e pequenas melhorias](#8-pontos-de-atenção-e-pequenas-melhorias)
9. [Perguntas que o professor pode fazer](#9-perguntas-que-o-professor-pode-fazer)
10. [Fase 3: bad smells e refatorações](#10-fase-3-bad-smells-e-refatorações)

---

## 1. Visão geral

O programa recebe um texto e o transforma em música. O processamento acontece em etapas bem separadas, cada uma feita por uma parte diferente do código:

```
 texto digitado ou .txt
          │
          ▼
 EntradaUsuario ── guarda o texto e valida (vazio? caracteres aceitos?)
          │
          ▼
 Tokenizador ───── quebra cada linha em "tokens" (ex.: "C#:3", "[4]", "?")
          │
          ▼
 Parser + Mapeamento + Regras ── decide o que cada token faz e monta a Partitura
          │
          ▼
 Partitura ─────── vozes (uma por linha) + mudanças de andamento
          │
          ▼
 Sintetizador ──── transforma a Partitura em um arquivo MIDI (mido.MidiFile)
          │
     ┌────┴─────┐
     ▼          ▼
  Player     ExportadorMidi
 (tocar)     (salvar .mid)
```

A interface gráfica (tkinter) fica por cima de tudo isso e não conhece nenhuma dessas peças diretamente: ela só conversa com dois controladores, o `ControladorAplicacao` (texto, geração, reprodução e arquivo) e o `ControladorConfiguracao` (BPM e parâmetros iniciais de cada voz), que repassam os pedidos para quem sabe resolver.

Três ideias guiam o projeto inteiro:

1. **Cada classe tem uma responsabilidade.** Ler arquivo, validar texto, quebrar em tokens, aplicar regras, gerar MIDI, tocar e salvar são trabalhos de classes diferentes.
2. **O mapeamento texto → música é fácil de mudar.** Cada linha da tabela do enunciado é uma classe de regra. Mudar o mapeamento é trocar ou adicionar regras, sem mexer no Parser.
3. **As partes dependem de abstrações, não de detalhes.** O Player não sabe que existe pygame; o Parser não sabe quais regras existem; a interface não sabe que existe MIDI. Isso facilita testar e trocar peças.

---

## 2. Organização em pacotes e camadas

```
main.py                         monta todas as peças e abre a janela
gerador_musical/
  excecoes.py                   erros esperados do sistema
  musica/                       MODELO: notas, durações, instrumentos, vozes, partitura
    limites.py
    duracao.py
    nota_musical.py
    instrumentos.py
    parametros_musica.py
    configuracao_inicial.py
    evento_musical.py
    voz.py
    partitura.py
  entrada/                      ENTRADA: texto digitado e arquivos .txt
    arquivo_texto.py
    entrada_usuario.py
  interpretacao/                INTERPRETAÇÃO: texto -> Partitura
    tokens.py
    tokenizador.py
    contexto.py
    parser.py
    regras/
      regra_mapeamento.py       classes base das regras
      regras_eventos.py         regras que criam notas e pausas
      regras_voz.py             regras que mudam a voz (atraso, volume, oitava, instrumento)
      regras_globais.py         regra que muda a música toda (andamento)
      mapeamento.py             a "tabela" que liga cada token à sua regra
  saida/                        SAÍDA: Partitura -> MIDI, tocar, salvar
    sintetizador.py
    backend_audio.py
    player.py
    exportador.py
  aplicacao/                    APLICAÇÃO: as fachadas que a interface usa
    controlador.py              fluxo da música (texto, gerar, tocar, exportar)
    controlador_configuracao.py BPM e parâmetros iniciais de cada voz (Fase 3)
  interface/                    INTERFACE: telas em tkinter
    estilo.py
    app.py
    tela_principal.py
    painel_configuracoes.py     painel de configurações da tela principal (Fase 3)
    tela_carregamento.py
    tela_reproducao.py
    recursos/                   fonte Micro 5 (.ttf) e a licença dela
tests/                          testes automáticos (pytest)
docs/                           croqui da fase 2 e esta explicação
```

### Quem depende de quem

As setas mostram "quem importa quem". Repare que elas sempre apontam para baixo: as camadas de cima usam as de baixo, nunca o contrário.

```
                interface
                    │
                    ▼
                aplicacao (ControladorAplicacao + ControladorConfiguracao)
           ┌────────┼─────────┐
           ▼        ▼         ▼
       entrada  interpretacao  saida
           │        │         │
           └────────┼─────────┘
                    ▼
                  musica
```

- **`musica`** é o centro. Não importa nada de texto, de MIDI nem de interface (está escrito no `__init__.py` do pacote). Por isso é a parte mais estável e mais fácil de testar.
- **`entrada`**, **`interpretacao`** e **`saida`** usam o modelo musical, mas não se conhecem entre si. O Sintetizador, por exemplo, recebe uma `Partitura` pronta e não sabe de onde ela veio.
- **`aplicacao`** junta tudo para a interface, em duas fachadas: uma para o fluxo da música e outra para as configurações.
- **`interface`** só fala com a aplicação. Se um dia trocássemos tkinter por uma página web, o resto do código ficaria igual.

Essa organização é uma **arquitetura em camadas**, e a separação entre modelo (`musica`), controle (`aplicacao`) e telas (`interface`) lembra o padrão **MVC** (Model-View-Controller).

---

## 3. O caminho de uma música, passo a passo

### 3.1 O que acontece quando o usuário clica em "gerar música"

1. **`TelaPrincipal._ao_gerar()`** lê o texto do campo com `get_texto()`.
2. Se o texto é o mesmo da última geração, só os parâmetros mudaram: chama `controlador.regerar_com_novos_parametros()` (pula para o passo 6). Senão, chama `controlador.atualizar_texto(texto)` e `controlador.gerar_musica()`.
3. **`ControladorAplicacao.gerar_musica()`** valida: se `entrada.esta_vazio()`, lança `TextoVazioErro("texto vazio")`; se `entrada.eh_formato_valido()` é falso, lança `FormatoInvalidoErro("formato incorreto")`.
4. **`Parser.interpretar(texto)`** faz duas etapas:
   - `texto_to_token(texto)`: separa o texto em linhas e o `Tokenizador` quebra cada linha em tokens. O resultado fica guardado em `parser.tokens`.
   - `token_to_partitura()`: para cada linha, cria uma `Voz` com os parâmetros iniciais da `ConfiguracaoInicial` e passa cada token pelo `Mapeamento`, que escolhe a regra certa. As regras criam eventos (notas e pausas) e mudam parâmetros.
5. O Parser devolve uma **`Partitura`**: a lista de vozes e as mudanças de andamento.
6. **`_sintetizar_e_carregar(partitura)`**: o `Sintetizador` gera o `mido.MidiFile` e o `Player` grava esse MIDI num arquivo temporário, pronto para tocar.
7. Se deu tudo certo, a tela principal chama `app.mostrar_tela("reproducao")`. Se algum `GeradorMusicalErro` foi lançado, ela mostra a mensagem com `app.mostrar_erro(...)` e fica onde está.

Depois, na tela de reprodução:

- **tocar**: `controlador.tocar()` → `Player.tocar()` → o backend (pygame) carrega o arquivo e toca. A tela agenda `_verificar_fim()` a cada 200 ms com `after()` para saber quando a música acabou, sem travar a janela.
- **pausar / retomar / parar**: o controlador repassa ao Player, que repassa ao backend.
- **baixar midi**: `controlador.exportar_midi()` → `ExportadorMidi.exportar(...)` grava em `~/Downloads/musica_AAAAMMDD_HHMMSS.mid`.

### 3.2 Um exemplo completo, de verdade

Vamos seguir o texto `C:3?D>H`, de uma linha só, com a configuração padrão. (Esta saída foi gerada rodando o próprio código.)

**Etapa 1: tokens.** O Tokenizador lê a linha da esquerda para a direita:

| Lexema | Tipo | Detalhes |
|--------|------|----------|
| `C:3` | NOTA | nota Dó natural, duração 3 (semínima) |
| `?` | CARACTERE | |
| `D` | NOTA | nota Ré natural, sem duração (vai usar a padrão) |
| `>` | CARACTERE | |
| `H` | CARACTERE | |

**Etapa 2: regras.** A voz 0 começa com instrumento 6 (cravo), oitava 6 e volume 100. O Parser passa cada token pelo Mapeamento:

| Token | Regra escolhida | Efeito | Posição da voz |
|-------|-----------------|--------|----------------|
| `C:3` | `RegraNota` | cria nota Dó, 1 beat, cravo, oitava 6, volume 100 | 0 → 1 beat |
| `?` | `RegraOitava(+1)` | oitava atual passa a ser 7 | 1 |
| `D` | `RegraNota` | cria nota Ré, 1 beat (padrão), oitava 7 | 1 → 2 |
| `>` | `RegraAndamento(+10)` | registra na Partitura: "em 2 beats, +10 bpm" | 2 |
| `H` | `RegraRepetirOuPausar` (padrão) | o token anterior (`>`) não era nota, então cria uma pausa | 2 → 3 |

**Etapa 3: MIDI.** O Sintetizador gera duas trilhas:

```
trilha 0 (andamento)
   set_tempo tempo=500000 time=0        # 120 bpm = 500000 microssegundos por beat
   set_tempo tempo=461538 time=960      # 130 bpm, 960 ticks (2 beats) depois
trilha 1 (voz 0, canal 0)
   program_change program=6 time=0      # cravo
   note_on  note=84 velocity=100 time=0 # Dó6 = 12 x (6+1) + 0 = 84
   note_off note=84 time=480            # 1 beat = 480 ticks
   note_on  note=98 velocity=100 time=0 # Ré7 = 12 x (7+1) + 2 = 98
   note_off note=98 time=480
   end_of_track time=480                # a pausa final segura a trilha por mais 1 beat
```

O `time` de cada mensagem MIDI é **delta**: quantos ticks se passaram desde a mensagem anterior, e não o tempo absoluto. Por isso a pausa não gera mensagem nenhuma; ela só aumenta o `time` da próxima.

---

## 4. Arquivo por arquivo, função por função

Convenções usadas no código, que valem para todos os arquivos:

- Nomes começando com `_` (ex.: `_ler_nota`) são **privados**: só a própria classe usa. Os outros formam a interface pública da classe.
- `@classmethod` que devolve um objeto pronto (ex.: `Mapeamento.padrao()`, `ConfiguracaoInicial.padrao()`) é um **método de fábrica**: um jeito com nome claro de construir o objeto já configurado.
- `@dataclass(frozen=True)` cria uma classe de dados **imutável** (depois de criada, não muda). Usamos para coisas que são "valores", como uma nota ou um token.
- Os docstrings marcam o que é **NOVO (Fase 2)**, o que veio da **Fase 1** e o que mudou na **Fase 3** (refatorações por bad smells), para mostrar a evolução do projeto.

### 4.1 `main.py`: ponto de entrada

É o único lugar que conhece as classes concretas de tudo e monta as peças. Isso se chama **composition root** ("raiz de composição").

| Função | O que faz |
|--------|-----------|
| `criar_controladores()` | Cria o catálogo de instrumentos, a configuração inicial, o Tokenizador, o Mapeamento padrão, o Parser, a EntradaUsuario, o Sintetizador, o Player (com `BackendPygame`) e o ExportadorMidi. Devolve dois controladores prontos: o `ControladorAplicacao` (com entrada, parser, sintetizador, player e exportador) e o `ControladorConfiguracao` (com a configuração e o catálogo). Repare que a **mesma** `configuracao` vai para o Parser e para o `ControladorConfiguracao`: quando o painel da tela muda um parâmetro, o Parser enxerga a mudança. |
| `main()` | Cria a janela `App` com os dois controladores (`App(*criar_controladores())`: o `*` "desempacota" a dupla em dois argumentos), chama `construir()` e entra no `mainloop()` do tkinter (o laço que espera cliques e teclas). |

O `if __name__ == "__main__": main()` no fim faz o programa rodar quando executamos `python main.py`, mas não quando o arquivo é só importado (por exemplo, por um teste).

### 4.2 `excecoes.py`: erros do sistema

Uma pequena **hierarquia de exceções**. Todas herdam de `GeradorMusicalErro`, então a interface pode tratar qualquer erro esperado com um único `except GeradorMusicalErro`.

| Classe | Quando acontece |
|--------|-----------------|
| `GeradorMusicalErro` | Base de todos os erros esperados. |
| `TextoVazioErro` | Gerar música com o campo vazio (ou só com espaços). |
| `FormatoInvalidoErro` | O texto tem caracteres fora do alfabeto aceito (ex.: letras cirílicas ou japonesas). |
| `ArquivoInvalidoErro` | Arquivo que não existe, não é .txt, ou "salvar" sem saber onde. |
| `MusicaNaoGeradaErro` | Tocar ou exportar antes de gerar a música. |
| `AudioIndisponivelErro` | O computador não consegue tocar o MIDI (pygame sem módulo de som, ou Linux sem banco de sons). O arquivo .mid continua podendo ser salvo. |

Erros de programação (como um `ValueError` de valor fora do limite) não herdam dessa base de propósito: eles indicam bug ou entrada inválida dentro do código, não uma situação normal de uso.

### 4.3 Pacote `musica/`: o modelo musical

#### `limites.py`

Só constantes, para não espalhar "números mágicos" pelo código: `VOLUME_MINIMO = 0`, `VOLUME_MAXIMO = 127`, `PROGRAMA_MIDI_MINIMO = 0`, `PROGRAMA_MIDI_MAXIMO = 127`, `OITAVA_MINIMA = 0`, `OITAVA_MAXIMA = 8`, `BPM_MINIMO = 20`, `BPM_MAXIMO = 300`. Os limites de volume e instrumento vêm do padrão MIDI (0 a 127). A oitava máxima 8 é a última oitava completa que cabe em 0–127 com a fórmula usada em `NotaMusical.altura_midi`.

#### `duracao.py`: `Duracao` (Enum)

Representa a figura musical. O valor de cada membro é o número usado no texto (`A:3` → 3).

| Membro | Valor | Beats |
|--------|-------|-------|
| `SEMIBREVE` | 1 | 4 |
| `MINIMA` | 2 | 2 |
| `SEMINIMA` | 3 | 1 |
| `COLCHEIA` | 4 | 0,5 |
| `SEMICOLCHEIA` | 5 | 0,25 |
| `FUSA` | 6 | 0,125 |
| `SEMIFUSA` | 7 | 0,0625 |

A constante `BEATS_POR_SEMIBREVE = 4` registra a decisão do grupo: **a semínima vale 1 beat**.

| Função | O que faz |
|--------|-----------|
| `from_identificador(identificador)` | Converte o dígito do texto (1–7) em `Duracao`. `cls(identificador)` procura o membro com aquele valor; se não existir, o Python lança `ValueError` e nós relançamos com uma mensagem mais clara ("Use 1 a 7"). |
| `padrao()` | Duração usada quando a nota não tem `:n`: `SEMINIMA`. |
| `fracao_da_semibreve()` | Quanto a figura vale em relação à semibreve: `1 / 2 ** (valor - 1)`. Semibreve 1, mínima 1/2, semínima 1/4... |
| `em_beats()` | Duração em beats: fração da semibreve × 4. É a unidade usada pelo BPM, pelo atraso `[n]` e pelo Sintetizador. |

Por que um `Enum` e não números soltos? Porque assim é impossível ter uma "duração 9": só existem os 7 valores válidos, e cada um tem nome.

#### `nota_musical.py`: `Acidente` (Enum) e `NotaMusical`

`Acidente` representa sustenido, bemol ou natural. O valor de cada membro é o próprio caractere do texto (`"#"`, `"b"`, `""`).

| Função | O que faz |
|--------|-----------|
| `Acidente.from_caractere(caractere)` | `"#"` → `SUSTENIDO`, `"b"` → `BEMOL`, qualquer outra coisa → `NATURAL`. Usa `cls(caractere)` e, se der `ValueError`, devolve `NATURAL`. |
| `Acidente.eh_acidente(caractere)` | `True` se o caractere é `#` ou `b`. Usado pelo Tokenizador para saber se o caractere depois da letra faz parte da nota. |
| `Acidente.deslocamento_semitons()` | +1 para sustenido, −1 para bemol, 0 para natural. |

`NotaMusical` é uma nota **sem oitava**: só a letra (`A` a `G`) e o acidente. É um **objeto de valor imutável** (`frozen=True`): duas notas com a mesma letra e o mesmo acidente são iguais (`NotaMusical("A") == NotaMusical("A")`), o que facilita muito os testes.

Constantes da classe: `LETRAS_DE_NOTA = "ABCDEFG"`; `SEMITONS`, a posição de cada letra na escala cromática a partir do Dó (C=0, D=2, E=4, F=5, G=7, A=9, B=11); e `NOMES`, os nomes em português (A=Lá, B=Si, C=Dó...).

| Função | O que faz |
|--------|-----------|
| `eh_letra_de_nota(caractere)` | `True` só para `A`–`G` maiúsculos. É o que define "isto começa uma nota" no Tokenizador. A letra `H` deixou de ser nota na Fase 2. |
| `semitom()` | Semitom da letra + deslocamento do acidente. Ex.: `C#` → 0 + 1 = 1; `Eb` → 4 − 1 = 3. Pode dar −1 (`Cb`) ou 12 (`B#`), que caem na oitava vizinha, como na música de verdade. |
| `altura_midi(oitava)` | Número MIDI da nota numa oitava: `12 × (oitava + 1) + semitom()`. Com essa fórmula, Dó4 = 60 (o "dó central" do padrão MIDI) e Lá4 = 69. Se o resultado sair de 0–127, lança `ValueError`. |
| `nome()` | Nome legível, ex.: `"Lá#"`, `"Mib"`. Hoje não é usado pelo programa (ficou para mensagens e testes). |

#### `instrumentos.py`: `Instrumento` e `CatalogoInstrumentos`

No topo do arquivo ficam constantes com os programas MIDI que o código usa pelo nome: `PIANO = 0`, `CRAVO = 6`, `TUBULAR_BELLS = 14`, `ORGAO_DE_IGREJA = 19`, `BANDONEON = 23`, `CORDAS = 48`, `FAGOTE = 70`, `GAITA_DE_FOLES = 109`, `AGOGO = 113`.

**Atenção à numeração:** o MIDI (e o mido) usam programas de **0 a 127**. Listas como a da Wikipédia numeram de **1 a 128**. O enunciado mistura as duas; no código tudo está convertido para 0–127 (ex.: "Church Organ GM 20" na lista vira programa 19).

`Instrumento` é um objeto de valor imutável com `programa` (número MIDI) e `nome`.

`CatalogoInstrumentos` é a lista de instrumentos que o programa oferece (30, o enunciado pede no mínimo 25).

| Função | O que faz |
|--------|-----------|
| `__init__(instrumentos)` | Guarda a lista e monta um dicionário `programa → Instrumento` para buscas rápidas. |
| `padrao()` | Fábrica com os 30 instrumentos escolhidos pelo grupo, incluindo todos os obrigatórios do enunciado. |
| `listar()` | Devolve uma **cópia** da lista (quem recebe pode mexer na cópia sem estragar o catálogo). É o que a tela usa para montar a lista de instrumentos. |
| `buscar(programa)` | Devolve o `Instrumento` daquele programa (lança `KeyError` se não existir). |
| `contem(programa)` | `True` se o programa está no catálogo. Usado nos testes. |
| `nome_de(programa)` | Atalho para `buscar(programa).nome`. Hoje não é usado pelo programa. |

Observação: as regras de troca de instrumento por dígito podem gerar qualquer programa de 0 a 127, mesmo os que não estão no catálogo. O catálogo é só o que aparece para o usuário escolher na tela.

#### `parametros_musica.py`: `ParametrosMusica`

O **estado de uma voz** enquanto o texto é interpretado: instrumento, oitava e volume. Cada um tem dois valores:

- **padrão/inicial**: o valor com que a voz começou (vem da `ConfiguracaoInicial`);
- **atual**: o valor depois dos comandos lidos no texto.

Mudança da Fase 1 para a Fase 2: antes existia um `ParametrosMusica` para a música toda; agora existe **um por voz**, porque cada linha tem sua oitava, seu volume e seu instrumento. O BPM saiu daqui porque é global.

| Função | O que faz |
|--------|-----------|
| `__init__(instrumento_inicial, oitava_padrao, volume_padrao)` | Guarda os valores iniciais e começa com `atual = inicial`. |
| `dobrar_volume()` | Comando espaço: `volume_atual = min(volume_atual × 2, 127)`. |
| `reset_volume()` | Volta o volume ao padrão da voz. |
| `get_volume()` | Volume atual. |
| `incrementar_oitava()` | Comando `?`: sobe uma oitava; se passar de 8, volta à oitava padrão da voz (regra da Fase 1). |
| `decrementar_oitava()` | Comando `V`: desce uma oitava; se ficar abaixo de 0, volta à oitava padrão (decisão simétrica à de subir). |
| `reset_oitava()` | Volta a oitava ao padrão. |
| `get_oitava()` | Oitava atual. |
| `set_instrumento(midi)` | Troca o instrumento atual; lança `ValueError` fora de 0–127. |
| `get_instrumento()` | Instrumento atual. |
| `somar_ao_instrumento(quantidade)` | **Fase 3.** Soma ao instrumento atual e usa `% 128` para dar a volta se passar de 127 (ex.: 126 + 4 = 2). Usado pela regra dos dígitos pares. Antes essa conta ficava na própria regra (ver seção 10, "Inveja de Recursos"). |
| `reset_instrumento()` | Volta ao instrumento inicial da voz. |
| `resetar()` | Volta volume, oitava e instrumento aos iniciais. Hoje não é chamado pelo programa. |

#### `configuracao_inicial.py`: `ConfiguracaoInicial`

Os valores com que a música **começa**: o BPM global e, para cada voz, instrumento, oitava e volume iniciais. É esta classe que a tela altera quando o usuário mexe nas configurações. O Parser só lê dela.

Constantes do módulo: `BPM_PADRAO = 120`; `INSTRUMENTOS_PADRAO = (CRAVO, ORGAO_DE_IGREJA, PIANO, FAGOTE)`; `OITAVAS_PADRAO = (6, 5, 4, 3)`; `VOLUMES_PADRAO = (100, 80, 60, 40)`. Constante da classe: `TAMANHO_DO_CICLO = 4`.

| Função | O que faz |
|--------|-----------|
| `__init__(bpm_inicial)` | Guarda o BPM e carrega os padrões nas listas por voz. |
| `_carregar_padroes()` | Copia as tuplas de padrão para listas (`list(...)`), que podem ser alteradas sem mexer nas constantes. |
| `_validar(valor, minimo, maximo, nome)` | Método estático que lança `ValueError` se o valor estiver fora do intervalo. É reaproveitado por todos os `set_`, então a validação fica num lugar só. |
| `padrao()` | Fábrica: `ConfiguracaoInicial(BPM_PADRAO)`. |
| `get_bpm_inicial()` / `set_bpm_inicial(bpm)` | Lê/altera o BPM (20 a 300). |
| `get_instrumento_inicial(i)` / `set_instrumento_inicial(i, programa)` | Lê/altera o instrumento inicial da voz `i` (0 a 127). |
| `get_oitava_inicial(i)` / `set_oitava_inicial(i, oitava)` | Lê/altera a oitava inicial da voz `i` (0 a 8). |
| `get_volume_inicial(i)` / `set_volume_inicial(i, volume)` | Lê/altera o volume inicial da voz `i` (0 a 127). |
| `criar_parametros(i)` | **Fábrica** de `ParametrosMusica`: cria um objeto **novo** com os valores iniciais da voz `i`. Por ser novo a cada chamada, os comandos do texto mudam a cópia e nunca estragam a configuração. |
| `restaurar_padroes()` | Desfaz as mudanças do usuário. Hoje não há botão que use isso. |
| `_indice_no_ciclo(i)` | `i % 4`. É o que faz a 5ª linha (voz 4) começar igual à 1ª, a 6ª igual à 2ª, e assim por diante. |

#### `evento_musical.py`: `TipoEvento` e `EventoMusical`

`TipoEvento` é um Enum com `NOTA` e `PAUSA`.

`EventoMusical` é algo que **ocupa tempo** na linha do tempo de uma voz. Uma nota guarda uma "foto" do instrumento, da oitava e do volume da voz **no momento em que foi lida**. Assim o Sintetizador não precisa reinterpretar comandos: tudo o que ele precisa está no evento.

Campos: `tipo`, `duracao`, `nota` (só para notas), `instrumento`, `oitava`, `volume`.

Mudanças da Fase 1: `nota` virou `NotaMusical` (letra + acidente), `duracao` virou o Enum `Duracao`, e o antigo `eh_acao()` saiu (comandos não viram eventos; eles só mudam parâmetros).

| Função | O que faz |
|--------|-----------|
| `criar_nota(nota, duracao, parametros)` | Fábrica de nota: copia instrumento, oitava e volume **atuais** dos parâmetros. Copiar os valores (em vez de guardar o objeto `parametros`) evita um bug clássico: se o evento guardasse a referência, um `?` lido depois mudaria a oitava das notas que já foram criadas. |
| `criar_pausa(duracao)` | Fábrica de pausa (sem nota, instrumento, oitava ou volume). |
| `eh_nota()` / `eh_pausa()` | Perguntam o tipo. |
| `altura_midi()` | Número MIDI da nota: `nota.altura_midi(oitava)`. Lança `ValueError` se for pausa. |
| `duracao_em_beats()` | `duracao.em_beats()`. |

#### `voz.py`: `Voz`

Uma voz é **uma linha do texto**: a sequência de eventos dela, os parâmetros e o atraso inicial. A voz 0 é a primeira linha, a voz 1 a segunda, e assim por diante.

| Função | O que faz |
|--------|-----------|
| `__init__(indice, parametros)` | Guarda o número da voz, os parâmetros, atraso 0 e lista de eventos vazia. |
| `adicionar_evento(evento)` | Põe um evento no fim da voz. |
| `get_eventos()` | Devolve uma cópia da lista de eventos. |
| `set_atraso(beats)` | Atraso de `[n]`; lança `ValueError` se for negativo. |
| `get_atraso()` | Atraso em beats. |
| `posicao_atual_beats()` | Onde a voz "está" no tempo: atraso + soma das durações dos eventos. É usado para saber **em que momento** um `>` ou `<` aconteceu. |
| `duracao_total_beats()` | Duração total da voz (hoje é igual à posição atual). |
| `canal_midi()` | Canal MIDI da voz. O MIDI tem 16 canais (0–15), e o canal 9 é reservado para bateria, então ele é pulado: vozes 0–8 usam os canais 0–8, vozes 9–14 usam 10–15, e depois o ciclo recomeça (`indice % 15`). |
| `esta_vazia()` | `True` se a voz não tem eventos. |

Constante: `CANAL_PERCUSSAO_MIDI = 9`.

#### `partitura.py`: `MudancaAndamento` e `Partitura`

`MudancaAndamento` (imutável) registra um `>` ou `<`: a posição em beats e o **delta** (+10 ou −10). Guardamos o delta, e não o BPM final, porque as linhas são lidas uma de cada vez: só dá para saber o BPM real em cada ponto depois de juntar e ordenar as mudanças de todas as vozes.

`Partitura` é o **resultado da interpretação**: todas as vozes mais as mudanças de andamento. Não sabe nada de texto nem de MIDI.

| Função | O que faz |
|--------|-----------|
| `__init__(bpm_inicial)` | BPM inicial, lista de vozes e lista de mudanças vazias. |
| `adicionar_voz(voz)` / `get_vozes()` | Adiciona / devolve cópia da lista de vozes. |
| `numero_de_vozes()` | Quantidade de vozes (usado nos testes). |
| `get_bpm_inicial()` | BPM com que a música começa. |
| `registrar_mudanca_andamento(posicao, delta)` | Guarda uma `MudancaAndamento`. Chamado pela `RegraAndamento`. |
| `get_mudancas_andamento()` | As mudanças **ordenadas por posição**, de todas as vozes juntas. |
| `bpm_em(posicao)` | BPM efetivo num ponto: começa no BPM inicial e soma, em ordem, os deltas das mudanças até aquela posição, limitando entre 20 e 300 a cada passo. Ex.: 120, `+10` em 4 beats e `−10` em 8 beats → `bpm_em(5) = 130`, `bpm_em(9) = 120`. |
| `duracao_total_beats()` | Duração da voz mais longa (`max` com `default=0` para partitura sem vozes). |
| `esta_vazia()` | `True` se nenhuma voz tem eventos. Hoje não é usado pelo programa. |

### 4.4 Pacote `entrada/`: o texto do usuário

#### `arquivo_texto.py`: `ArquivoTexto`

Cuida **só** de ler e gravar arquivos .txt. Foi separada de `EntradaUsuario` para não misturar "o que é um texto válido" com "como mexer no disco" (Princípio da Responsabilidade Única). Constantes: `EXTENSAO_ACEITA = ".txt"`, `CODIFICACAO = "utf-8"`.

| Função | O que faz |
|--------|-----------|
| `ler(caminho)` | Se não for um .txt existente, lança `ArquivoInvalidoErro`. Tenta ler em UTF-8; se o arquivo foi salvo em outra codificação (comum no Windows), cai no `except UnicodeDecodeError` e lê em latin-1. |
| `salvar(caminho, conteudo)` | Grava o texto em UTF-8, substituindo o arquivo se já existir. |
| `eh_arquivo_txt(caminho)` | `True` se o caminho existe, é um arquivo e termina em `.txt` (sem diferenciar maiúsculas). |

#### `entrada_usuario.py`: `EntradaUsuario`

Guarda o texto que o usuário digitou ou carregou, e lembra **de onde** ele veio (para "salvar" sobrescrever o arquivo original, como pede a Mudança 1).

Constantes do módulo: `ACENTOS` (letras acentuadas do português) e `ALFABETO_ACEITO = frozenset(string.printable + ACENTOS)`. `string.printable` são os caracteres imprimíveis do teclado americano (letras, dígitos, pontuação, espaço, quebra de linha). O `frozenset` deixa a pergunta "este caractere é aceito?" muito rápida.

| Função | O que faz |
|--------|-----------|
| `__init__(arquivo_texto=None)` | Texto vazio, sem arquivo de origem. Recebe um `ArquivoTexto` (ou cria um), o que permite trocar por um falso em testes. |
| `get_conteudo()` / `set_conteudo(texto)` | Lê / atualiza o texto (a tela chama `set_conteudo` através do controlador antes de gerar ou salvar). |
| `esta_vazio()` | `True` se o texto é vazio ou só tem espaços e quebras de linha (`not conteudo.strip()`). |
| `eh_formato_valido()` | `True` se **todos** os caracteres estão no alfabeto aceito. É o que gera a mensagem "formato incorreto". |
| `carregar_arquivo(caminho)` | Lê pelo `ArquivoTexto`, guarda o texto, uma cópia do original e o caminho de origem. |
| `salvar_arquivo(caminho=None)` | Grava o texto. Sem caminho, usa o arquivo de origem; se o texto não veio de arquivo, lança `ArquivoInvalidoErro`. Devolve o caminho gravado. |
| `foi_modificado()` | `True` se o texto mudou desde o último carregar/salvar. Hoje só os testes usam. |
| `veio_de_arquivo()` | `True` se existe arquivo de origem. A tela usa para decidir entre salvar direto ou abrir "salvar como". |
| `limpar()` | Esvazia tudo e esquece o arquivo de origem (nova composição). |

### 4.5 Pacote `interpretacao/`: do texto à Partitura

A interpretação é feita em **duas etapas**, como num compilador:

1. **Análise léxica** (Tokenizador): só reconhece a **forma** dos pedaços do texto. Sabe que `C#:3` é uma nota, mas não sabe o que uma nota faz.
2. **Análise semântica** (Parser + Mapeamento + Regras): decide o **significado** de cada pedaço e monta a Partitura.

Essa separação existe porque na Fase 2 algumas "unidades" têm vários caracteres (`C#:3`, `[4]`). Na Fase 1 cada caractere era uma unidade.

#### `tokens.py`: `TipoToken` e `Token`

`TipoToken` (Enum): `ATRASO` (`[n]` no início da linha), `NOTA` (letra + acidente opcional + `:n` opcional) e `CARACTERE` (qualquer outro caractere isolado).

`Token` (imutável) tem: `tipo`, `lexema` (o trecho original do texto, ex.: `"C#:3"`), `coluna` (posição na linha), `nota` e `duracao` (só para notas) e `valor` (o número do atraso).

| Função | O que faz |
|--------|-----------|
| `eh_nota()` | `True` se o tipo é `NOTA`. |

#### `tokenizador.py`: `Tokenizador`

Quebra **uma linha** em tokens. A gramática, de modo informal:

```
linha  := atraso? unidade*
atraso := '[' dígitos ']' ' '?          (só no início da linha)
nota   := [A-G] ('#' | 'b')? (':' [1-7])?
outro  := qualquer caractere            -> token CARACTERE
```

Usa duas **expressões regulares**: `PADRAO_ATRASO = r"\[(\d+)\] ?"` (colchete, um ou mais dígitos, colchete e um espaço opcional) e `PADRAO_DURACAO = r":([1-7])"` (dois-pontos e um dígito de 1 a 7). Os parênteses "capturam" o número para depois usarmos com `m.group(1)`.

| Função | O que faz |
|--------|-----------|
| `tokenizar(linha)` | Primeiro tenta ler um atraso no começo. Depois anda pela linha com um índice `pos`: se o caractere é letra de nota, chama `_ler_nota`; senão, `_ler_caractere`. Cada função de leitura devolve o token **e a próxima posição**, e é assim que `C#:3` vira um token só (a posição pula 4 caracteres). |
| `_ler_atraso(linha)` | Aplica `PADRAO_ATRASO.match(linha)`. O `match` só procura no **início** da string, então `[4]` no meio da linha não é atraso. Devolve `(token ATRASO, posição depois do espaço)` ou `(None, 0)`. |
| `_ler_nota(linha, posicao)` | Lê a letra, depois o acidente (`_ler_acidente`) e a duração (`_ler_duracao`). Monta o token com `NotaMusical(letra, Acidente.from_caractere(acidente))` e `Duracao.from_identificador(...)` se houver dígito (senão `duracao=None`). |
| `_ler_acidente(linha, posicao)` | Olha o próximo caractere; se for `#` ou `b`, devolve ele e avança uma posição. Por isso `Bb` é Si bemol, enquanto um `b` sozinho vira caractere (e depois pausa). |
| `_ler_duracao(linha, posicao)` | Tenta `PADRAO_DURACAO.match(linha, posicao)`. Se casar, devolve o dígito e a posição depois dele. Se não (ex.: `A:9`), devolve `("", posicao)`: a nota fica sem duração e o `:` e o `9` são lidos depois como caracteres soltos. |
| `_ler_caractere(linha, posicao)` | Cria um token `CARACTERE` de um caractere e avança uma posição. |

Detalhe importante: o Tokenizador **nunca falha**. Qualquer caractere que ele não reconhece vira `CARACTERE`, e as regras decidem o que fazer com ele.

#### `contexto.py`: `ContextoInterpretacao`

O "estado compartilhado" enquanto **uma linha** é interpretada: o que uma regra pode ler e alterar. Um contexto novo é criado para cada linha, então a memória de "qual foi a nota anterior" não passa de uma voz para outra.

| Função | O que faz |
|--------|-----------|
| `__init__(voz, partitura)` | Guarda a voz que está sendo montada e a partitura, e começa sem token anterior e sem nota anterior. |
| `parametros()` | Atalho para os parâmetros da voz atual (`voz.parametros`). |
| `registrar_evento(evento)` | Adiciona o evento na voz e, se for nota, guarda em `nota_anterior`. |
| `anterior_foi_nota()` | `True` se o token **imediatamente anterior** era uma nota. |
| `avancar(token)` | Chamado pelo Parser depois de cada regra: o token atual vira o anterior. |
| `posicao_atual_beats()` | Repassa `voz.posicao_atual_beats()` (usado pela regra de andamento). |

Na Fase 1, `nota_anterior` ficava dentro do Parser. Ela veio para o contexto porque são as regras que precisam dela, e as regras não devem depender do Parser.

#### `parser.py`: `Parser`

Transforma o texto em `Partitura`, em duas etapas que já existiam na Fase 1:

1. `texto_to_token`: texto → tokens de cada linha (só forma);
2. `token_to_partitura`: tokens → Partitura (aplica o Mapeamento).

Os tokens ficam guardados em `self.tokens`. É isso que permite cumprir o requisito "alterar os parâmetros e tocar de novo **sem reinterpretar o texto**": a tela muda a `ConfiguracaoInicial` e o controlador chama só a etapa 2.

O Parser **não conhece nenhuma regra específica**: ele só pergunta ao Mapeamento.

| Função | O que faz |
|--------|-----------|
| `__init__(tokenizador, mapeamento, configuracao)` | Recebe as três dependências prontas (injeção de dependência). |
| `interpretar(texto)` | Atalho: `texto_to_token` + `token_to_partitura`. |
| `texto_to_token(texto)` | Separa em linhas e tokeniza cada uma (uma *list comprehension*). Guarda e devolve uma lista de listas: uma lista de tokens por linha. |
| `token_to_partitura(tokens=None)` | Cria uma `Partitura` com o BPM da configuração e, para cada linha (`enumerate` dá o índice), interpreta a linha e adiciona a voz. Se não receber tokens, usa os guardados. |
| `_separar_linhas(texto)` | `texto.splitlines()`, que aceita quebras `\n` e `\r\n` (Windows). Linhas em branco continuam contando: viram vozes em silêncio, e a numeração das vozes não muda. |
| `_interpretar_linha(indice, tokens, partitura)` | Cria a `Voz` com `configuracao.criar_parametros(indice)` (parâmetros novos, já com o ciclo de 4), cria um `ContextoInterpretacao` e aplica cada token. Devolve a voz pronta. |
| `_aplicar(token, contexto)` | `mapeamento.aplicar(token, contexto)` e depois `contexto.avancar(token)`. |

#### `regras/regra_mapeamento.py`: as classes base

Cada linha da tabela de mapeamento do enunciado é uma **regra**, e toda regra responde a duas perguntas.

`RegraMapeamento` (classe abstrata, `ABC`):

| Função | O que faz |
|--------|-----------|
| `aceita(token)` | Abstrata: "esta regra trata este token?". |
| `aplicar(token, contexto)` | Abstrata: executa o efeito (criar evento, mudar parâmetro...). |

`RegraPorCaractere(RegraMapeamento)` é uma base para as regras disparadas por um conjunto fixo de caracteres. Ela já implementa o `aceita()`, então as filhas só precisam escrever o `aplicar()`.

| Função | O que faz |
|--------|-----------|
| `__init__(caracteres)` | Guarda os caracteres num `frozenset` (ex.: `RegraPausa` recebe `"abcdefgh"`). |
| `aceita(token)` | `True` se o token é `CARACTERE` e o lexema está no conjunto. |

Como as classes base são abstratas (`ABC` + `@abstractmethod`), o Python não deixa criar uma regra que esqueceu de implementar `aplicar()`: dá erro na hora de instanciar.

#### `regras/regras_eventos.py`: regras que criam notas e pausas

| Classe | `aceita` | `aplicar` |
|--------|----------|-----------|
| `RegraNota` | `token.eh_nota()` | Cria uma nota com a duração do token ou, se não houver, `Duracao.padrao()`, usando os parâmetros atuais da voz, e registra no contexto. |
| `RegraPausa` (`RegraPorCaractere`) | caracteres `a`–`h` minúsculos | Registra uma pausa de duração padrão. Um `b` logo depois de uma nota nunca chega aqui, porque o Tokenizador já o leu como bemol. |
| `RegraRepetirOuPausar` | sempre `True` | É a **regra padrão** (o "senão" da tabela). Se o token anterior era nota, repete essa nota (mesma letra e duração, com os parâmetros atuais da voz); senão, faz uma pausa. |

Exemplo do comportamento da regra padrão: `AHH` gera nota, nota, pausa. O primeiro `H` vem logo depois de `A` e repete o Lá; o segundo `H` vem depois de outro `H` (que não é token de nota), então vira pausa.

#### `regras/regras_voz.py`: regras que mudam só a voz atual

| Classe | Caracteres | `aplicar` |
|--------|-----------|-----------|
| `RegraAtraso` | token `ATRASO` (seu próprio `aceita`) | `voz.set_atraso(token.valor)`. |
| `RegraVolume` | espaço | `parametros().dobrar_volume()`. |
| `RegraOitava(caracteres, sentido)` | `?` (+1) e `V` (−1) | Sobe ou desce a oitava. Uma classe só, com o sentido como parâmetro, em vez de duas classes quase iguais. |
| `RegraInstrumentoFixo(caracteres, programa)` | `!` → bandoneon; `;` e dígitos ímpares → sinos tubulares; `,` → agogô | `parametros().set_instrumento(programa)`. Uma classe reaproveitada em três linhas da tabela. |
| `RegraInstrumentoSomaDigito` | dígitos pares | `parametros().somar_ao_instrumento(int(token.lexema))`. A conta (somar e dar a volta depois de 127) fica no `ParametrosMusica`, que é quem conhece o limite. |

Os dígitos que chegam a essas regras são só os **soltos**: os de `:n` e `[n]` já foram consumidos pelo Tokenizador.

#### `regras/regras_globais.py`: regra que muda a música toda

| Classe | Caracteres | `aplicar` |
|--------|-----------|-----------|
| `RegraAndamento(caracteres, delta_bpm)` | `>` (+10) e `<` (−10) | Registra na Partitura uma `MudancaAndamento` na posição atual da voz. Não muda o BPM na hora: quem calcula o BPM em cada ponto é `Partitura.bpm_em`. |

#### `regras/mapeamento.py`: `Mapeamento`

A "tabela" que liga cada token à sua regra: uma lista **ordenada** de regras mais uma regra padrão.

| Função | O que faz |
|--------|-----------|
| `__init__(regras, regra_padrao)` | Guarda a lista e a regra padrão. |
| `padrao()` | Fábrica com o mapeamento da Fase 2. É o **único lugar** do código onde a tabela aparece. |
| `adicionar_regra(regra)` | Acrescenta uma regra no fim da lista, sem mudar nenhuma outra classe. |
| `encontrar_regra(token)` | Devolve a **primeira** regra cujo `aceita(token)` é verdadeiro; se nenhuma aceitar, a regra padrão. Usa `next(gerador, padrão)`. |
| `aplicar(token, contexto)` | `encontrar_regra(token).aplicar(token, contexto)`. |

A tabela montada por `padrao()`, na ordem em que as regras são testadas:

| Ordem | Regra | Dispara com |
|-------|-------|-------------|
| 1 | `RegraAtraso` | `[n]` no início da linha |
| 2 | `RegraNota` | `A`–`G` (com `#`/`b` e `:n` opcionais) |
| 3 | `RegraPausa` | `a`–`h` |
| 4 | `RegraVolume` | espaço |
| 5 | `RegraOitava("?", +1)` | `?` |
| 6 | `RegraOitava("V", -1)` | `V` |
| 7 | `RegraAndamento(">", +10)` | `>` |
| 8 | `RegraAndamento("<", -10)` | `<` |
| 9 | `RegraInstrumentoFixo("!", BANDONEON)` | `!` |
| 10 | `RegraInstrumentoFixo(";13579", TUBULAR_BELLS)` | `;` e dígitos ímpares |
| 11 | `RegraInstrumentoFixo(",", AGOGO)` | `,` |
| 12 | `RegraInstrumentoSomaDigito()` | dígitos pares |
| padrão | `RegraRepetirOuPausar()` | todo o resto (`H`, `O`, `I`, `U`, outras letras, símbolos) |

Este é o coração do **padrão Strategy**: o Parser chama `aplicar` sem saber qual regra concreta está do outro lado.

### 4.6 Pacote `saida/`: MIDI, som e arquivo

#### Um pouco de MIDI antes

- Um arquivo MIDI não guarda som; guarda **instruções**: "comece a tocar a nota 60 com força 100", "pare a nota 60", "use o instrumento 6".
- **MIDI tipo 1** tem várias **trilhas** tocando ao mesmo tempo. Usamos uma trilha para o andamento e uma por voz.
- O tempo é medido em **ticks**. Usamos 480 ticks por beat (`TICKS_POR_BEAT`).
- O `time` de cada mensagem é **delta**: ticks desde a mensagem anterior da mesma trilha.
- `set_tempo` usa microssegundos por beat, não BPM. `mido.bpm2tempo(120)` = 500000.
- `note_on` tem `velocity` (força da nota, 0–127): usamos o volume da voz. `note_off` termina a nota.
- `program_change` troca o instrumento de um canal.

#### `sintetizador.py`: `Sintetizador`

Converte uma `Partitura` em um `mido.MidiFile` em memória.

Mudanças da Fase 1: `gerar_onda(evento)` virou `gerar_mensagens(evento, canal)` (com MIDI não geramos forma de onda, e sim mensagens), e `exportar_midi` saiu daqui para o `ExportadorMidi` (gravar arquivo é outra responsabilidade).

| Função | O que faz |
|--------|-----------|
| `gerar_musica(partitura)` | Cria um `MidiFile(type=1, ticks_per_beat=480)`, adiciona a trilha de andamento e uma trilha por voz, e devolve o arquivo. |
| `_criar_trilha_andamento(partitura)` | Primeiro um `set_tempo` com o BPM inicial em `time=0`. Depois, para cada mudança (já ordenada), converte a posição em ticks, calcula o BPM daquele ponto com `partitura.bpm_em(...)` e adiciona um `set_tempo` com `time = tick - tick_anterior` (o delta). |
| `_criar_trilha_voz(voz)` | Anda pelos eventos acumulando a `espera` (em ticks). Começa com o atraso da voz. Pausa: só soma à espera. Nota: se o instrumento mudou desde a última nota, emite um `program_change` (carregando a espera); depois emite `note_on` com a espera acumulada e `note_off` com a duração da nota, e zera a espera. Se a voz termina com pausas, adiciona um `end_of_track` com a espera que sobrou, para a trilha durar até o fim do silêncio. |
| `gerar_mensagens(evento, canal)` | Para uma nota, devolve `[note_on, note_off]`: `note_on` com `velocity = volume` e `time=0`, `note_off` com `time` igual à duração em ticks. |
| `beats_para_ticks(beats)` | `round(beats × 480)`. Hoje todas as durações dão um número inteiro de ticks (até a semifusa, 0,0625 beat, dá 30), e o `round` é só uma proteção caso alguma conta gere casas decimais, já que o MIDI só aceita ticks inteiros. |

Como cada voz toca uma nota de cada vez, o `note_off` de uma nota sempre vem antes do `note_on` da próxima, e as contas de delta ficam simples.

#### `backend_audio.py`: `BackendAudio` e `BackendPygame`

`BackendAudio` é uma **interface** (classe abstrata) que diz o que um "aparelho de som" precisa saber fazer: `carregar(arquivo_midi)`, `tocar()`, `pausar()`, `retomar()`, `parar()` e `esta_tocando()`. O Player depende só dela.

`BackendPygame` é a implementação de verdade, usando `pygame.mixer.music`, que toca arquivos .mid direto. Usamos o **pygame-ce**, a versão do pygame mantida pela comunidade: o código continua com `import pygame`, mas ele tem pacotes prontos para as versões novas do Python (o pygame original não tem para o 3.14 e, sem pacote pronto, era instalado sem o módulo de som).

Quem transforma o MIDI em som muda conforme o sistema: no Windows e no macOS é o sintetizador do próprio sistema; no Linux é o **FluidSynth** (que vem junto com o pygame-ce), e ele precisa de um **banco de sons** (arquivo `.sf2`) com o timbre de cada instrumento. A constante `BANCOS_DE_SOM_LINUX` lista os lugares onde as distribuições costumam instalar esse arquivo.

| Função | O que faz |
|--------|-----------|
| `__init__()` | Marca que o mixer ainda não foi iniciado. |
| `_garantir_inicializado()` | Na primeira vez que for preciso (inicialização "preguiçosa"), escolhe o banco de sons e chama `pygame.mixer.init()`. Se o pygame não tiver o módulo de som, troca o erro técnico por um `AudioIndisponivelErro`. |
| `_escolher_banco_de_som()` | Só no Linux, e só se o usuário não escolheu um: procura o primeiro `.sf2` de `BANCOS_DE_SOM_LINUX` que existe e coloca o caminho na variável de ambiente `SDL_SOUNDFONTS`, que é onde o FluidSynth procura. |
| `carregar(arquivo_midi)` | Inicializa se precisar e carrega o arquivo no mixer. Se o computador não consegue tocar MIDI (ex.: Linux sem banco de sons), lança `AudioIndisponivelErro` com uma mensagem explicando o que instalar. Assim a tela mostra um aviso em vez de o programa mostrar um erro técnico. |
| `tocar()` / `pausar()` / `retomar()` | `play()`, `pause()`, `unpause()` do pygame. |
| `parar()` | Se o mixer já foi iniciado, para e descarrega o arquivo (`stop()` e `unload()`), liberando o arquivo temporário. |
| `esta_tocando()` | `pygame.mixer.music.get_busy()`, ou `False` se nada foi iniciado. |

Nos testes usamos um `BackendFalso` (em `tests/conftest.py`) que só anota as chamadas, então os testes rodam sem som e sem pygame tocando nada. Isso só é possível porque o Player depende da interface e não do pygame.

#### `player.py`: `Player`

Controla a reprodução da música já gerada.

| Função | O que faz |
|--------|-----------|
| `__init__(backend)` | Recebe o backend pronto. Começa sem música, sem tocar e sem pausa. |
| `carregar(musica)` | Para o que estiver tocando, guarda a música e grava o MIDI num arquivo temporário (`gerador_musical.mid` na pasta temporária do sistema), porque o pygame toca a partir de arquivo. |
| `tocar()` | Se não há música, lança `MusicaNaoGeradaErro`. Senão, manda o backend carregar o arquivo e tocar do início. Tocar de novo **não** recria a música nem reinterpreta o texto. |
| `parar()` | Para o backend e zera os estados. |
| `pausar()` | Só pausa se está tocando e não está pausado. |
| `retomar()` | Só retoma se está tocando e está pausado. |
| `terminou()` | `True` quando estava tocando, não está pausado e o backend diz que parou. A checagem de "não pausado" é importante: o pygame também responde "não estou tocando" durante a pausa. |

A reprodução é **assíncrona**: o pygame toca em segundo plano, e a interface continua respondendo enquanto a música toca.

Na Fase 3, `play()` e `stop()` viraram `tocar()` e `parar()`: são os mesmos nomes do `BackendAudio` e do `ControladorAplicacao`. Antes a mesma ação tinha dois nomes, um em inglês e outro em português (ver seção 10).

#### `exportador.py`: `Exportador` e `ExportadorMidi`

`Exportador` é uma classe abstrata com um único método, `exportar(midi, destino=None)`. Se um dia quisermos salvar em WAV ou MP3, basta criar outro exportador.

`ExportadorMidi` grava arquivos .mid. Constante: `EXTENSAO = ".mid"`.

| Função | O que faz |
|--------|-----------|
| `__init__(diretorio=None)` | Pasta onde salvar; `None` significa "a pasta padrão". Os testes passam uma pasta temporária aqui. |
| `exportar(midi, destino=None)` | Sem destino, monta `pasta / nome_padrao`. Cria a pasta se ela não existir (`mkdir(parents=True, exist_ok=True)`), grava com `midi.save` e devolve o caminho. |
| `diretorio_padrao()` | `~/Downloads` (`Path.home() / "Downloads"`). |
| `gerar_nome_padrao()` | `musica_AAAAMMDD_HHMMSS.mid`, com a data e hora atuais. Assim um arquivo novo nunca sobrescreve outro. |

### 4.7 Pacote `aplicacao/`: `ControladorAplicacao` e `ControladorConfiguracao`

São as **fachadas** do sistema: o único ponto de contato entre a interface e o resto. As telas só chamam métodos daqui e tratam `GeradorMusicalErro` para mostrar mensagens. Todas as dependências chegam prontas pelo construtor (montadas em `main.criar_controladores`).

Até a Fase 2 era uma classe só, com 23 métodos públicos que misturavam duas coisas: o fluxo da música e o ajuste de parâmetros. Na Fase 3 ela foi dividida em duas (ver seção 10, "Classe Grande").

#### `controlador.py`: `ControladorAplicacao`

O fluxo da música: texto → geração → reprodução → arquivo.

| Função | O que faz |
|--------|-----------|
| `__init__(entrada, parser, sintetizador, player, exportador)` | Guarda as dependências. `_musica` começa `None` (nada gerado). |
| `atualizar_texto(texto)` | Repassa o texto da tela para a `EntradaUsuario`. |
| `carregar_arquivo(caminho)` | Carrega o .txt e devolve o texto para a tela mostrar no campo. |
| `salvar_texto(caminho=None)` | Salva o texto (sobrescreve o original se veio de arquivo). |
| `texto_veio_de_arquivo()` | Pergunta à entrada se o texto tem arquivo de origem. |
| `limpar()` | Nova composição: para a música, esvazia a entrada e esquece a música gerada. |
| `gerar_musica()` | Valida (vazio → `TextoVazioErro`; caractere inválido → `FormatoInvalidoErro`), interpreta o texto e chama `_sintetizar_e_carregar`. |
| `regerar_com_novos_parametros()` | Chama só `parser.token_to_partitura()` (usa os tokens já lidos) e sintetiza de novo. É o requisito de mudar parâmetros sem reinterpretar o texto. |
| `musica_foi_gerada()` | `True` se já existe música. |
| `_sintetizar_e_carregar(partitura)` | Parte comum das duas anteriores: Partitura → MIDI → Player. |
| `tocar()` / `pausar()` / `retomar()` / `parar()` | Repassam ao Player, que usa os mesmos nomes. |
| `reproducao_terminou()` | `player.terminou()`. |
| `exportar_midi(destino=None)` | Se nada foi gerado, lança `MusicaNaoGeradaErro`; senão, pede ao exportador e devolve o caminho. |

#### `controlador_configuracao.py`: `ControladorConfiguracao` (Fase 3)

O BPM e os parâmetros iniciais de cada voz, que o painel de configurações lê e altera.

| Função | O que faz |
|--------|-----------|
| `__init__(configuracao, catalogo)` | Guarda a `ConfiguracaoInicial` (a mesma do Parser) e o catálogo de instrumentos. |
| `listar_instrumentos()` | Lista do catálogo, para o painel montar o menu. |
| `get_bpm()` / `set_bpm(bpm)` | BPM inicial da configuração. |
| `get_instrumento_voz(i)` / `set_instrumento_voz(i, programa)` | Instrumento inicial da voz `i`. |
| `get_oitava_voz(i)` / `set_oitava_voz(i, oitava)` | Oitava inicial da voz `i`. |
| `get_volume_voz(i)` / `set_volume_voz(i, volume)` | Volume inicial da voz `i`. |

Os `set_` não validam nada aqui: quem valida é a `ConfiguracaoInicial`, que lança `ValueError` fora dos limites. O painel captura esse erro e simplesmente ignora o clique (por exemplo, apertar `+` com o BPM já em 300).

Como as duas fachadas usam a **mesma** `ConfiguracaoInicial` que o Parser, o que o painel muda vale na próxima geração, inclusive em `regerar_com_novos_parametros()`.

### 4.8 Pacote `interface/`: as telas

A interface usa **tkinter**, que vem junto com o Python. O visual copia o croqui do Figma (cores, fonte pixelada Micro 5, cantos arredondados).

Como funciona uma interface gráfica: o programa monta as telas e entra no `mainloop()`, um laço que fica esperando **eventos** (clique, tecla, tempo passando). Cada botão tem uma função ligada a ele (um *callback*), chamada pelo tkinter quando o evento acontece. Por isso os métodos das telas se chamam `_ao_gerar`, `_ao_limpar`...: eles dizem **o que fazer ao** acontecer algo.

#### `estilo.py`: o tema visual

Cada tela é um **Canvas** (uma área de desenho) do tamanho do frame no Figma. As medidas no código são as mesmas do Figma (em pixels) e passam pela função `px()`, que multiplica pela escala. Assim, dá para conferir cada número no painel do Figma. Como o tkinter não tem cantos arredondados, botões e painéis são desenhados no Canvas, e o clique é ligado com `tag_bind`.

Constantes: as cores do Figma (`FUNDO = "#467385"`, `CARTAO = "#a4cbd2"`, `PAINEL = "#ffe7cf"`, `ESCURO = "#071f36"`, `VERMELHO = "#900b09"`); a fonte (`FAMILIA = "Micro 5"`, `FAMILIA_RESERVA = "Courier New"`, `ARQUIVO_FONTE`); os tamanhos de texto do Figma (`TITULO = 78`, `TEXTO = 65`); e os dados da escala (`ALTURA_REFERENCIA = 1232`, a altura da tela mais alta; `FRACAO_DO_MONITOR = 0.85`; `MARGEM_MONITOR = 140`). `ICONES` guarda os ícones como desenhos numa grade 24×24 (linhas, círculos e arcos).

Funções do módulo:

| Função | O que faz |
|--------|-----------|
| `preparar_sistema()` | Chamada **antes** de criar a janela. Carrega a fonte `Micro5-Regular.ttf` só para este programa, sem precisar instalar: no Windows chama `_preparar_windows()`, nos outros sistemas `_carregar_fonte_fontconfig()`. |
| `_preparar_windows()` | Avisa o Windows que o programa trata o zoom de tela sozinho (texto nítido em 125%/150%) e registra a fonte com `AddFontResourceExW` e `FR_PRIVATE` (vale só para este processo). |
| `_carregar_fonte_fontconfig()` | No Linux, o tkinter encontra as fontes pelo **fontconfig**. Esta função chama `FcConfigAppFontAddFile` da biblioteca fontconfig (via `ctypes`) para registrar o .ttf só para este programa. Se a biblioteca não existir (ex.: macOS sem fontconfig) ou algo falhar, o programa segue com a fonte reserva. |
| `preparar(janela)` | Chamada **depois** de criar a janela: se a fonte Micro 5 está disponível, usa ela (senão, Courier New um pouco menor); e calcula a escala para a tela mais alta ocupar 85% da altura livre do monitor. |
| `px(medida)` | Converte uma medida do Figma em pixels: `round(medida × escala)`. |
| `fonte(tamanho)` | Devolve `(família, -tamanho_em_pixels)`. O tamanho **negativo** no tkinter significa pixels (positivo seria pontos). |

Duas classes pequenas agrupam valores que antes viajavam soltos pelos métodos de desenho (Fase 3, ver seção 10, "Lista de Parâmetros Longa"). As duas são **objetos de valor** imutáveis (`@dataclass(frozen=True)`).

`Caixa(x, y, largura, altura)`: um retângulo em px do Figma, do jeito que aparece no painel de propriedades do Figma.

| Função | O que faz |
|--------|-----------|
| `centro` (propriedade) | O ponto do meio da caixa, `(x + largura/2, y + altura/2)`. Usado para centralizar o texto dos botões. |
| `em_pixels()` | Os quatro cantos já convertidos por `px()`: `(esquerda, topo, direita, base)`, o formato que o Canvas pede. |
| `ponto_da_grade(a, b, divisoes=24)` | Converte um ponto da grade 24×24 dos ícones para um ponto da tela dentro da caixa. |
| `expandida(margem_x, margem_y)` | Uma caixa maior, com a margem em cada lado. Usado na área de clique do deslizador. |

`EstiloTexto(tamanho, cor, ancora)`: como um texto aparece. A âncora diz qual ponto do texto fica na posição dada: `"nw"` canto superior esquerdo, `"n"` meio de cima, `"center"` meio, `"w"` meio da esquerda, `"ne"` canto superior direito. O método `com(**mudancas)` devolve uma cópia com algum valor trocado (ex.: `ESTILO_SECUNDARIO.com(ancora="ne")`). Estilos prontos, usados nas telas:

| Constante | Uso |
|-----------|-----|
| `ESTILO_TITULO` | "gerador de música" (tamanho 78, centralizado em cima). |
| `ESTILO_ROTULO` | Rótulos escuros como "texto de entrada:" e "upload:" (é o padrão). |
| `ESTILO_SECUNDARIO` | Rótulos azuis dentro dos painéis ("voz:", "volume:", "bpm:"...). |
| `ESTILO_BOTAO` | Texto creme no meio de botões e pílulas. |
| `ESTILO_VALOR` | Valor creme à esquerda de uma pílula (o número do bpm, o nome do instrumento). |

`_contorno_arredondado(esquerda, topo, direita, base, raio)` é uma função auxiliar do módulo: calcula os pontos do polígono de cantos arredondados (cada canto é um quarto de círculo, com seno e cosseno de 15 em 15 graus).

`Desenho(tk.Canvas)`, a área de desenho de cada tela:

| Função | O que faz |
|--------|-----------|
| `__init__(mestre, largura, altura)` | Cria o Canvas com o tamanho do frame do Figma convertido por `px()` e fundo `FUNDO`. |
| `retangulo(caixa, cor, raio=0, tags=())` | Retângulo de cantos arredondados (polígono de `_contorno_arredondado`). Com `raio=0`, um retângulo comum. |
| `circulo(caixa, cor, tags=())` | Círculo (ou elipse) preenchido dentro da caixa. |
| `texto(x, y, texto, estilo=ESTILO_ROTULO, tags=())` | Texto na fonte do tema, com o tamanho, a cor e a âncora do `EstiloTexto`. |
| `icone(nome, caixa, cor, espessura, tags)` | Desenha um ícone de `ICONES` dentro da caixa, convertendo os pontos da grade 24×24 com `caixa.ponto_da_grade`. |
| `pintar(item, cor)` | Troca a cor de uma forma (usado para pintar a aba de voz selecionada). |
| `widget(caixa, widget)` | Coloca um widget normal do tkinter (como o campo de texto) dentro da caixa, com `create_window`. |
| `nova_tag()` | Gera um nome único (`clicavel1`, `clicavel2`...) para agrupar os itens de um botão: fundo, texto e ícone. |
| `tornar_clicavel(tag, comando)` | Liga o clique em qualquer item com aquela tag ao `comando` e troca o cursor para "mãozinha" ao passar o mouse. |
| `botao(caixa, texto, comando, cor=ESCURO, raio=22)` | Botão completo: fundo arredondado + texto creme no meio + clique. Com `cor=ESCURO` é um botão principal; com `cor=FUNDO`, uma "pílula" secundária. Devolve os ids do fundo e do texto, para mudar depois (ex.: o texto "tocar" virar "pausar"). |

Exemplo de como uma tela desenha um botão: `d.botao(Caixa(66, 1077, 307, 76), "gerar música", self._ao_gerar)`. Os quatro números são exatamente o X, Y, W e H do botão no Figma.

`Deslizador`, a barra de volume do Figma (trilho fino e bolinha que se arrasta). Constantes: `DIAMETRO = 24` (bolinha) e `AREA_DE_CLIQUE = (15, 20)` (margem em volta do trilho que também aceita clique).

| Função | O que faz |
|--------|-----------|
| `__init__(desenho, trilho, minimo, maximo, comando)` | `trilho` é uma `Caixa`. Desenha uma área de clique invisível (`trilho.expandida(*AREA_DE_CLIQUE)`, para ficar fácil de acertar), o trilho e a bolinha. Liga clique e arrasto a `_ao_arrastar`. |
| `set(valor)` | Move a bolinha para a posição do valor, **sem** chamar o comando (usado quando a tela troca de voz). Valores fora do intervalo deixam a bolinha na ponta. |
| `_ao_arrastar(evento)` | Converte a posição do mouse numa fração de 0 a 1 do trilho, depois num valor entre mínimo e máximo, move a bolinha e chama o comando com o valor. |

#### `app.py`: `App`

A janela principal (herda de `tk.Tk`). Guarda as três telas e mostra uma de cada vez. Constante: `TITULO`.

| Função | O que faz |
|--------|-----------|
| `__init__(controlador, controlador_configuracao)` | Chama `estilo.preparar_sistema()`, cria a janela, chama `estilo.preparar(self)` e guarda os dois controladores. |
| `construir()` | Título, cor de fundo, janela de tamanho fixo (o layout segue as medidas do Figma) e cria as três telas, todas na mesma posição do grid. Mostra a principal. |
| `mostrar_tela(nome)` | Esconde todas as telas (`grid_remove`) e mostra só a pedida (`grid`). A janela fica do tamanho daquela tela. |
| `tela(nome)` | Dá acesso a uma tela (a de carregamento usa para entregar o texto à principal). |
| `mostrar_erro(mensagem)` | Caixa de erro (`messagebox.showerror`). |
| `mostrar_info(mensagem)` | Caixa de informação (`messagebox.showinfo`). |

As telas recebem o `App` e falam com o sistema por `self.app.controlador`; o painel de configurações recebe o `app.controlador_configuracao`. Elas usam `TYPE_CHECKING` para importar `App` só para as anotações de tipo, o que evita uma importação circular (o `app.py` importa as telas, e as telas precisariam importar o `app.py`).

#### `tela_principal.py`: `TelaPrincipal`

Frame "Pagina inicial" do Figma: botão de upload, campo de texto, painel de configurações e os botões "gerar música" e "limpar". Novidade da Fase 2 no mesmo estilo: a pílula "salvar texto".

Na Fase 3, todo o painel de configurações saiu daqui para a classe `PainelConfiguracoes` (abaixo). A tela tinha 25 métodos e 15 atributos; agora tem 13 métodos e cuida só do texto e dos botões (ver seção 10, "Classe Grande").

Constantes: `LARGURA, ALTURA = 813, 1232`.

Construção da tela:

| Função | O que faz |
|--------|-----------|
| `__init__(app)` | Guarda o app e o texto da última geração (`None`). |
| `construir()` | Cria o `Desenho`, desenha cabeçalho e campo de texto, cria o `PainelConfiguracoes` (passando o Canvas e o `app.controlador_configuracao`) e manda ele se construir, e por fim desenha os botões. |
| `_construir_cabecalho()` | Cartão azul-claro, botão redondo de upload (círculo + ícone, clicáveis juntos) e título. |
| `_construir_campo_texto()` | Rótulo, pílula "salvar texto", fundo creme e o `tk.Text` (com `wrap="none"`, porque cada linha é uma voz e não pode quebrar sozinha; `undo=True` liga o Ctrl+Z). Cria também a dica "digite aqui...", um `Label` posicionado dentro do campo que aparece só quando ele está vazio. |
| `_construir_botoes()` | "gerar música" e "limpar". |

Eventos (o que acontece quando o usuário interage):

| Função | O que faz |
|--------|-----------|
| `_ao_abrir_carregamento()` | Mostra a tela de upload. |
| `_ao_gerar()` | Pega o texto. Se é igual ao da última geração e já existe música, chama `regerar_com_novos_parametros()`; senão, atualiza o texto e chama `gerar_musica()`. Em erro, mostra a mensagem e fica na tela; em sucesso, guarda o texto gerado e vai para a reprodução. |
| `_ao_limpar()` | Limpa o controlador e o campo, e esquece o texto gerado. |
| `_ao_salvar_texto()` | Atualiza o texto no controlador. Se veio de arquivo, salva direto; senão, abre "salvar como" (se o usuário cancelar, não faz nada). Mostra onde salvou ou o erro. |
| `_ao_modificar_texto(evento)` | Chamado pelo evento `<<Modified>>` do campo. Rearma o evento (`edit_modified(False)`, senão ele só dispara uma vez) e atualiza a dica. |
| `_atualizar_dica()` | Esconde a dica se há texto, mostra se o campo está vazio. |
| `set_texto(texto)` | Troca todo o conteúdo do campo (usado depois de carregar um .txt). |
| `get_texto()` | Lê o campo de `"1.0"` (linha 1, coluna 0) até `"end-1c"`: o `-1c` tira o `\n` que o tkinter sempre acrescenta no fim. |

#### `painel_configuracoes.py`: `PainelConfiguracoes` (Fase 3)

O bloco "configurações:" do Figma, desenhado no Canvas da tela principal: abas de voz `v0`–`v3` (novidade da Fase 2), volume, bpm, instrumento e oitava. Volume, instrumento e oitava valem para a voz selecionada; o bpm vale para a música toda. Não é um widget do tkinter: é uma classe comum que recebe o `Desenho` onde desenhar e o `ControladorConfiguracao` com quem falar.

Constantes: `NUMERO_DE_VOZES = 4`, `VOLUME_MAXIMO = 100` (fim do deslizador, decisão do grupo), `PASSO_BPM = 10`, `ITENS_POR_COLUNA = 10` (lista de instrumentos em colunas, para não sair da tela). Atributo público: `voz_selecionada`.

| Função | O que faz |
|--------|-----------|
| `__init__(desenho, configuracao)` | Guarda o Canvas e o controlador; começa na voz 0. |
| `construir()` | Rótulo "configurações:", painel creme e os controles: seletor de voz, volume, bpm, instrumento e oitava. No fim seleciona a voz 0 para preencher os controles. |
| `_construir_seletor_voz(x, y)` | Rótulo "voz:" e quatro botões `v0`–`v3`. Guarda os ids dos fundos para pintar a aba selecionada. O `lambda i=i:` congela o valor de `i` em cada botão (sem o `i=i`, todos os botões usariam o último valor do laço). |
| `_construir_volume(x, y)` | Rótulo, valor numérico, ícone de alto-falante e o `Deslizador` de 0 a `VOLUME_MAXIMO`. |
| `_construir_contador(x, y, titulo, ao_mudar, passo)` | Constrói um contador reutilizável (rótulo + pílula com o valor + botões `-` e `+`), usado para o bpm e para a oitava. Devolve o id do texto do valor. |
| `_construir_instrumento(x, y)` | Pílula com o nome do instrumento e uma seta; ao clicar abre um `tk.Menu` com os instrumentos do catálogo em colunas. Monta o dicionário `programa → nome` usado para mostrar o nome. |
| `selecionar_voz(indice)` | Seleciona a voz, pinta a aba escolhida de escuro e as outras de azul, e atualiza os controles. |
| `_atualizar_controles()` | Copia do controlador para a tela os valores da voz selecionada: bpm, oitava, volume (texto e bolinha) e instrumento. |
| `_alterar(alteracao)` | Parte comum de bpm, oitava e instrumento: chama a função de alteração; se ela lançar `ValueError` (fora do limite), ignora o clique; senão, atualiza os controles. Antes o mesmo `try/except` estava repetido em cada evento. |
| `_ao_mudar_bpm(delta)` | `_alterar(set_bpm(atual + delta))`. |
| `_ao_mudar_oitava(delta)` | Igual, para a oitava da voz selecionada. |
| `_ao_mudar_volume(valor)` | Chamado pelo deslizador: salva o volume da voz e atualiza o número. |
| `_ao_abrir_lista_instrumentos()` | Abre o menu logo abaixo da pílula (`tk_popup` com a posição da tela). |
| `_ao_escolher_instrumento(programa)` | Salva o instrumento da voz selecionada (via `_alterar`). |

#### `tela_carregamento.py`: `TelaCarregamento`

Frame "upload botton" do Figma. Constantes: `LARGURA, ALTURA = 813, 527`.

| Função | O que faz |
|--------|-----------|
| `__init__(app)` | Guarda o app. |
| `construir()` | Cartão, título, "upload:", painel, a área "buscar arquivo..." (ícone de nuvem + texto, clicáveis juntos) e o botão "voltar". |
| `_ao_procurar_arquivo()` | Abre o diálogo de abrir arquivo (só .txt). Se o usuário cancelar, não faz nada; senão chama `carregar`. |
| `carregar(caminho)` | Pede ao controlador para carregar; em erro mostra a mensagem; em sucesso coloca o texto na tela principal e volta para ela. Fica separado do diálogo para poder ser testado sem abrir janela. |
| `_ao_voltar()` | Mostra a tela principal. |

#### `tela_reproducao.py`: `TelaReproducao`

Frame "Gerador de musica" do Figma. Aparece depois de gerar. Novidades da Fase 2: o play vira pausar/retomar, a pílula "parar", o estado no canto e o aviso de fim.

Constantes: `INTERVALO_VERIFICACAO_MS = 200`, `LARGURA, ALTURA = 813, 586`, `TAG_ICONE_PLAY`. Estados: `_tocando` e `_pausado`.

| Função | O que faz |
|--------|-----------|
| `__init__(app)` | Guarda o app e começa parada. |
| `construir()` | Cartão, título, "música gerada!", texto de estado, painel, "baixar midi", "salvar como...", botão de play (círculo + pílula, que fazem a mesma coisa), "parar" e "voltar". |
| `_ao_tocar_ou_pausar()` | O botão de play tem três papéis: parado → toca; tocando → pausa; pausado → retoma. |
| `_ao_tocar()` | Pede ao controlador para tocar (em erro, mostra a mensagem). Marca como tocando e agenda `_verificar_fim` com `after()`, só se ainda não havia uma verificação rodando. |
| `_ao_pausar_ou_retomar()` | Alterna entre pausar e retomar e atualiza o estado. |
| `_ao_parar()` | Para a música e zera os estados. |
| `_ao_baixar_midi()` | Exporta para Downloads com o nome padrão. |
| `_ao_salvar_midi_como()` | Abre "salvar como" para .mid e exporta no lugar escolhido. |
| `_exportar_midi(destino)` | Parte comum das duas anteriores: chama o controlador e mostra onde salvou ou o erro. |
| `_ao_voltar()` | Para a música, volta o estado para "pronta para tocar" e mostra a tela principal. |
| `_verificar_fim()` | Se não está mais tocando, para de verificar. Se a música acabou, para, mostra "fim" e avisa o usuário; senão, agenda a si mesmo de novo daqui a 200 ms. É um *polling* que não trava a interface. |
| `_mostrar_estado(texto)` | Escreve o estado no canto e ajusta o botão de play: texto "tocar", "pausar" ou "retomar", e ícone de play ou de pausa (apaga o ícone antigo pela tag e desenha o novo). |

Por que `after()` e não um laço `while`? Um `while` esperando a música acabar travaria o `mainloop`, e a janela pararia de responder. Com `after()`, o tkinter chama a verificação de tempos em tempos e continua atendendo os cliques no meio.

---

## 5. Testes

Os testes ficam em `tests/` e usam o **pytest**. Para rodar todos: `pytest` na pasta do projeto (hoje são **86 testes, todos passando**). Para rodar só um arquivo: `pytest tests/test_parser.py`; só os testes com uma palavra no nome: `pytest -k oitava`.

O `pyproject.toml` diz ao pytest onde estão os testes (`testpaths = ["tests"]`) e que a pasta do projeto entra no caminho de importação (`pythonpath = ["."]`), por isso os testes conseguem fazer `from gerador_musical...`.

### O que cada arquivo testa

| Arquivo | Testes | O que verifica |
|---------|--------|----------------|
| `test_musica.py` | 23 | `Duracao` (conversão 1–7, identificador inválido dá erro, cada figura vale metade da anterior); `NotaMusical` (Dó4 = 60, Lá4 = 69, sustenido e bemol); `ParametrosMusica` (dobrar volume, limite 127, oitava que passa do máximo volta ao padrão, descer oitava, voltar ao instrumento inicial, somar ao instrumento passando de 127 volta ao começo); `ConfiguracaoInicial` (padrões por voz, ciclo de 4 vozes, mudança do usuário aparece em `criar_parametros`); `Partitura` (`bpm_em` acumula mudanças, respeita limites, duração total conta o atraso); catálogo com pelo menos 25 instrumentos e com todos os obrigatórios. |
| `test_tokenizador.py` | 11 | Linha vazia, nota com e sem duração, sustenido, bemol, `b` sozinho é caractere, atraso só no início, dígito solto, `A:9` e o exemplo do enunciado `[4] C:2 D:2 E:3`. |
| `test_regras.py` | 13 | Cada regra isolada: nota usa os parâmetros da voz e a duração padrão; pausa; repetir quando o anterior era nota e pausar quando não era; volume; oitava; instrumento fixo; soma do dígito; atraso; andamento registrado na posição certa. E o `Mapeamento`: usa a regra padrão quando nenhuma aceita, e aceita uma regra nova sem mudar código. |
| `test_parser.py` | 7 | Integração Tokenizador + Mapeamento + Parser: cada linha vira uma voz, vozes começam com os padrões, atraso, andamento vale para todas as vozes, a nota anterior não passa de uma linha para outra, regerar sem reler o texto, caracteres estranhos não quebram o programa. |
| `test_entrada_usuario.py` | 8 | Texto só com espaços é vazio, alfabeto estrangeiro é inválido, acentos são válidos, carregar .txt, recusar arquivo que não é .txt, salvar por cima do original, salvar sem origem dá erro, `foi_modificado`. |
| `test_saida.py` | 12 | Sintetizador (uma trilha de andamento + uma por voz, `note_on`/`note_off` com volume e duração certos, `program_change` ao trocar instrumento, atraso em ticks, `set_tempo` ao mudar andamento, nenhuma voz no canal 9); Exportador (grava na pasta configurada e o arquivo pode ser lido de volta); Player (erro sem música, chamadas ao backend na ordem certa, tocar de novo não recria a música, pausado não conta como "terminou"). |
| `test_controladores.py` | 12 | **Fase 3.** `ControladorConfiguracao` (lista os 30 instrumentos, altera os valores da voz, valores fora do limite dão `ValueError`); `ControladorAplicacao` montado como no `main.py`, mas com backend falso (texto vazio, formato incorreto, exportar sem gerar, gerar + tocar + exportar, regerar usa o BPM novo do painel, limpar para a música). Servem de "rede de segurança" da refatoração: garantem que separar o controlador não mudou o comportamento. |

### Técnicas usadas

- **Teste unitário × teste de integração.** `test_regras.py` testa cada regra sozinha (unitário). `test_parser.py` e `test_saida.py` usam várias peças reais juntas (integração).
- **Fixtures** (`tests/conftest.py`). O pytest entrega objetos prontos para os testes que os pedem pelo nome do parâmetro: `contexto` (uma voz com cravo, oitava 6, volume 40, numa partitura de 120 bpm) e `backend` (o backend falso). O `conftest.py` é lido automaticamente pelo pytest.
- **Dublês de teste (*test doubles*).** O `BackendFalso` finge ser o pygame e só anota as chamadas. Assim testamos o Player sem tocar som. Isso só funciona porque o Player depende da interface `BackendAudio`.
- **`@pytest.mark.parametrize`.** Roda o mesmo teste com vários valores (ex.: identificadores 1, 3 e 7).
- **`pytest.raises`.** Verifica que um erro **é** lançado quando deveria.
- **`tmp_path`.** Fixture do próprio pytest que dá uma pasta temporária, para testar leitura e gravação de arquivos sem sujar o computador.

### O que não tem teste automático

A interface (telas tkinter) e o `BackendPygame` (som de verdade) não têm testes automáticos: dependem de janela e de placa de som. Eles são testados à mão, rodando o programa. Na Fase 3, para conferir que a refatoração da interface não mudou nada, rodamos as telas antes e depois, clicando nos mesmos lugares, e comparamos as capturas de tela: ficaram idênticas.

---

## 6. Conceitos de Desenvolvimento de Software no código

### 6.1 Abstração e encapsulamento

- **Abstração** é mostrar só o que importa. Quem usa a `Partitura` pergunta `bpm_em(5)` e não precisa saber como as mudanças estão guardadas. Quem usa o `Player` chama `tocar()` e não sabe que existe um arquivo temporário.
- **Encapsulamento** é esconder o estado interno e só deixar mexer por métodos. Ex.: os valores da `ConfiguracaoInicial` estão em listas privadas (`_instrumentos`, `_oitavas`, `_volumes`) e só mudam pelos `set_`, que **validam** antes. Os métodos `get_eventos()`, `get_vozes()` e `listar()` devolvem **cópias**, para ninguém alterar a lista interna por fora.

### 6.2 Coesão e acoplamento

- **Alta coesão**: cada classe faz uma coisa só, e tudo dentro dela tem a ver com essa coisa. `ArquivoTexto` só mexe com disco; `Tokenizador` só reconhece a forma do texto; `ExportadorMidi` só grava arquivos.
- **Baixo acoplamento**: as classes se conhecem o mínimo possível. O Sintetizador recebe uma `Partitura` e não sabe nada de texto; a interface só conhece o controlador; as regras só conhecem o `ContextoInterpretacao`.

### 6.3 SOLID

| Princípio | O que diz | Onde aparece |
|-----------|-----------|--------------|
| **S**: Responsabilidade Única | Uma classe deve ter um único motivo para mudar. | `ArquivoTexto` (disco) separado de `EntradaUsuario` (regras do texto); `Tokenizador` (forma) separado do `Parser` (significado); `Sintetizador` (gerar MIDI) separado do `ExportadorMidi` (gravar) e do `Player` (tocar). Na Fase 3: `ControladorAplicacao` (fluxo da música) separado do `ControladorConfiguracao` (parâmetros), e `TelaPrincipal` (texto e botões) separada do `PainelConfiguracoes`. |
| **O**: Aberto/Fechado | Aberto para extensão, fechado para modificação. | Para criar um comando novo, escreve-se uma regra nova e ela entra em `Mapeamento.padrao()` ou por `adicionar_regra()`. O `Parser` e o `Mapeamento` não mudam. O teste `test_mapeamento_aceita_regra_nova_sem_mudar_codigo` demonstra isso. O mesmo vale para um novo formato de exportação (nova subclasse de `Exportador`) ou um novo jeito de tocar som (nova subclasse de `BackendAudio`). |
| **L**: Substituição de Liskov | Uma subclasse deve poder substituir a classe mãe sem quebrar nada. | Qualquer `RegraMapeamento` funciona no lugar de outra para o `Mapeamento`; o `BackendFalso` substitui o `BackendPygame` no `Player`; `ExportadorMidi` substitui `Exportador` no controlador. |
| **I**: Segregação de Interfaces | Interfaces pequenas, específicas. | `RegraMapeamento` tem só dois métodos (`aceita` e `aplicar`); `Exportador` tem um (`exportar`); `BackendAudio` tem só o que o Player usa. |
| **D**: Inversão de Dependência | Depender de abstrações, não de implementações. | O `Player` depende de `BackendAudio` (abstrato), não do pygame. O `ControladorAplicacao` recebe um `Exportador` (abstrato). As dependências são criadas fora e **injetadas** pelo construtor, e o único lugar que escolhe as classes concretas é o `main.py`. |

### 6.4 Padrões de projeto

| Padrão | Onde | Para quê |
|--------|------|----------|
| **Strategy** | `RegraMapeamento` e suas subclasses, usadas pelo `Mapeamento` | Cada regra é uma "estratégia" para tratar um token. O Parser chama `aplicar` sem saber qual regra concreta é. Trocar o mapeamento é trocar as estratégias. |
| **Chain of Responsibility** (variação) | `Mapeamento.encontrar_regra` | O token passa pelas regras em ordem até alguma aceitar; se nenhuma aceitar, a regra padrão trata. |
| **Fachada (Facade)** | `ControladorAplicacao` e `ControladorConfiguracao` | Uma interface simples para um sistema com muitas peças. As telas chamam `gerar_musica()` e não precisam saber que isso envolve entrada, parser, sintetizador e player. São duas fachadas pequenas em vez de uma grande, cada uma para um assunto. |
| **Adaptador (Adapter)** | `BackendPygame` | Adapta a API do pygame (`play`, `unpause`, `get_busy`) à interface que o sistema espera (`tocar`, `retomar`, `esta_tocando`). |
| **Método de fábrica (Factory Method)** | `Mapeamento.padrao()`, `ConfiguracaoInicial.padrao()`, `CatalogoInstrumentos.padrao()`, `EventoMusical.criar_nota()`/`criar_pausa()`, `ConfiguracaoInicial.criar_parametros()`, `Duracao.from_identificador()` | Criar objetos já configurados, com um nome que explica o que está sendo criado. |
| **Objeto de valor (Value Object)** | `NotaMusical`, `Instrumento`, `Token`, `MudancaAndamento`, e na interface `Caixa` e `EstiloTexto` (dataclasses `frozen`) | Objetos imutáveis comparados pelo conteúdo. Não podem ser alterados por engano depois de criados. |
| **Injeção de dependência + Composition Root** | construtores de `Parser`, `Player`, `ControladorAplicacao`, `ControladorConfiguracao`, `ExportadorMidi`; `main.criar_controladores()` | Cada classe recebe o que precisa em vez de criar sozinha, e só o `main.py` decide as peças concretas. Facilita testes e trocas. |
| **MVC / camadas** | `musica` (modelo), `interface` (visão), `aplicacao` (controle) | Separar dados e regras da apresentação. |
| **Programação orientada a eventos** | telas tkinter (`_ao_...`, `mainloop`, `after`) | A interface reage a eventos (clique, tempo) em vez de seguir um roteiro fixo. |

### 6.5 Herança, polimorfismo e classes abstratas

- **Herança**: `RegraPausa`, `RegraVolume`, `RegraOitava` etc. herdam de `RegraPorCaractere`, que herda de `RegraMapeamento`. A classe do meio existe para **reaproveitar** o `aceita()` que seria igual em todas.
- **Polimorfismo**: o mesmo chamado `regra.aplicar(token, contexto)` faz coisas diferentes dependendo da regra. O `Mapeamento` não usa nenhum `if` para saber qual é qual.
- **Classes abstratas** (`ABC` + `@abstractmethod`): `RegraMapeamento`, `BackendAudio` e `Exportador` não podem ser instanciadas; servem de contrato.
- **Parametrização em vez de classes repetidas**: `RegraOitava("?", +1)` e `RegraOitava("V", -1)` são a mesma classe com parâmetros diferentes; o mesmo para `RegraAndamento` e `RegraInstrumentoFixo`. Isso evita código duplicado (princípio **DRY**, *Don't Repeat Yourself*).

### 6.6 Tratamento de erros

- Uma **hierarquia de exceções** do domínio (`excecoes.py`) para os erros esperados, com uma base comum. A interface trata todos com um `except GeradorMusicalErro` e mostra a mensagem.
- **Validação nas bordas**: o texto é validado no controlador antes de interpretar; valores de configuração são validados na `ConfiguracaoInicial`. Dentro da interpretação, nada quebra: qualquer caractere desconhecido cai na regra padrão.
- **Mensagens específicas**: "texto vazio", "formato incorreto", "Gere a música antes de salvar.".

### 6.7 Outras boas práticas

- **Constantes nomeadas** em vez de números mágicos (`limites.py`, `TICKS_POR_BEAT`, `PASSO_BPM`, `CANAL_PERCUSSAO_MIDI`).
- **Enums** para conjuntos fechados de valores (`Duracao`, `Acidente`, `TipoToken`, `TipoEvento`).
- **Anotações de tipo** (`def bpm_em(self, posicao_beats: float) -> int`), que documentam o código e ajudam a IDE a achar erros.
- **Docstrings** no padrão do pydoc, explicando o porquê das decisões e marcando o que mudou da Fase 1 para a Fase 2 e o que foi refatorado na Fase 3.
- **Cópias defensivas** (`list(self.vozes)`) e **foto dos parâmetros** nos eventos, para evitar *aliasing* (dois lugares mexendo no mesmo objeto sem querer).
- **Separação léxico/semântico**, como em compiladores: o Tokenizador nunca decide significado, e o Parser nunca olha caractere por caractere.
- **YAGNI** (*You Aren't Gonna Need It*): na Fase 3 apagamos o código que não era usado em lugar nenhum (`Voz.ultima_nota`, `Token.eh_caractere`, `Sintetizador.partitura`). Algumas funções ainda existem sem uso no programa (seção 8).

### 6.8 Evolução da Fase 1 para a Fase 2

O enunciado pede para **re-projetar acrescentando classes às da Fase 1**. Foi o que fizemos:

| Classe | Situação | O que mudou |
|--------|----------|-------------|
| `EntradaUsuario` | da Fase 1, estendida | Lembra o arquivo de origem; `salvar_arquivo`, `foi_modificado`, `veio_de_arquivo`, `limpar`. |
| `ParametrosMusica` | da Fase 1, adaptada | Agora é **por voz**; o BPM saiu; `decrementar_oitava`, `reset_instrumento`, `resetar`. |
| `EventoMusical` | da Fase 1, adaptada | Nota virou `NotaMusical`, duração virou `Duracao`, `eh_acao()` saiu. |
| `Parser` | da Fase 1, adaptado | Mantém as duas etapas; não conhece mais as regras (usa o `Mapeamento`); a nota anterior foi para o contexto; cria uma voz por linha. |
| `Sintetizador` | da Fase 1, adaptado | `gerar_onda` virou `gerar_mensagens` (MIDI); exportar saiu para o `ExportadorMidi`. |
| `Player` | da Fase 1, adaptado | Depende de `BackendAudio`; `carregar`, `terminou`. |
| `ArquivoTexto` | nova | Mudança 1 (ler/salvar .txt). |
| `Duracao`, `Acidente`, `NotaMusical` | novas | Mudança 4 (durações e acidentes). |
| `Instrumento`, `CatalogoInstrumentos` | novas | Mudança 3 (pelo menos 25 instrumentos). |
| `ConfiguracaoInicial`, `Voz`, `Partitura`, `MudancaAndamento` | novas | Mudança 4 (linhas = vozes, padrões por voz, andamento global). |
| `Token`, `Tokenizador`, `ContextoInterpretacao` | novas | Unidades com mais de um caractere (`C#:3`, `[4]`). |
| `RegraMapeamento` e as regras, `Mapeamento` | novas | Mapeamento fácil de mudar (o enunciado avisa que ele muda a cada fase). |
| `ExportadorMidi`, `BackendAudio`, `BackendPygame` | novas | Mudança 2 (salvar MIDI) e reprodução testável. |
| `ControladorAplicacao` | nova | Separar a interface do resto. |

---

## 7. Requisitos e onde eles são atendidos

| Requisito | Onde no código |
|-----------|----------------|
| Mudança 1: carregar um .txt, editar e salvar (sobrescrevendo o original) | `ArquivoTexto`; `EntradaUsuario.carregar_arquivo`/`salvar_arquivo`; `TelaCarregamento`; `TelaPrincipal._ao_salvar_texto` |
| Mudança 2: salvar a música em MIDI | `Sintetizador` + `ExportadorMidi`; "baixar midi" e "salvar como..." na `TelaReproducao` |
| Mudança 3: pelo menos 25 instrumentos, incluindo os obrigatórios | `CatalogoInstrumentos.padrao()` (30); lista de instrumentos na tela; testes `test_catalogo_*` |
| Mudança 4: novo mapeamento (durações `:n`, sustenido e bemol, `H` deixou de ser nota) | `Tokenizador`, `Duracao`, `Acidente`, `NotaMusical`, regras |
| Mudança 4: cada linha é uma voz, com oitava, volume e instrumento iniciais próprios | `Parser._interpretar_linha`, `Voz`, `ConfiguracaoInicial` (padrões e ciclo de 4) |
| Mudança 4: atraso `[n]` no início da linha | `Tokenizador._ler_atraso`, `RegraAtraso`, `Sintetizador._criar_trilha_voz` |
| Mudança 4: `>` e `<` mudam o BPM da música toda | `RegraAndamento`, `MudancaAndamento`, `Partitura.bpm_em`, trilha de andamento |
| Mudança 4: `?` sobe e `V` desce a oitava | `RegraOitava`, `ParametrosMusica` |
| Mensagens "texto vazio" e "formato incorreto" | `ControladorAplicacao.gerar_musica`, `EntradaUsuario`, exceções |
| Alterar parâmetros e gerar de novo sem reinterpretar o texto | `PainelConfiguracoes` + `ControladorConfiguracao`; `Parser.token_to_partitura` com tokens guardados; `regerar_com_novos_parametros`; `TelaPrincipal._ao_gerar` |
| Pausar, retomar e parar; aviso de fim | `Player`, `TelaReproducao` (`_verificar_fim` com `after`) |
| Interface não trava enquanto toca | reprodução assíncrona do pygame + `after()` em vez de laço |
| Mapeamento fácil de mudar | regras como classes + `Mapeamento.padrao()` como único lugar da tabela |
| Interface separada da lógica | `ControladorAplicacao` e `ControladorConfiguracao`; a interface só importa os controladores e as exceções |

---

## 8. Pontos de atenção e pequenas melhorias

Já arrumado: os docstrings desatualizados e os "TODO" de decisões já tomadas (na revisão do pydoc), e, na Fase 3, o import sem uso em `nota_musical.py`, a docstring duplicada em `CatalogoInstrumentos.padrao()`, o `== True` em `contexto.py`, o atributo `Sintetizador.partitura` que nunca era lido e as funções `Voz.ultima_nota` e `Token.eh_caractere`, que não eram usadas nem nos testes.

O que ainda vale o grupo decidir (nenhum item quebra o programa):

1. **Regra `.` da Fase 1**: na Fase 1, `.` também subia uma oitava, e o enunciado da Fase 2 não tirou essa regra. Hoje só `?` sobe. Se o grupo quiser seguir à risca, é trocar `RegraOitava("?", +1)` por `RegraOitava("?.", +1)` em `Mapeamento.padrao()`. Ficou fora da Fase 3 de propósito: refatorar não deve mudar o comportamento do programa.
2. **Funções sem uso no programa** (só nos testes, ou com uso planejado): `Partitura.esta_vazia`, `ParametrosMusica.resetar`, `ConfiguracaoInicial.restaurar_padroes`, `NotaMusical.nome`, `CatalogoInstrumentos.nome_de`, `EntradaUsuario.foi_modificado`. Decidam: apagar (YAGNI) ou usar (ex.: um botão "restaurar padrões" que chama `restaurar_padroes`, ou avisar "texto modificado, deseja salvar?" com `foi_modificado`).
3. **Espaço dobra o volume**: em textos com espaços entre as notas (como o exemplo do enunciado `[4] C:2 D:2 E:3`), o volume chega em 127 muito rápido. Está registrado como decisão no README; se o grupo quiser mudar, basta trocar o caractere da `RegraVolume` em `Mapeamento.padrao()`.
4. **Convenção de oitava**: hoje Dó4 = 60 (padrão MIDI). Algumas bibliotecas, como o JFugue (Java), usam Dó5 = 60. Se o grupo mudar, é só a fórmula de `NotaMusical.altura_midi` e os testes que conferem os números.

---

## 9. Perguntas que o professor pode fazer

**Por que separar Tokenizador e Parser?**
Porque são responsabilidades diferentes: o Tokenizador reconhece a forma (`C#:3` é uma nota com acidente e duração) e o Parser decide o significado. Se o mapeamento mudar, o Tokenizador não muda; se a sintaxe de uma nota mudar, as regras não mudam.

**Como vocês fariam se o professor mudasse o mapeamento de novo?**
Criaríamos (ou ajustaríamos) classes de regra e mudaríamos só a lista em `Mapeamento.padrao()`. Parser, Sintetizador e interface não mudam. É o Aberto/Fechado com o padrão Strategy.

**O que acontece com um caractere que não está na tabela?**
O Tokenizador transforma em `CARACTERE`, nenhuma regra aceita, e o `Mapeamento` aplica a regra padrão `RegraRepetirOuPausar`: repete a nota anterior se o token anterior era nota, senão faz uma pausa. Nada quebra: há um teste que passa `@#$%&*()` e até caracteres japoneses direto para o Parser. No uso normal, caracteres de outros alfabetos nem chegam ao Parser, porque o controlador barra antes com "formato incorreto".

**Como o programa sabe que `Bb` é Si bemol e não "Si" seguido de pausa?**
O Tokenizador, ao ler uma letra de nota, olha o próximo caractere; se for `#` ou `b`, ele faz parte da nota. Um `b` que não vem depois de uma nota vira caractere e depois pausa.

**Por que o evento guarda instrumento, oitava e volume, se a voz já tem os parâmetros?**
Porque os parâmetros da voz mudam enquanto o texto é lido. O evento guarda uma "foto" do momento em que a nota foi lida. Se guardasse a referência, um `?` lido depois mudaria as notas anteriores.

**Por que `MudancaAndamento` guarda o delta e não o BPM?**
Porque as linhas são interpretadas uma de cada vez. Uma mudança na linha 2 pode acontecer **antes**, no tempo, de uma mudança na linha 1. Só depois de juntar e ordenar todas é possível calcular o BPM de cada ponto (`Partitura.bpm_em`).

**Como funciona o "gerar de novo sem reinterpretar o texto"?**
O Parser guarda os tokens. Se o texto não mudou, a tela chama `regerar_com_novos_parametros()`, que roda só `token_to_partitura()` com a `ConfiguracaoInicial` atualizada.

**Para que servem os controladores?**
São as fachadas: a interface só fala com eles. Isso desacopla as telas do resto. Trocar tkinter por outra interface não exige mexer na interpretação nem na saída. São dois porque são dois assuntos: o `ControladorAplicacao` cuida do fluxo da música e o `ControladorConfiguracao` dos parâmetros iniciais (antes era um só, com 23 métodos públicos).

**Por que o Player não usa o pygame direto?**
Inversão de dependência: ele depende da interface `BackendAudio`. Assim os testes usam um `BackendFalso` sem som, e poderíamos trocar o pygame por outra biblioteca sem mudar o Player.

**Onde as peças concretas são escolhidas?**
Só em `main.criar_controladores()` (composition root). O resto do código recebe as dependências prontas pelo construtor.

**Por que a interface não trava enquanto a música toca?**
O pygame toca em segundo plano, e a tela verifica o fim com `after(200, ...)`, que agenda a verificação sem bloquear o `mainloop` do tkinter.

**O que é o canal 9 e por que pular?**
No padrão General MIDI, o canal 10 (índice 9) é reservado para bateria: qualquer nota nele vira um som de percussão. Por isso `Voz.canal_midi()` pula esse canal.

**Como a quinta linha do texto ganha os valores da primeira?**
`ConfiguracaoInicial._indice_no_ciclo` usa `indice % 4`: a voz 4 usa os valores da voz 0, a voz 5 os da voz 1, e assim por diante.

**O que é um tick e por que 480?**
É a menor unidade de tempo do arquivo MIDI. 480 por beat é um valor comum, e com ele todas as durações do enunciado (até a semifusa, 1/16 de beat = 30 ticks) dão números inteiros.

**Como vocês testaram?**
86 testes automáticos com pytest: unitários (regras, modelo musical, tokenizador) e de integração (parser, sintetizador, exportador, controladores). O som é testado com um dublê (`BackendFalso`). A interface foi testada rodando o programa.

**Usaram código de terceiros?**
As bibliotecas mido (gerar o MIDI) e pygame-ce (tocar), a tkinter (que vem com o Python) e a fonte Micro 5 (licença OFL). Está tudo listado no README.

---

## 10. Fase 3: bad smells e refatorações

Na Fase 3, outro grupo vai revisar o nosso código usando o checklist de 10 bad smells do professor. O próprio checklist sugere que o grupo autor faça uma **autoavaliação** antes de entregar o código. Foi o que fizemos: passamos os 10 smells no código e usamos as ferramentas que o enunciado recomenda para Python, o **Radon** (complexidade) e o **Pylint** (avisos de design como "muitos argumentos" e "muitos métodos públicos").

**Refatorar** é mudar a estrutura do código sem mudar o que ele faz. Para garantir que nada mudou: os 73 testes que já existiam continuam passando (agora são 86, com os novos), e as telas foram rodadas antes e depois, clicando nos mesmos lugares, com capturas de tela idênticas.

### 10.1 Checklist dos 10 smells

| # | Smell | Resultado | Onde estava e o que fizemos |
|---|-------|-----------|-----------------------------|
| 1 | Código Duplicado | **Refatorado** | `TelaPrincipal._ao_mudar_bpm` e `_ao_mudar_oitava` repetiam o mesmo `try / except ValueError / atualizar controles`. **Extrair Método**: virou `PainelConfiguracoes._alterar`, usado também na escolha de instrumento. A conversão dos quatro cantos de um retângulo para pixels (`px(x), px(y), px(x + largura), px(y + altura)`) aparecia em `retangulo`, `circulo` e no `Deslizador`; agora é `Caixa.em_pixels()`. O mapeamento texto → música não tem duplicação: cada comando é uma regra, e regras parecidas são a mesma classe com parâmetros (`RegraOitava("?", +1)` e `RegraOitava("V", -1)`). |
| 2 | Classe Grande | **Refatorado** | `ControladorAplicacao` tinha 23 métodos públicos (fluxo da música + ajuste de parâmetros). **Extrair Classe**: os 9 métodos de parâmetros foram para o `ControladorConfiguracao`. `TelaPrincipal` tinha 25 métodos, 15 atributos e 337 linhas (texto + todo o painel). **Extrair Classe**: o painel virou `PainelConfiguracoes`, e a tela ficou com 13 métodos, 6 atributos e 168 linhas. |
| 3 | Método Longo | OK | Nenhum método com lógica passa de 20 linhas. O mais longo é `CatalogoInstrumentos.padrao()` (32 linhas), mas ele é só a lista dos 30 instrumentos, sem nenhum `if` ou laço. A maior complexidade ciclomática do projeto (Radon) é 6, em `Desenho.icone` (nota B; todo o resto é nota A). |
| 4 | Lista de Parâmetros Longa | **Refatorado** | Os métodos de desenho recebiam 7 ou 8 valores soltos, ex.: `botao(x, y, largura, altura, texto, comando, cor, raio)` e `texto(x, y, texto, tamanho, cor, ancora, tags)`. **Introduzir Objeto-Parâmetro**: posição e tamanho viraram uma `Caixa`, e tamanho, cor e âncora do texto viraram um `EstiloTexto`. Agora nenhum método passa de 5 parâmetros. O construtor do `ControladorAplicacao` também caiu de 7 para 5, como consequência do item 2. |
| 5 | Inveja de Recursos | **Refatorado** | `RegraInstrumentoSomaDigito.aplicar` pegava o instrumento do `ParametrosMusica`, fazia a conta com o limite 127 e devolvia o resultado: estava mais interessada nos dados de outra classe do que nos seus. **Mover Método**: a conta virou `ParametrosMusica.somar_ao_instrumento(n)`, e a regra só chama esse método. As outras regras já faziam assim (`incrementar_oitava()`, `dobrar_volume()`), que é exatamente o exemplo do checklist. |
| 6 | Obsessão por Tipos Primitivos | **Refatorado em parte** | O modelo já usa objetos pequenos: `NotaMusical` (letra + acidente, e sabe calcular seu valor MIDI), `Duracao` (Enum), `Instrumento`, `Token`, `EventoMusical`. Na interface, as posições eram quatro números soltos em toda chamada; agora são `Caixa`. Volume e oitava continuam `int` de propósito: os limites ficam num lugar só (`limites.py`) e são validados em um lugar só (`ParametrosMusica` e `ConfiguracaoInicial`). Uma classe `Volume` acrescentaria uma classe sem tirar nenhuma regra repetida. |
| 7 | Switch Statements | OK | Não existe `switch` nem cadeia de `if/elif` por caractere: cada comando é uma subclasse de `RegraMapeamento` e o `Mapeamento` escolhe por polimorfismo (padrão Strategy), que é a correção sugerida no próprio checklist. Os poucos `if/elif` que existem são pequenos e locais (ex.: `TelaReproducao._mostrar_estado` escolhe entre "tocar", "pausar" e "retomar"). |
| 8 | Cirurgia com Espingarda | Analisado, mantido | Um **comando novo** no texto é uma mudança local: uma classe de regra nova e uma linha em `Mapeamento.padrao()`. Já um **parâmetro novo por voz** (ex.: pan, esquerda/direita) mexeria em várias classes: `ParametrosMusica` (valor atual), `ConfiguracaoInicial` (valor inicial), `EventoMusical` (foto na nota), `Sintetizador` (mensagem MIDI), `ControladorConfiguracao` e `PainelConfiguracoes` (tela). É o ponto mais fraco que sobra. Mantivemos porque cada classe muda pela sua própria responsabilidade (modelo, valor inicial, MIDI, tela), que é o custo normal de separar em camadas; juntar tudo numa classe só traria de volta a Classe Grande. |
| 9 | Comentários | OK | Não há código comentado, e os comentários de linha explicam o **porquê** (ex.: `# "end" traria um \n a mais`). Todos os métodos têm docstring no padrão do pydoc; alguns curtos repetem o nome (ex.: `get_bpm`: "Devolve o BPM inicial."), mantidos para a documentação gerada ficar completa. Na Fase 3 apagamos uma docstring duplicada em `CatalogoInstrumentos.padrao()`. |
| 10 | Classes Alternativas com Interfaces Diferentes | **Refatorado** | A mesma ação tinha dois nomes: `Player.play()` e `Player.stop()`, mas `BackendAudio.tocar()`/`parar()` e `ControladorAplicacao.tocar()`/`parar()`. **Renomear Método**: o Player passou a usar `tocar()` e `parar()`. A interface comum de áudio (`BackendAudio`, abstrata) já existia desde a Fase 2, e é o que permite trocar o pygame pelo `BackendFalso` nos testes. |

Aproveitamos para tirar também o que não era usado em lugar nenhum (nem nos testes): `Voz.ultima_nota`, `Token.eh_caractere`, o atributo `Sintetizador.partitura`, o `import and_` em `nota_musical.py` e o `== True` em `contexto.py`.

### 10.2 Antes e depois, em números

| Medida | Antes | Depois |
|--------|-------|--------|
| Avisos de design do Pylint (muitos argumentos, muitos métodos públicos, muitos atributos, import sem uso, string sem efeito) | 20 | 3 |
| Métodos públicos do `ControladorAplicacao` | 23 | 14 (+ 9 no `ControladorConfiguracao`) |
| `TelaPrincipal`: métodos / atributos / linhas | 25 / 15 / 337 | 13 / 6 / 168 |
| Maior número de parâmetros num método de desenho | 8 | 5 |
| Complexidade ciclomática média (Radon) | 1,59 (A) | 1,56 (A) |
| Testes automáticos, todos passando | 73 | 86 |

Os 3 avisos que sobraram, e por que ficaram:

- `PainelConfiguracoes` tem 12 atributos (o Pylint sugere no máximo 7). São os controles que ele precisa atualizar quando a voz muda: rótulos, deslizador, menu e abas. Dividir mais só espalharia o mesmo painel em várias classes.
- `TelaReproducao` tem 8 atributos, pelo mesmo motivo (rótulos do estado e do botão de play, estados `_tocando` e `_pausado`).
- `TelaPrincipal._ao_modificar_texto(evento)` não usa o `evento`, mas o tkinter sempre passa esse argumento para quem trata o evento.

Para rodar as mesmas medições: `radon cc -a gerador_musical` e `pylint gerador_musical` (os dois se instalam com `pip install radon pylint`).

### 10.3 Refatorações usadas, pelo nome do catálogo

| Refatoração | Onde |
|-------------|------|
| Extrair Classe (*Extract Class*) | `ControladorConfiguracao` (de `ControladorAplicacao`), `PainelConfiguracoes` (de `TelaPrincipal`) |
| Extrair Método (*Extract Method*) | `PainelConfiguracoes._alterar`, `Caixa.em_pixels`, `estilo._contorno_arredondado` |
| Introduzir Objeto-Parâmetro (*Introduce Parameter Object*) | `Caixa` e `EstiloTexto` nos métodos de `Desenho` e no `Deslizador` |
| Mover Método (*Move Method*) | `ParametrosMusica.somar_ao_instrumento` (saiu de `RegraInstrumentoSomaDigito`) |
| Renomear Método (*Rename Method*) | `Player.play()`/`stop()` → `tocar()`/`parar()` |
| Remover código morto | `Voz.ultima_nota`, `Token.eh_caractere`, `Sintetizador.partitura`, import sem uso |

Quando chegar o relatório do grupo revisor, esta seção ajuda a montar o slide pedido no enunciado: para cada observação deles, dá para apontar se já estava resolvida aqui ou o que foi feito depois.
