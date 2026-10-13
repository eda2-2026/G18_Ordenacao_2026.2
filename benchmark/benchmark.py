from __future__ import annotations

import argparse
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
import sys

# Garante importações a partir da raiz do projeto
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.modelos import Time, Jogo
from src.montecarlo import executar_monte_carlo

# Tabela de algoritmos avaliados, incluindo sorted() nativo em C como linha de base
ALGORITMOS_BENCHMARK = {
    "insertion": "insertion",
    "merge": "merge",
    "quick": "quick",
    "heap": "heap",
    "radix": "radix",
    "sorted_python": lambda times: sorted(times, key=lambda t: t.chave(), reverse=True),
}


def gerar_cenario_sintetico(n_times: int, seed: int = 42) -> tuple[list[Time], list[Jogo]]:
    """Gera um campeonato fictício com n_times e rodadas restantes proporcionais."""
    rng = random.Random(seed)
    times: list[Time] = []

    for i in range(n_times):
        pts = rng.randint(5, max(10, n_times * 2))
        vit = rng.randint(1, max(2, pts // 3))
        gp = rng.randint(10, 50)
        gc = rng.randint(10, 50)
        ataque = round(rng.uniform(0.7, 1.8), 2)
        defesa = round(rng.uniform(0.7, 1.8), 2)

        times.append(
            Time(
                nome=f"Time_{i:04d}",
                pontos=pts,
                vitorias=vit,
                gols_pro=gp,
                gols_contra=gc,
                ataque=ataque,
                defesa=defesa,
            )
        )

    # Gera jogos restantes: cada time joga 2 partidas restantes
    jogos: list[Jogo] = []
    indices = list(range(n_times))
    # Cria pares aleatórios
    for _ in range(2):
        rng.shuffle(indices)
        for i in range(0, n_times - 1, 2):
            m = times[indices[i]].nome
            v = times[indices[i + 1]].nome
            jogos.append(Jogo(mandante=m, visitante=v))

    return times, jogos


@dataclass
class RegistroBenchmark:
    algoritmo: str
    n_times: int
    n_simulacoes: int
    tempo_total: float
    simulacoes_por_segundo: float
    ms_por_simulacao: float
    tempo_ordenacao_total: float = 0.0
    ms_por_ordenacao: float = 0.0


def rodar_benchmark_monte_carlo(
    n_times_lista: list[int] = [6, 20, 200, 2000],
    simulacoes_grid: dict[int, int] | None = None,
    ignorar_insertion_grande: bool = False,
    repeticoes: int = 3,
) -> list[RegistroBenchmark]:
    """Executa o benchmark integrado de Monte Carlo, repetindo medições e usando a mediana."""
    if simulacoes_grid is None:
        simulacoes_grid = {
            6: 500,
            20: 200,
            200: 50,
            2000: 10,
        }

    registros: list[RegistroBenchmark] = []

    print("\n" + "=" * 90)
    print(f" INICIANDO BENCHMARK INTEGRADO DE ORDENAÇÃO NO MONTE CARLO (Mediana de {repeticoes} repetições)")
    print("=" * 90)

    for n in n_times_lista:
        n_sim = simulacoes_grid.get(n, 50)
        times, jogos = gerar_cenario_sintetico(n, seed=42)

        # Ordena a tabela inicial pela chave, simulando a classificação real de um torneio
        times = sorted(times, key=lambda t: t.chave(), reverse=True)

        print(f"\n>>> Cenário: {n} Times | {len(jogos)} Jogos | {n_sim} Simulações")

        for nome_alg in ALGORITMOS_BENCHMARK:
            if n >= 2000 and nome_alg == "insertion" and ignorar_insertion_grande:
                print(f"  - {nome_alg:<14}: [SKIPPED - ignorado por parâmetro]")
                continue

            tempos_totais: list[float] = []
            tempos_ord: list[float] = []

            for rep in range(repeticoes):
                resultado = executar_monte_carlo(
                    tabela_inicial=times,
                    jogos_restantes=jogos,
                    num_simulacoes=n_sim,
                    algoritmo=ALGORITMOS_BENCHMARK[nome_alg],
                    seed=42 + rep,
                )
                tempos_totais.append(resultado.tempo_execucao)
                tempos_ord.append(resultado.tempo_ordenacao)

            duracao_total = statistics.median(tempos_totais)
            duracao_ord = statistics.median(tempos_ord)
            sim_sec = n_sim / max(1e-6, duracao_total)
            ms_sim = (duracao_total / n_sim) * 1000.0
            ms_ord = (duracao_ord / n_sim) * 1000.0

            registros.append(
                RegistroBenchmark(
                    algoritmo=nome_alg,
                    n_times=n,
                    n_simulacoes=n_sim,
                    tempo_total=duracao_total,
                    simulacoes_por_segundo=sim_sec,
                    ms_por_simulacao=ms_sim,
                    tempo_ordenacao_total=duracao_ord,
                    ms_por_ordenacao=ms_ord,
                )
            )

            print(
                f"  - {nome_alg:<14}: {duracao_total:8.4f}s total | "
                f"{ms_sim:6.2f} ms/simulação ({ms_ord:6.2f} ms ordenação) | "
                f"{sim_sec:8.1f} sim/s"
            )

    return registros


def comparar_ja_ordenada_vs_embaralhada(n: int = 2000, seed: int = 42, repeticoes: int = 3) -> None:
    """Demonstra o impacto da entrada já ordenada versus aleatória na ordenação direta (mediana de repetições)."""
    from src.ordenacao import ordenar_tabela

    times, _ = gerar_cenario_sintetico(n, seed=seed)
    times_ordenada = sorted(times, key=lambda t: t.chave(), reverse=True)
    times_shuffled = list(times)
    random.Random(123).shuffle(times_shuffled)

    print("\n" + "=" * 90)
    print(f" CONTRASTE DE ENTRADA: TABELA JÁ ORDENADA VS. EMBARALHADA (N = {n}, Mediana de {repeticoes} repetições)")
    print(" Demonstração empírica: 'O melhor algoritmo depende do formato da entrada'")
    print("=" * 90)

    print(f"{'Algoritmo':<15} | {'Já Ordenada (ms)':>20} | {'Embaralhada (ms)':>18} | {'Impacto / Razão':>18}")
    print(f"{'-' * 16}|{'-' * 22}|{'-' * 20}|{'-' * 20}")

    for alg in ["insertion", "merge", "quick", "heap", "radix"]:
        tempos_ord = []
        tempos_shuf = []
        for _ in range(repeticoes):
            t0 = time.perf_counter()
            ordenar_tabela(list(times_ordenada), algoritmo=alg)
            tempos_ord.append((time.perf_counter() - t0) * 1000.0)

            t0 = time.perf_counter()
            ordenar_tabela(list(times_shuffled), algoritmo=alg)
            tempos_shuf.append((time.perf_counter() - t0) * 1000.0)

        med_ord = statistics.median(tempos_ord)
        med_shuf = statistics.median(tempos_shuf)
        razao = med_shuf / max(1e-3, med_ord)
        print(f"{alg:<15} | {med_ord:20.2f} | {med_shuf:18.2f} | {razao:16.1f}x")
    print("=" * 90 + "\n")


# Alias para retrocompatibilidade
comparar_quase_ordenada_vs_embaralhada = comparar_ja_ordenada_vs_embaralhada


def imprimir_tabela_resumo(registros: list[RegistroBenchmark]) -> None:
    """Imprime uma tabela consolidada formatada em Markdown."""
    print("\n" + "=" * 115)
    print(" TABELA COMPARATIVA DE DESEMPENHO (TEMPO TOTAL E ISOLADO DE ORDENAÇÃO)")
    print("=" * 115)

    cabecalho = (
        f"| {'Algoritmo':<15} | {'N Times':>7} | {'Simulações':>10} | "
        f"{'Tempo Total (s)':>15} | {'ms / Simulação':>15} | {'ms / Ordenação':>15} | {'Simulações/s':>14} |"
    )
    separador = (
        f"|{'-' * 17}|{'-' * 9}|{'-' * 12}|{'-' * 17}|{'-' * 17}|{'-' * 17}|{'-' * 16}|"
    )

    print(cabecalho)
    print(separador)

    for r in registros:
        print(
            f"| {r.algoritmo:<15} | {r.n_times:7d} | {r.n_simulacoes:10d} | "
            f"{r.tempo_total:15.4f} | {r.ms_por_simulacao:15.2f} | {r.ms_por_ordenacao:15.2f} | {r.simulacoes_por_segundo:14.1f} |"
        )
    print(separador + "\n")


def imprimir_analise_teorica(registros: list[RegistroBenchmark]) -> None:
    """Imprime a análise baseada estritamente nos números medidos durante a execução."""
    print("=" * 95)
    print(" ANÁLISE DOS RESULTADOS E DISCUSSÃO BASEADA NOS DADOS MEDIDOS")
    print("=" * 95)

    regs_n20 = [r for r in registros if r.n_times == 20]
    regs_n200 = [r for r in registros if r.n_times == 200]
    regs_n2000 = [r for r in registros if r.n_times == 2000]

    print("\n1. Campeonato Real (N = 20):")
    if regs_n20:
        ord_ms = {r.algoritmo: r.ms_por_ordenacao for r in regs_n20 if r.algoritmo != "sorted_python"}
        sim_ms = {r.algoritmo: r.ms_por_simulacao for r in regs_n20 if r.algoritmo != "sorted_python"}
        min_ord, max_ord = min(ord_ms.values()), max(ord_ms.values())
        min_sim, max_sim = min(sim_ms.values()), max(sim_ms.values())
        pct_ord = (sum(ord_ms.values()) / max(1e-6, sum(sim_ms.values()))) * 100.0
        delta_sim = max_sim - min_sim

        print(
            f"   - Ordenação isolada: {min_ord:.2f} a {max_ord:.2f} ms por simulação (~{pct_ord:.0f}% do tempo total)."
        )
        print(
            f"   - Tempo total da simulação: {min_sim:.2f} a {max_sim:.2f} ms por iteração (~{statistics.mean(sim_ms.values()):.2f} ms em média)."
        )
        print(
            f"   - Conclusão prática: Para um campeonato real de 20 clubes, a diferença entre o algoritmo mais "
            f"rápido e o mais lento é de até ~{delta_sim:.2f} ms por simulação, o que é imperceptível para o usuário final."
        )

    print("\n2. Campeonatos Maiores (N = 200):")
    if regs_n200:
        ord_ms = {r.algoritmo: r.ms_por_ordenacao for r in regs_n200}
        print("   - Tempo isolado de ordenação medido:")
        for alg, t_ms in ord_ms.items():
            print(f"     * {alg:<14}: {t_ms:.2f} ms / ordenação")
        print(
            "   - Graças à chave pré-computada e poucas inversões na tabela vinda de rodadas anteriores, "
            "o Insertion Sort é bastante competitivo neste cenário."
        )

    print("\n3. Grandes Cenários (N = 2000):")
    if regs_n2000:
        ord_ms = {r.algoritmo: r.ms_por_ordenacao for r in regs_n2000}
        print("   - Comparando exclusivamente 'ms / Ordenação' (o tempo total inclui simulações com ruído):")
        for alg, t_ms in ord_ms.items():
            print(f"     * {alg:<14}: {t_ms:.2f} ms / ordenação")

        if "insertion" in ord_ms:
            t_ins = ord_ms["insertion"]
            outros_comp = [alg for alg in ["merge", "quick", "heap"] if alg in ord_ms and ord_ms[alg] > t_ins]
            if outros_comp:
                nomes_comp = ", ".join(outros_comp[:-1]) + f" e {outros_comp[-1]}" if len(outros_comp) > 1 else outros_comp[0]
                print(
                    f"   - Destaque: Quando a tabela de entrada está quase ordenada, o Insertion Sort executa "
                    f"em apenas {t_ins:.2f} ms (menos trocas locais), superando {nomes_comp}."
                )
            else:
                print(
                    f"   - Insertion Sort mediu {t_ins:.2f} ms na tabela quase ordenada."
                )

        if "radix" in ord_ms and "merge" in ord_ms:
            razao_radix_merge = ord_ms['merge'] / max(1e-3, ord_ms['radix'])
            print(
                f"   - O Radix LSD foi cerca de {razao_radix_merge:.1f}x mais rápido que o Merge Sort nesta faixa."
            )

        # Calcula a taxa de crescimento real entre N=200 e N=2000 a partir dos dados medidos
        if regs_n200:
            ord_ms_200 = {r.algoritmo: r.ms_por_ordenacao for r in regs_n200}
            crescimentos = []
            for alg in ["merge", "radix", "quick"]:
                if alg in ord_ms and alg in ord_ms_200 and ord_ms_200[alg] > 0:
                    fator = ord_ms[alg] / ord_ms_200[alg]
                    crescimentos.append(f"{alg} (~{fator:.1f}x)")
            if crescimentos:
                str_cresc = ", ".join(crescimentos)
                print(
                    f"   - Crescimento medido de N=200 para N=2000: {str_cresc}, refletindo "
                    f"um escalonamento proporcional e um ganho prático por fator constante nesta faixa de N."
                )

    print("\n4. Baseline Nativa em C vs Python Puro:")
    regs_c = [r for r in registros if r.algoritmo == "sorted_python"]
    if regs_c:
        print(
            "   - A baseline 'sorted_python' (Timsort implementado em C) mostra a eficiência de instruções compiladas "
            "frente ao interpretador de bytecode do Python."
        )
    print("=" * 95 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark dos algoritmos de ordenação no Monte Carlo."
    )
    parser.add_argument(
        "--pular-insertion-2000",
        action="store_true",
        help="Pula o Insertion Sort no cenário N=2000.",
    )
    parser.add_argument(
        "--repeticoes",
        type=int,
        default=3,
        help="Número de repetições por medição para cálculo da mediana (padrão: 3).",
    )
    args = parser.parse_args()

    registros = rodar_benchmark_monte_carlo(
        n_times_lista=[6, 20, 200, 2000],
        ignorar_insertion_grande=args.pular_insertion_2000,
        repeticoes=args.repeticoes,
    )
    imprimir_tabela_resumo(registros)
    comparar_ja_ordenada_vs_embaralhada(n=2000, seed=42, repeticoes=args.repeticoes)
    imprimir_analise_teorica(registros)


if __name__ == "__main__":
    main()