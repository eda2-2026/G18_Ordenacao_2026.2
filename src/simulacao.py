"""Módulo de simulação de partidas com distribuição de Poisson (Algoritmo de Knuth).

HIPÓTESES DO MODELO (SIMPLIFICADO):
1. Processo de Poisson Homogêneo: Assume-se que os gols ocorrem aleatoriamente
   ao longo dos 90 minutos com uma taxa média constante (lambda).
2. Independência Marginal: O número de gols do time mandante é estatisticamente
   independente dos gols do visitante condicionado às suas taxas médias esperadas.
3. Decomposição Multiplicativa: O número esperado de gols de uma equipe é modelado
   como o produto de sua capacidade ofensiva (ataque), da fragilidade defensiva
   do oponente (defesa), de uma taxa basal de gols da competição e do fator casa.
4. Forças Estáticas: As métricas de ataque e defesa dos clubes permanecem fixas
   durante todas as rodadas restantes simuladas.

LIMITAÇÕES DO MODELO (NÃO VALIDADO EMPIRICAMENTE):
1. Não Calibrado: Os parâmetros de ataque e defesa utilizados são fictícios e
   didáticos, sem calibração estatística formal (ex.: Máxima Verossimilhança)
   sobre campeonatos reais.
2. Equidispersão Estrita da Poisson: A distribuição de Poisson impõe que a
   variância seja igual à média, ignorando possíveis efeitos de superdispersão.
3. Ausência de Correlação em Baixos Escores: No futebol real, empates como 0x0
   e 1x1 costumam ter probabilidade ligeiramente superior à Poisson independente
   (fenômeno modelado por Poisson Bivariada ou correções de Dixon & Coles).
4. Desconsideração de Fatores Dinâmicos: O modelo não considera cartões vermelhos,
   desgaste físico, lesões, clima, pressão psicológica ou ajustes táticos reativos.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional
from src.modelos import Time


@dataclass(frozen=True)
class ResultadoJogo:
    """Registra o placar observado em uma partida simulada."""

    mandante: str
    visitante: str
    gols_mandante: int
    gols_visitante: int


def poisson_knuth(lam: float, rng: Optional[random.Random] = None) -> int:
   
    if lam <= 0.0:
        return 0

    rand_func = rng.random if rng is not None else random.random
    limiar = math.exp(-lam)
    k = 0
    p = 1.0

    while p > limiar:
        k += 1
        p *= rand_func()

    return k - 1


def calcular_lambdas(
    time_mandante: Time,
    time_visitante: Time,
    fator_casa: float = 1.15,
    base_gols: float = 1.30,
) -> tuple[float, float]:
    """Calcula a expectativa de gols (lambda) para mandante e visitante."""
    # Mandante se beneficia do fator casa multiplicativo
    lambda_mandante = time_mandante.ataque * time_visitante.defesa * fator_casa * base_gols
    # Visitante sofre a defesa do mandante sem o fator casa
    lambda_visitante = time_visitante.ataque * time_mandante.defesa * base_gols

    # Garante um limite inferior para evitar taxas não-físicas
    lambda_mandante = max(0.05, float(lambda_mandante))
    lambda_visitante = max(0.05, float(lambda_visitante))

    return lambda_mandante, lambda_visitante


def simular_jogo(
    mandante: Time,
    visitante: Time,
    fator_casa: float = 1.15,
    base_gols: float = 1.30,
    rng: Optional[random.Random] = None,
) -> ResultadoJogo:
    """Simula uma partida entre dois times e atualiza seus pontos, vitórias e gols in-place."""
    lam_mandante, lam_visitante = calcular_lambdas(
        mandante, visitante, fator_casa=fator_casa, base_gols=base_gols
    )

    gols_m = poisson_knuth(lam_mandante, rng=rng)
    gols_v = poisson_knuth(lam_visitante, rng=rng)

    # Atualização dos gols pró e contra
    mandante.gols_pro += gols_m
    mandante.gols_contra += gols_v
    visitante.gols_pro += gols_v
    visitante.gols_contra += gols_m

    # Atualização de pontuação e vitórias
    if gols_m > gols_v:
        mandante.pontos += 3
        mandante.vitorias += 1
    elif gols_m < gols_v:
        visitante.pontos += 3
        visitante.vitorias += 1
    else:
        mandante.pontos += 1
        visitante.pontos += 1

    return ResultadoJogo(
        mandante=mandante.nome,
        visitante=visitante.nome,
        gols_mandante=gols_m,
        gols_visitante=gols_v,
    )
