# G18_Ordenacao_2026.2 - Probabilidades no Campeonato (Monte Carlo & Ordenação)

Sistema de linha de comando (CLI) em Python para estimativa de probabilidades em campeonatos de futebol (título, vaga continental e rebaixamento) utilizando simulação estocástica de Monte Carlo e múltiplos algoritmos de ordenação desenvolvidos manualmente (Insertion Sort, Merge Sort, Quick Sort, Heap Sort e Radix Sort LSD Multicritério).

O objetivo do trabalho é aplicar os algoritmos de ordenação estudados em EDA2 no laço crítico de simulação de milhares de cenários de torneios, analisando suas complexidades assintóticas, estabilidade e desempenho prático conforme a quantidade de equipes e partidas cresce.

## Vídeo de apresentação

Link a ser adicionado.

## Alunos

| Matrícula | Nome |
| --------- | ---- |
| 232001380 | Caio Vilas Boas Miranda |
| 232021516 | Guilherme Gusmão Nepomuceno |

## Descrição

O sistema resolve um problema clássico de torcedores e analistas esportivos: dada a tabela de classificação atual e os confrontos restantes da temporada, estimar as probabilidades de cada time ser campeão, classificar-se para competições continentais ou sofrer rebaixamento.

A base padrão do projeto utiliza dados oficiais do **Campeonato Brasileiro Série A 2023** após a 35ª rodada (20 clubes, 35 partidas disputadas por equipe, totalizando exatamente 867 gols pró e 867 gols contra em equilíbrio matemático estrito, restando 30 jogos correspondentes às rodadas 36, 37 e 38).

Como o saldo de gols e os gols pró atuam como critérios de desempate essenciais no regulamento, o modelo não apenas simula vitória/empate/derrota, mas gera placares reais de gols através da distribuição de Poisson (algoritmo clássico de Donald Knuth). As forças de ataque e defesa de cada clube são calculadas dinamicamente ao carregar a classificação a partir dos dados do campeonato, dividindo a taxa de gols por jogo do time pela média de gols por jogo de toda a liga (colunas manuais de ataque e defesa eventualmente presentes no CSV são desconsideradas em favor do cálculo dinâmico).

A cada iteração da simulação de Monte Carlo:
1. Uma cópia independente da tabela inicial é instanciada para preservar os dados originais.
2. Cada partida restante é simulada via amostragem de Poisson a partir das forças de ataque/defesa e do fator mandante.
3. A pontuação, vitórias, gols marcados e sofridos são atualizados *in-place*.
4. A tabela completa é reordenada pelo algoritmo de ordenação selecionado.
5. As posições finais são contabilizadas nas faixas configuráveis (1º lugar para título, Top $K$ para continental e Últimos $R$ para rebaixamento).

Todos os dados de entrada são carregados e validados a partir de arquivos CSV (`data/classificacao.csv` e `data/jogos_restantes.csv`), com checagem estrita de integridade referencial para impedir jogos com clubes não cadastrados e verificação de conservação do total de gols pró e contra.

## Algoritmos de ordenação

O núcleo de ordenação foi desenvolvido manualmente, contemplando 5 algoritmos clássicos selecionáveis por parâmetro:

