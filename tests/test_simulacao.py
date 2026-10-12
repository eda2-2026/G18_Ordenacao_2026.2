"""Testes unitários para o módulo de simulação e distribuição de Poisson."""

from __future__ import annotations

import math
import random
import pytest
from src.modelos import Time
from src.simulacao import (
    poisson_knuth,
    calcular_lambdas,
    simular_jogo,
    ResultadoJogo,
)


def test_poisson_knuth_casos_limites():
    """Valida comportamento de Poisson para lambda <= 0."""
    assert poisson_knuth(0.0) == 0
    assert poisson_knuth(-2.5) == 0


def test_poisson_knuth_reprodutibilidade():
    """Garante que a mesma semente produz os mesmos valores de gols."""
    rng1 = random.Random(12345)
    rng2 = random.Random(12345)

    amostras1 = [poisson_knuth(1.8, rng1) for _ in range(50)]
    amostras2 = [poisson_knuth(1.8, rng2) for _ in range(50)]

    assert amostras1 == amostras2


def test_poisson_knuth_convergencia_media():
    """Verifica pela Lei dos Grandes Números se a média amostral converge para lambda."""
    lam = 2.4
    n_amostras = 20_000
    rng = random.Random(999)

    amostras = [poisson_knuth(lam, rng) for _ in range(n_amostras)]
    media = sum(amostras) / n_amostras

    # Erro padrão da média é sqrt(lambda / N)
    erro_padrao = math.sqrt(lam / n_amostras)
    # 4 erros padrão cobre > 99.99% dos casos
    assert abs(media - lam) < 4 * erro_padrao


def test_calcular_lambdas():
    t_casa = Time("Casa FC", ataque=1.5, defesa=0.8)
    t_fora = Time("Fora FC", ataque=1.0, defesa=1.2)

    lam_c, lam_f = calcular_lambdas(t_casa, t_fora, fator_casa=1.2, base_gols=1.3)
    # lam_c = 1.5 * 1.2 * 1.2 * 1.3 = 2.808
    # lam_f = 1.0 * 0.8 * 1.3 = 1.04
    assert pytest.approx(lam_c, 0.001) == 2.808
    assert pytest.approx(lam_f, 0.001) == 1.04


def test_simular_jogo_vitoria_mandante():
    """Simula com semente controlada e confere atualização dos dados."""
    casa = Time("Casa FC", pontos=0, vitorias=0, gols_pro=0, gols_contra=0, ataque=5.0, defesa=0.1)
    fora = Time("Fora FC", pontos=0, vitorias=0, gols_pro=0, gols_contra=0, ataque=0.1, defesa=5.0)

    # Forças muito desbalanceadas favorecem vitória da casa
    rng = random.Random(42)
    res = simular_jogo(casa, fora, rng=rng)

    assert isinstance(res, ResultadoJogo)
    assert res.mandante == "Casa FC"
    assert res.visitante == "Fora FC"
    assert casa.gols_pro == res.gols_mandante
    assert casa.gols_contra == res.gols_visitante
    assert fora.gols_pro == res.gols_visitante
    assert fora.gols_contra == res.gols_mandante

    if res.gols_mandante > res.gols_visitante:
        assert casa.pontos == 3
        assert casa.vitorias == 1
        assert fora.pontos == 0
        assert fora.vitorias == 0
    elif res.gols_mandante == res.gols_visitante:
        assert casa.pontos == 1
        assert fora.pontos == 1
    else:
        assert fora.pontos == 3
        assert fora.vitorias == 1
        assert casa.pontos == 0


def test_simular_jogo_conservacao_gols_e_pontos():
    """Valida propriedades de conservação em 100 partidas simuladas."""
    rng = random.Random(77)
    for _ in range(100):
        t1 = Time("T1", ataque=1.2, defesa=1.1)
        t2 = Time("T2", ataque=1.1, defesa=1.2)
        res = simular_jogo(t1, t2, rng=rng)

        # Saldo líquido da partida entre as duas equipes deve somar zero
        assert t1.saldo + t2.saldo == 0
        # Pontuação total distribuída deve ser 3 (vitória) ou 2 (empate)
        assert (t1.pontos + t2.pontos) in (2, 3)
