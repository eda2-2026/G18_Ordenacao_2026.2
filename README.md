# G18_Ordenacao_2026.2 - Probabilidades no Campeonato (Monte Carlo & Ordenação)

Sistema de linha de comando (CLI) em Python para estimativa de probabilidades em campeonatos de futebol (título, vaga continental e rebaixamento) utilizando simulação estocástica de Monte Carlo e múltiplos algoritmos de ordenação desenvolvidos manualmente (Insertion Sort, Merge Sort, Quick Sort, Heap Sort e Radix Sort LSD Multicritério).

O objetivo do trabalho é aplicar os algoritmos de ordenação estudados em EDA2 no laço crítico de simulação de milhares de cenários de torneios, analisando suas complexidades assintóticas, estabilidade e desempenho prático conforme a quantidade de equipes e partidas cresce.

## Entrega parcial — aproximadamente 100%

O percentual é uma estimativa de escopo, dividida em cinco etapas.

| Etapa | Estado |
| ----- | ------ |
| 1. Domínio de dados, critérios de desempate e leitura CSV | Concluída |
| 2. Núcleo com 5 algoritmos de ordenação próprios e gabarito `sorted()` | Concluída |
| 3. Simulação estatística de partidas com modelo Poisson (Donald Knuth) | Concluída |
| 4. Simulação de Monte Carlo com faixas configuráveis e CLI formatada | Concluída |
| 5. Benchmark integrado com análise teórica e suíte de testes (39 testes) | Concluída |

## Vídeo de apresentação

Link a ser adicionado.

## Alunos

| Matrícula | Nome |
| --------- | ---- |
| 232001380 | Caio Vilas Boas Miranda | 
| 232021516 | Guilherme Gusmão |

## Descrição

O sistema resolve um problema clássico de torcedores e analistas estatísticos: dada a tabela atual de classificação e os jogos restantes da temporada, estimar as probabilidades de cada time ser campeão, classificar-se para competições continentais ou ser rebaixado.

Como o saldo de gols e os gols pró entram como critérios de desempate fundamentais, o modelo não apenas simula vitória/empate/derrota, mas gera placares reais de partidas com base nas forças de ataque e defesa de cada clube através da distribuição de Poisson.

A cada iteração da simulação de Monte Carlo:
1. Uma cópia independente da tabela inicial é instanciada para preservar os dados originais.
2. Cada jogo pendente é simulado via amostragem de Poisson (algoritmo de Donald Knuth).
3. A pontuação, vitórias, gols marcados e sofridos são atualizados *in-place*.
4. A tabela completa é reordenada pelo algoritmo de ordenação selecionado.
5. As posições finais são contabilizadas nas faixas configuráveis (1º lugar para título, Top $K$ para continental e Últimos $R$ para rebaixamento).

Os dados de entrada são carregados e validados a partir de arquivos CSV (`classificacao.csv` e `jogos_restantes.csv`).

## Algoritmos de ordenação

O núcleo de ordenação foi desenvolvido manualmente, contemplando 5 algoritmos clássicos selecionáveis por parâmetro:

