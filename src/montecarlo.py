from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, Sequence
from src.modelos import Time, Jogo, validar_jogos
from src.ordenacao import ordenar_tabela
from src.simulacao import simular_jogo


@dataclass
class EstatisticasTime:
    """Estatísticas e probabilidades estimadas para um time."""

    nome: str
    pontos_iniciais: int
    prob_titulo: float
    prob_continental: float
    prob_rebaixamento: float
    posicao_media: float
    distribuicao_posicoes: dict[int, int]


@dataclass
class ResultadoMonteCarlo:
    """Resultado consolidado da execução do Monte Carlo."""

    estatisticas: list[EstatisticasTime]
    num_simulacoes: int
    algoritmo: str
    tempo_execucao: float
    top_continental: int
    rebaixamento_n: int
    tempo_ordenacao: float = 0.0


def executar_monte_carlo(
    tabela_inicial: Sequence[Time],
    jogos_restantes: Sequence[Jogo],
    num_simulacoes: int = 1000,
    algoritmo: str | Callable[[list[Time]], list[Time]] = "merge",
    top_continental: int = 2,
    rebaixamento_n: int = 2,
    seed: int | None = 42,
    fator_casa: float = 1.15,
    base_gols: float = 1.30,
) -> ResultadoMonteCarlo:
    """Executa a simulação de Monte Carlo por N iterações.

    Em cada iteração:
    1. Clona a tabela inicial para não mutar os dados originais.
    2. Simula todos os jogos restantes gerando placares de Poisson.
    3. Ordena a tabela final pelo algoritmo escolhido (o laço crítico).
    4. Computa a posição de chegada de cada time e acumula as contagens.
    """
    if num_simulacoes <= 0:
        raise ValueError("O número de simulações deve ser maior que zero.")

    nome_alg = getattr(algoritmo, "__name__", "custom") if callable(algoritmo) else str(algoritmo)
    ordenar = algoritmo if callable(algoritmo) else (lambda ts: ordenar_tabela(ts, algoritmo=algoritmo))

    n_times = len(tabela_inicial)
    if n_times == 0:
        return ResultadoMonteCarlo(
            estatisticas=[],
            num_simulacoes=num_simulacoes,
            algoritmo=nome_alg,
            tempo_execucao=0.0,
            top_continental=top_continental,
            rebaixamento_n=rebaixamento_n,
            tempo_ordenacao=0.0,
        )

    if jogos_restantes:
        validar_jogos(tabela_inicial, jogos_restantes)

    # Ajusta faixas se excederem o número de times
    top_k = min(top_continental, n_times)
    reb_r = min(rebaixamento_n, n_times)
    primeiro_rebaixado_pos = n_times - reb_r + 1  # 1-indexed

    rng = random.Random(seed) if seed is not None else random.Random()
    t_inicio = time.perf_counter()

    # Estrutura para armazenar contagens de posições: {nome: {posicao_1_a_N: contagem}}
    contagens: dict[str, dict[int, int]] = {
        t.nome: {pos: 0 for pos in range(1, n_times + 1)}
        for t in tabela_inicial
    }
    pontos_iniciais = {t.nome: t.pontos for t in tabela_inicial}

    tempo_sort = 0.0

    # LAÇO CRÍTICO DE MONTE CARLO
    for _ in range(num_simulacoes):
        # 1. Clona os clubes rapidamente
        clones = {t.nome: t.copiar() for t in tabela_inicial}

        # 2. Simula os confrontos pendentes
        for jogo in jogos_restantes:
            mandante = clones[jogo.mandante]
            visitante = clones[jogo.visitante]
            simular_jogo(
                mandante,
                visitante,
                fator_casa=fator_casa,
                base_gols=base_gols,
                rng=rng,
            )

        # 3. Ordenação da tabela (gargalo computacional medido isoladamente)
        t0 = time.perf_counter()
        tabela_ordenada = ordenar(list(clones.values()))
        tempo_sort += time.perf_counter() - t0

        # 4. Registra posições finais
        for idx, time_final in enumerate(tabela_ordenada):
            pos = idx + 1
            contagens[time_final.nome][pos] += 1

    tempo_total = time.perf_counter() - t_inicio

    # Compila as estatísticas finais
    estatisticas: list[EstatisticasTime] = []
    for t_orig in tabela_inicial:
        nome = t_orig.nome
        dist = contagens[nome]

        vezes_titulo = dist.get(1, 0)
        vezes_continental = sum(dist.get(p, 0) for p in range(1, top_k + 1))
        vezes_rebaixado = sum(
            dist.get(p, 0) for p in range(primeiro_rebaixado_pos, n_times + 1)
        )
        pos_media = sum(p * dist.get(p, 0) for p in range(1, n_times + 1)) / num_simulacoes

        estatisticas.append(
            EstatisticasTime(
                nome=nome,
                pontos_iniciais=pontos_iniciais[nome],
                prob_titulo=(vezes_titulo / num_simulacoes) * 100.0,
                prob_continental=(vezes_continental / num_simulacoes) * 100.0,
                prob_rebaixamento=(vezes_rebaixado / num_simulacoes) * 100.0,
                posicao_media=pos_media,
                distribuicao_posicoes=dist,
            )
        )

    # Ordena as estatísticas para exibição (da menor posição média para a maior)
    estatisticas.sort(key=lambda e: (e.posicao_media, -e.prob_titulo))

    return ResultadoMonteCarlo(
        estatisticas=estatisticas,
        num_simulacoes=num_simulacoes,
        algoritmo=nome_alg,
        tempo_execucao=tempo_total,
        top_continental=top_k,
        rebaixamento_n=reb_r,
        tempo_ordenacao=tempo_sort,
    )