- **Insertion Sort**: Algoritmo incremental e estável. Complexidade $\mathcal{O}(n)$ no melhor caso (quase ordenado) e $\mathcal{O}(n^2)$ no médio e pior caso; $\mathcal{O}(1)$ de memória auxiliar. Destaca-se fortemente quando a entrada já está quase ordenada, superando algoritmos mais sofisticados devido à quase ausência de trocas.
- **Merge Sort**: Algoritmo de divisão e conquista e estável. Complexidade $\Theta(n \log n)$ em todos os casos; $\mathcal{O}(n)$ de memória auxiliar para intercalação. Garante preservação rigorosa da ordem original em caso de empate total de critérios.
- **Quick Sort**: Algoritmo baseado em divisão e particionamento (implementado com partição de Hoare e pivô central). Complexidade $\mathcal{O}(n \log n)$ no caso médio/melhor e $\mathcal{O}(n^2)$ no pior caso; $\mathcal{O}(\log n)$ de espaço na pilha de recursão. Instável por natureza, mas determinizado na interface `ordenar_tabela` via desempate determinístico pelo índice de entrada original ($-i$).
- **Heap Sort**: Algoritmo baseado em árvore binária quase completa (*Min-Heap* para ordenação decrescente *in-place*). Complexidade $\mathcal{O}(n \log n)$ em todos os casos; $\mathcal{O}(1)$ de memória auxiliar. Instável por construção, também determinizado em `ordenar_tabela` pelo índice de entrada.
- **Radix Sort LSD Multicritério**: Algoritmo linear não-comparativo com complexidade $\mathcal{O}(k \cdot (n + b))$, onde $k$ é o número de critérios e $b$ a amplitude dos valores. Executa passadas de *Counting Sort* estável do critério menos importante para o mais importante (LSD). Trata saldo de gols negativo via deslocamento (*offset*) e inverte a chave para ordenação decrescente estável. O desempate lexicográfico preliminar por nome tem `desempate_nome=False` como padrão para evitar a sobrecarga de manipulação de strings em grandes volumes de dados.
- **Gabarito e Baseline (`sorted()`)**: O Timsort nativo do Python entra exclusivamente nos testes automatizados como gabarito oficial para validar os 5 algoritmos e no benchmark como linha de base compilada em C.

## Como executar

Requisitos: Python 3.11+.

Instalação das dependências de teste:
```bash
pip install -r requirements.txt
```

### Executar a Simulação Principal (CLI)

Execução padrão (1.000 simulações com dados reais do Brasileirão, Top 6 para Libertadores e Z-4 para rebaixamento):
```bash
python3 src/main.py
```

Opções de personalização via linha de comando:
```bash
# Selecionar o algoritmo de ordenação (insertion, merge, quick, heap, radix)
python3 src/main.py --algoritmo radix

# Ajustar a quantidade de simulações e definir semente determinística
python3 src/main.py --simulacoes 5000 --seed 42

# Personalizar as faixas do regulamento (ex: Top 4 continental, Últimos 3 rebaixados)
python3 src/main.py --top-continental 4 --rebaixamento 3 --algoritmo quick

# Apontar para outro diretório de dados CSV
python3 src/main.py --dados data/
```

Para consultar todas as opções disponíveis:
```bash
python3 src/main.py --help
```

### Executar o Benchmark Integrado

Executa o experimento comparativo de desempenho com cenários de 6, 20, 200 e 2.000 equipes (com repetições e uso da mediana para amortecer ruídos do sistema), incluindo o contraste direto de tabela quase ordenada vs. embaralhada:
```bash
python3 benchmark/benchmark.py
```

Para pular opcionalmente o `insertion_sort` no cenário de 2.000 equipes:
```bash
python3 benchmark/benchmark.py --pular-insertion-2000
```

### Testes Automatizados

A suíte conta com 43 testes automatizados cobrindo equivalência estrita entre os 5 algoritmos em cenários com empates massivos, imutabilidade da tabela inicial, validação de integridade referencial, Poisson de Knuth, Monte Carlo e benchmark:
```bash
pytest -v
```

## Resultados do Benchmark

Os testes de desempenho foram executados no seguinte ambiente:
- **Sistema Operacional:** Linux (x86_64)
- **Ambiente de Execução:** Python 3.14.4 (CPython)
- **Metodologia:** Cada medição foi repetida 3 vezes, registrando-se a **mediana** dos tempos totais e dos tempos isolados de ordenação.

### Tabela de Desempenho no Monte Carlo

