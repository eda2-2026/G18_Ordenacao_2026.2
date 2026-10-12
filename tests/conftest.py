"""Configuração e fixtures comuns para os testes do pytest."""

from __future__ import annotations

import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para imports de 'src'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.modelos import Time, configurar_criterios


@pytest.fixture(autouse=True)
def restaurar_criterios_padrao():
    """Garante que a ordem de critérios seja restaurada após cada teste."""
    configurar_criterios(("pontos", "vitorias", "saldo", "gols_pro"))
    yield
    configurar_criterios(("pontos", "vitorias", "saldo", "gols_pro"))


@pytest.fixture
def times_amostra() -> list[Time]:
    """Retorna uma lista variada de times para testes de ordenação."""
    return [
        Time("Dragao AC", pontos=7, vitorias=2, gols_pro=6, gols_contra=8),     # saldo -2
        Time("Aurora FC", pontos=10, vitorias=3, gols_pro=9, gols_contra=4),    # saldo +5
        Time("Fenix SC", pontos=4, vitorias=1, gols_pro=3, gols_contra=8),      # saldo -5
        Time("Canario EC", pontos=9, vitorias=2, gols_pro=7, gols_contra=6),    # saldo +1
        Time("Borborema SC", pontos=10, vitorias=3, gols_pro=8, gols_contra=5), # saldo +3
        Time("Esperanca FC", pontos=6, vitorias=1, gols_pro=5, gols_contra=9),  # saldo -4
    ]


@pytest.fixture
def times_com_empates() -> list[Time]:
    """Retorna times com empates parciais e totais para validar desempates."""
    return [
        # Empate total em todos os critérios numéricos
        Time("Time B", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),  # saldo 4
        Time("Time A", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),  # saldo 4
        # Empate parcial: mesmos pontos e vitorias, mas saldo diferente
        Time("Time C", pontos=10, vitorias=3, gols_pro=7, gols_contra=4),  # saldo 3
        # Empate parcial: mesmos pontos, mas vitorias diferentes
        Time("Time D", pontos=10, vitorias=2, gols_pro=10, gols_contra=2), # saldo 8
        # Time com saldo negativo expressivo
        Time("Time E", pontos=3, vitorias=1, gols_pro=2, gols_contra=12),  # saldo -10
    ]
