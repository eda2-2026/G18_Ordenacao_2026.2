from __future__ import annotations

import pytest
from benchmark.benchmark import (
    gerar_cenario_sintetico,
    rodar_benchmark_monte_carlo,
)


def test_gerar_cenario_sintetico():
    times, jogos = gerar_cenario_sintetico(10, seed=42)
    assert len(times) == 10
    assert len(jogos) > 0
    assert times[0].nome == "Time_0000"


def test_rodar_benchmark_resumido():
    # Roda uma versão rápida com N pequeno para garantir ausência de erros
    registros = rodar_benchmark_monte_carlo(
        n_times_lista=[6],
        simulacoes_grid={6: 5},
    )
    assert len(registros) > 0
    algs = {r.algoritmo for r in registros}
    assert "insertion" in algs
    assert "merge" in algs
    assert "quick" in algs
    assert "heap" in algs
    assert "radix" in algs
    assert "sorted_python" in algs


def test_comparar_ja_ordenada_vs_embaralhada_com_repeticoes(capsys):
    from benchmark.benchmark import (
        comparar_ja_ordenada_vs_embaralhada,
        comparar_quase_ordenada_vs_embaralhada,
    )
    # Executa com N pequeno e 3 repetições
    comparar_ja_ordenada_vs_embaralhada(n=10, seed=42, repeticoes=3)
    out1 = capsys.readouterr().out
    assert "CONTRASTE DE ENTRADA" in out1
    assert "Mediana de 3 repetições" in out1
    assert "insertion" in out1

    # Testa o alias de retrocompatibilidade
    comparar_quase_ordenada_vs_embaralhada(n=10, seed=42, repeticoes=3)
    out2 = capsys.readouterr().out
    assert "CONTRASTE DE ENTRADA" in out2