| Algoritmo | N Times | Simulações | Tempo Total (s) | ms / Simulação | ms / Ordenação | Simulações/s |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **insertion** | 6 | 500 | 0.0152 | 0.03 | 0.01 | 32823 |
| **merge** | 6 | 500 | 0.0166 | 0.03 | 0.01 | 30137 |
| **quick** | 6 | 500 | 0.0181 | 0.04 | 0.01 | 27598 |
| **heap** | 6 | 500 | 0.0199 | 0.04 | 0.02 | 25114 |
| **radix** | 6 | 500 | 0.0189 | 0.04 | 0.02 | 26490 |
| *sorted_python* | 6 | 500 | 0.0111 | 0.02 | 0.00 | 45169 |
| **insertion** | 20 | 200 | 0.0176 | 0.09 | 0.02 | 11345 |
| **merge** | 20 | 200 | 0.0215 | 0.11 | 0.04 | 9317 |
| **quick** | 20 | 200 | 0.0225 | 0.11 | 0.05 | 8908 |
| **heap** | 20 | 200 | 0.0272 | 0.14 | 0.06 | 7354 |
| **radix** | 20 | 200 | 0.0212 | 0.11 | 0.04 | 9456 |
| *sorted_python* | 20 | 200 | 0.0145 | 0.07 | 0.01 | 13832 |
| **insertion** | 200 | 50 | 0.0443 | 0.89 | 0.23 | 1129 |
| **merge** | 200 | 50 | 0.0690 | 1.38 | 0.63 | 724 |
| **quick** | 200 | 50 | 0.0676 | 1.35 | 0.60 | 739 |
| **heap** | 200 | 50 | 0.0991 | 1.98 | 1.15 | 504 |
| **radix** | 200 | 50 | 0.0523 | 1.05 | 0.37 | 955 |
| *sorted_python* | 200 | 50 | 0.0397 | 0.79 | 0.13 | 1259 |
| **insertion** | 2000 | 10 | 0.3861 | 38.61 | 2.88 | 25 |
| **merge** | 2000 | 10 | 0.4343 | 43.43 | 7.70 | 23 |
| **quick** | 2000 | 10 | 0.3704 | 37.04 | 6.88 | 27 |
| **heap** | 2000 | 10 | 0.4636 | 46.36 | 19.15 | 21 |
| **radix** | 2000 | 10 | 0.3137 | 31.37 | 4.29 | 31 |
| *sorted_python* | 2000 | 10 | 0.3399 | 33.99 | 1.56 | 29 |

### Contraste Empírico: Tabela Já Ordenada vs. Embaralhada ($N = 2.000$, Mediana de 3 Repetições)

Para evidenciar na prática que **"o melhor algoritmo depende do formato da entrada"**, mediu-se o tempo puro de ordenação (`ordenar_tabela`) em dois cenários extremos com 2.000 times (mediana de 3 execuções):

| Algoritmo | Já Ordenada (ms) | Embaralhada (`random.shuffle`) (ms) | Impacto / Degradação |
| :--- | :---: | :---: | :---: |
| **insertion** | **2.88** | **206.96** | **71.8× mais lento** |
| **merge** | 6.65 | 9.96 | 1.5× (estável $\Theta(n \log n)$) |
| **quick** | 6.86 | 8.00 | 1.2× ($\mathcal{O}(n \log n)$ médio) |
| **heap** | 15.83 | 15.85 | 1.0× ($\mathcal{O}(n \log n)$) |
| **radix** | 3.89 | 3.72 | 1.0× ($\mathcal{O}(k \cdot n)$ linear) |

