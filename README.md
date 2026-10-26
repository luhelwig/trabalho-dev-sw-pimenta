# Gerador de Música a partir de Texto

Trabalho prático de Desenvolvimento de Software (INF01120 – UFRGS), fase 2.

**Grupo:** Luiza Helwig da Silva, Marco Aurélio Lenhart e Maria Clara Escobar

A ideia é simples: você escreve um texto e o programa lê caractere por caractere, transformando cada um em nota, pausa ou alguma mudança no som (volume, oitava, instrumento, andamento). Cada linha do texto vira uma voz, e as vozes tocam ao mesmo tempo. No fim dá pra ouvir a música e salvar como arquivo MIDI.

## Como rodar

Precisa de Python 3.10 ou mais novo.

```
python -m venv .venv
.venv\Scripts\activate          # no Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Para rodar os testes: `pytest`

No Windows o som sai direto pelo sintetizador MIDI do próprio sistema. No Linux é preciso instalar também o tkinter (a biblioteca das janelas) e um banco de sons para o MIDI. No Ubuntu:

    sudo apt install python3-tk fluid-soundfont-gm

Sem o banco de sons a música não toca, mas o arquivo .mid é gerado normalmente.

Se você já tinha instalado o projeto antes, com o `pygame`, troque pelo `pygame-ce` antes de tudo:

    pip uninstall -y pygame pygame-ce
    pip install -r requirements.txt
## Como usar

1. Escreva o texto no campo "texto de entrada", ou clique no botão redondo no canto de cima para abrir um arquivo .txt.
2. Se quiser, ajuste as configurações. O bpm vale para a música inteira. Volume, instrumento e oitava valem para a voz selecionada: clique em v0, v1, v2 ou v3 para escolher a voz e mudar os valores dela.
3. Clique em "gerar música". Se o campo estiver vazio ou tiver caracteres que o programa não aceita, aparece um aviso.
4. Na tela de reprodução:
   - o botão de play toca, pausa e retoma;
   - "parar" volta a música para o começo;
   - "baixar midi" salva o arquivo na pasta Downloads (nome `musica_AAAAMMDD_HHMMSS.mid`, então nunca sobrescreve outro);
   - "salvar como..." deixa você escolher a pasta e o nome;
   - "voltar" leva de volta para o texto. Dá pra mudar as configurações e gerar de novo sem redigitar nada.

Na tela principal ainda tem "salvar texto", que grava o conteúdo do campo em .txt (se o texto veio de um arquivo, salva por cima dele), e "limpar", que apaga o campo.

## Como o texto vira música

Cada linha é uma voz. Os valores iniciais de cada uma são:

| Linha | Voz | Instrumento     | Oitava | Volume |
|-------|-----|-----------------|--------|--------|
| 1ª    | v0  | cravo           | 6      | 100    |
| 2ª    | v1  | órgão de igreja | 5      | 80     |
| 3ª    | v2  | piano           | 4      | 60     |
| 4ª    | v3  | fagote          | 3      | 40     |

Da 5ª linha em diante os valores se repetem (a 5ª começa igual à 1ª, e assim por diante). Uma linha em branco vira uma voz em silêncio.

Dentro de cada linha:

| No texto | O que acontece |
|----------|----------------|
| `A` a `G` (maiúsculas) | toca a nota: lá, si, dó, ré, mi, fá, sol |
| `#` ou `b` logo depois da nota | sustenido ou bemol (`C#`, `Bb`) |
| `:n` depois da nota, com n de 1 a 7 | duração: 1 semibreve, 2 mínima, 3 semínima, 4 colcheia, 5 semicolcheia, 6 fusa, 7 semifusa. Sem `:n`, a nota é uma semínima |
| `[n]` no começo da linha | a voz espera n beats antes de começar |
| `a` a `h` (minúsculas) | pausa |
| espaço | dobra o volume da voz (até no máximo 127) |
| `?` | sobe uma oitava |
| `V` | desce uma oitava |
| `>` e `<` | aumenta ou diminui 10 bpm, para todas as vozes, a partir daquele ponto |
| `!` | troca para bandoneon |
| `;` ou dígito ímpar | troca para sinos tubulares |
| `,` | troca para agogô |
| dígito par | soma o dígito ao número do instrumento atual |
| qualquer outro caractere (`H`, `O`, `I`, `U`, outras letras, símbolos) | se o anterior foi uma nota, repete essa nota; senão, faz uma pausa |

Um exemplo para testar, com o começo da Ode à Alegria em quatro vozes:

```
E:3E:3F:3G:3G:3F:3E:3D:3C:3C:3D:3E:3E:3D:3D:2
E:1D:1E:1D:1
G:1B:1G:1B:1
C:1G:1C:1G:1
```

## Decisões que tomamos

O enunciado deixa alguns pontos em aberto. O que decidimos:

- Uma semínima vale 1 beat, então a semibreve vale 4. O atraso `[n]` também é contado em beats.
- O bpm começa em 120 e fica sempre entre 20 e 300.
- A oitava fica entre 0 e 8. Se um `?` ou `V` passar desse limite, a voz volta para a oitava inicial dela.
- Se a soma do dígito passar do último instrumento MIDI (127), a contagem recomeça do 0.
- Como o espaço dobra o volume, um texto com muitos espaços chega rápido no volume máximo. Para controlar o volume, é melhor escrever as notas sem espaço.
- Se depois de `:` vier algo que não é de 1 a 7 (por exemplo `A:9`), a nota fica com a duração padrão e o `:` e o `9` são lidos como caracteres normais.
- O programa aceita os caracteres imprimíveis do teclado e as letras acentuadas do português. Qualquer outro caractere dá "formato incorreto".

## Organização do código

```
main.py                     monta todas as peças e abre a janela
gerador_musical/
  entrada/                  texto digitado e arquivos .txt
  interpretacao/            lê o texto: tokenizador, parser e as regras do mapeamento
  musica/                   notas, durações, vozes, partitura, instrumentos
  saida/                    gera o MIDI, toca e exporta
  aplicacao/                controlador (a interface só conversa com ele)
  interface/                telas em tkinter, com o visual do croqui do Figma
tests/                      testes automáticos (pytest)
docs/figma-fase2/           telas do croqui da fase 2
```

Cada linha da tabela de mapeamento é uma classe de regra. Para criar um comando novo, basta escrever uma regra e adicioná-la em `Mapeamento.padrao()`, sem mexer no resto do código.

## Créditos

- [mido](https://github.com/mido/mido) para montar o arquivo MIDI e 
- [pygame-ce](https://pyga.me) para tocar.