- **Insertion Sort**: Algoritmo incremental e estável. Complexidade $\mathcal{O}(n)$ no melhor caso (quase ordenado) e $\mathcal{O}(n^2)$ no médio e pior caso; $\mathcal{O}(1)$ de memória auxiliar. Extremamente eficiente para tabelas pequenas ($N \le 20$), mas proibitivo para grandes massas de dados.
- **Merge Sort**: Algoritmo de divisão e conquista e estável. Complexidade $\Theta(n \log n)$ em todos os casos; $\mathcal{O}(n)$ de memória auxiliar para intercalação. Garante preservação rigorosa da ordem original em caso de empate total de critérios.
- **Quick Sort**: Algoritmo baseado em divisão e particionamento (implementado com partição de Hoare e pivô central). Complexidade $\mathcal{O}(n \log n)$ no caso médio/melhor e $\mathcal{O}(n^2)$ no pior caso; $\mathcal{O}(\log n)$ de espaço na pilha de recursão. Instável.
- **Heap Sort**: Algoritmo baseado em árvore binária quase completa (*Min-Heap* para ordenação decrescente *in-place*). Complexidade $\mathcal{O}(n \log n)$ em todos os casos; $\mathcal{O}(1)$ de memória auxiliar. Instável.
- **Radix Sort LSD Multicritério**: Algoritmo linear não-comparativo com complexidade $\mathcal{O}(k \cdot (n + b))$, onde $k$ é o número de critérios e $b$ a amplitude dos valores. Executa passadas de *Counting Sort* estável do critério menos importante para o mais importante (LSD). Trata saldo de gols negativo via deslocamento (*offset*) e inverte a chave para ordenação decrescente estável. Suporta desempate preliminar lexicográfico (A-Z).
- **Gabarito e Baseline (`sorted()`)**: O Timsort nativo do Python entra exclusivamente nos testes automatizados como gabarito para verificar a corretude dos 5 algoritmos e no benchmark como linha de base em C.

## Como executar

Requisitos: Python 3.11+.

Instalação das dependências de teste:
```bash
pip install -r requirements.txt
```

### Executar a Simulação Principal (CLI)

Execução padrão (1.000 simulações com Merge Sort):
```bash
python3 src/main.py
```

Opções de personalização via linha de comando:
```bash
# Selecionar o algoritmo de ordenação (insertion, merge, quick, heap, radix)
python3 src/main.py --algoritmo radix

# Ajustar a quantidade de simulações e definir semente determinística
python3 src/main.py --simulacoes 5000 --seed 42

# Personalizar as faixas do regulamento (Top 3 continental, Último 1 rebaixado)
python3 src/main.py --top-continental 3 --rebaixamento 1 --algoritmo quick

# Apontar para outro diretório de dados CSV
python3 src/main.py --dados data/
```

Para consultar todas as opções disponíveis:
```bash
python3 src/main.py --help
```

### Executar o Benchmark Integrado

Executa o experimento comparativo de desempenho com cenários de 6, 20, 200 e 2.000 equipes, gerando tabela com tempo total, tempo por simulação e taxa de simulações/s, acompanhada da discussão teórica:
```bash
python3 benchmark/benchmark.py
```

Para incluir o `insertion_sort` mesmo no cenário de 2.000 equipes (pode demorar devido a $\mathcal{O}(n^2)$):
```bash
python3 benchmark/benchmark.py --todos-inclusive-grandes-insertion
```

### Testes Automatizados

A suíte conta com 39 testes cobrindo ordenação, simulação estocástica, modelo de Poisson, Monte Carlo, leitura CSV e benchmark:

```bash
pytest -v
```

## Estrutura do projeto

```
data/
  classificacao.csv      Base com times, pontuação atual, gols e forças de ataque/defesa
  jogos_restantes.csv    Confrontos pendentes da temporada
src/
  main.py                Interface de linha de comando (CLI) com formatação tabular
  modelos.py             Classes de domínio (Time, Jogo) e leitura de arquivos CSV
  ordenacao.py           Núcleo com os 5 algoritmos de ordenação implementados
  simulacao.py           Gerador Poisson de Knuth e simulador de placares de jogos
  montecarlo.py          Motor de simulação de Monte Carlo e agregação de probabilidades
benchmark/
  benchmark.py           Experimento de desempenho, tabela comparativa e análise teórica
tests/
  conftest.py            Fixtures compartilhadas e restauração automática de critérios
  test_ordenacao.py      Testes de estabilidade, empates, casos limites e massa aleatória
  test_simulacao.py      Testes de Poisson, convergência média e conservação de saldo/pontos
  test_modelos.py        Testes de dataclasses, critérios de desempate e leitura CSV
  test_montecarlo.py     Testes de probabilidades, faixas configuráveis e CLI
  test_benchmark.py      Testes de geração de cenários sintéticos e esteira de benchmark
requirements.txt         Dependências do projeto (pytest)
```