> **Discussão dos Resultados:**
> 1. **Campeonato Real ($N = 20$):** O tempo total por simulação completa é de $\approx 0.10$ a $0.14$ ms (média de $\approx 0.11$ ms). A ordenação isolada consome cerca de $40\%$ desse tempo ($0.03$ a $0.06$ ms). A diferença entre o algoritmo mais rápido e o mais lento é de até $\approx 0.04$ ms por simulação, o que é imperceptível para o usuário final.
> 2. **Ligas Médias ($N = 200$):** O Insertion Sort beneficia-se fortemente do arranjo inicial próximo do ordenado, exigindo pouquíssimas trocas locais ($0.24$ ms / ordenação). Merge ($0.56$ ms) e Quick ($0.59$ ms) mantêm comportamento assintótico muito próximo.
> 3. **Grandes Cenários ($N = 2.000$) e ms / Ordenação:** Ao analisar isoladamente o tempo de ordenação (evitando o ruído da geração estocástica de gols no tempo total), nota-se que:
>    - **Na entrada quase ordenada do campeonato:** O Insertion Sort foi o mais rápido entre os de comparação ($2.74$ ms por ordenação), superando Merge ($7.67$ ms), Quick ($6.82$ ms) e Heap ($19.26$ ms). Isso ocorre porque uma tabela que já reflete 35 rodadas anteriores sofre poucas inversões com os jogos de 3 rodadas restantes ($\mathcal{O}(n + d)$, com poucas inversões $d$).
>    - **Na entrada totalmente embaralhada:** O Insertion Sort degrada para seu pior caso $\mathcal{O}(n^2)$ ($206.96$ ms, $71.8\times$ mais lento), enquanto Merge, Quick e Heap mantêm seus tempos em torno de $8$ a $16$ ms e o Radix em $\approx 3.7$ ms.
>    - **Radix vs Merge Sort e Crescimento:** O Radix LSD apresentou vantagem prática de aproximadamente $1.8\times$ frente ao Merge Sort em $N=2.000$ ($4.19$ ms vs $7.67$ ms). De $N=200$ para $N=2.000$, o crescimento medido foi de $\approx 13.7\times$ no Merge e $\approx 11.4\times$ no Radix, indicando um escalonamento proporcional e que nesta faixa de valores de $N$ o ganho reflete um fator constante vantajoso da implementação e contagem por dígitos em vez de uma separação estritamente assintótica.
> 4. **Implementação em C vs Python Puro:** A linha de base `sorted_python` (Timsort em C) executa instruções nativas de máquina sem a sobrecarga do laço de interpretação do CPython, servindo como teto ótimo de desempenho.

## Limitações do Modelo

Embora o simulador forneça estimativas probabilísticas sólidas e matematicamente consistentes, certas hipóteses simplificadoras devem ser consideradas ao analisar os resultados:

1. **Forças Estáticas ao Longo do Tempo:** O modelo assume que o potencial ofensivo e defensivo das equipes permanece constante até o fim do torneio, desconsiderando variações táticas, evolução física, desfalques por lesão, suspensões por cartão ou trocas de treinador.
2. **Independência Estocástica dos Gols (Poisson Simples):** Os gols marcados por cada equipe são amostrados de variáveis aleatórias de Poisson independentes. No futebol real, placares de mandante e visitante guardam correlação mútua, especialmente em empates de baixa contagem (como 0x0 e 1x1, que ocorrem com frequência ligeiramente superior ao modelo independente de Poisson).
3. **Parâmetros de Simulação Escolhidos:** O fator mandante multiplicativo ($1.15$) e a taxa base de gols por partida ($1.30$) são valores heurísticos simples adotados pelos autores para balancear os placares médios, não constituindo modelos calibrados por regressão bivariada formal.

## Estrutura do projeto

```
data/
  classificacao.csv      Tabela real do Brasileirão 2023 (20 clubes, pontos, jogos, gols)
  jogos_restantes.csv    Confrontos pendentes reais das rodadas finais (30 partidas)
src/
  main.py                Interface de linha de comando (CLI) com saída formatada
  modelos.py             Classes de domínio (Time, Jogo), cálculo de forças e validação
  ordenacao.py           Implementações manuais dos 5 algoritmos de ordenação
  simulacao.py           Gerador Poisson de Knuth e simulador estocástico de confrontos
  montecarlo.py          Motor de Monte Carlo, medição isolada e agregação de probabilidades
benchmark/
  benchmark.py           Esteira de medição empírica, cálculo de medianas e análise
tests/
  conftest.py            Fixtures compartilhadas e restauração automática de critérios
  test_ordenacao.py      Testes de estabilidade, empates massivos e corretude dos 5 métodos
  test_simulacao.py      Testes do algoritmo de Knuth, Lei dos Grandes Números e balanços
  test_modelos.py        Testes de leitura CSV, validação de integridade e forças dinâmicas
  test_montecarlo.py     Testes de conservação das probabilidades, faixas e imutabilidade
  test_benchmark.py      Testes de geração sintética e esteira de benchmark
requirements.txt         Dependências do projeto (pytest)
```
