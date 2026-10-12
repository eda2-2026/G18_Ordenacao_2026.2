"""Testes automatizados para os algoritmos de ordenação da tabela.

Utiliza sorted(..., key=lambda t: t.chave(), reverse=True) estritamente como
gabarito para validação das implementações próprias.
"""

from __future__ import annotations

import random
import pytest
from src.modelos import Time
from src.ordenacao import (
    insertion_sort,
    merge_sort,
    quick_sort,
    heap_sort,
    radix_lsd_multicriterio,
    ordenar_tabela,
    ALGORITMOS,
)


@pytest.fixture
def gabarito():
    """Função auxiliar de gabarito oficial baseada em sorted() do Python."""
    return lambda times: sorted(times, key=lambda t: t.chave(), reverse=True)



# Testes de Casos Limítrofes (Lista Vazia e Um Elemento)


@pytest.mark.parametrize("algoritmo", ["insertion", "merge", "quick", "heap", "radix"])
def test_lista_vazia(algoritmo: str):
    """Garante que todos os algoritmos tratam lista vazia sem erros."""
    times: list[Time] = []
    resultado = ordenar_tabela(times, algoritmo=algoritmo)
    assert resultado == []


@pytest.mark.parametrize("algoritmo", ["insertion", "merge", "quick", "heap", "radix"])
def test_um_elemento(algoritmo: str):
    """Garante que todos os algoritmos tratam lista unitária corretamente."""
    times = [Time("Unico FC", pontos=10, vitorias=3, gols_pro=5, gols_contra=2)]
    resultado = ordenar_tabela(times, algoritmo=algoritmo)
    assert len(resultado) == 1
    assert resultado[0].nome == "Unico FC"



# Testes com Lista de Amostra Padrão (Sem empates totais)



def test_ordenacao_estavel_amostra(times_amostra, gabarito):
    """Testa algoritmos estáveis (Insertion e Merge) contra o gabarito."""
    esperado = gabarito(times_amostra)

    assert insertion_sort(times_amostra) == esperado
    assert merge_sort(times_amostra) == esperado
    # Radix com desempate_nome=False preserva estabilidade pura dos critérios
    assert radix_lsd_multicriterio(times_amostra, desempate_nome=False) == esperado


def test_ordenacao_instavel_amostra(times_amostra, gabarito):
    """Testa algoritmos instáveis (Quick e Heap) comparando tuplas de chave()."""
    esperado_chaves = [t.chave() for t in gabarito(times_amostra)]

    res_quick = quick_sort(times_amostra)
    assert [t.chave() for t in res_quick] == esperado_chaves

    res_heap = heap_sort(times_amostra)
    assert [t.chave() for t in res_heap] == esperado_chaves



# Testes com Empates Parciais e Saldo Negativo


def test_empates_parciais_e_saldo_negativo(times_com_empates, gabarito):
    """Verifica desempate por critérios sucessivos (pontos -> vitórias -> saldo -> GP)
    e o correto ordenamento de saldos negativos."""
    esperado = gabarito(times_com_empates)
    esperado_chaves = [t.chave() for t in esperado]

    # Insertion e Merge preservam estabilidade de entrada
    assert insertion_sort(times_com_empates) == esperado
    assert merge_sort(times_com_empates) == esperado
    assert radix_lsd_multicriterio(times_com_empates, desempate_nome=False) == esperado

    # Quick e Heap comparam chaves
    res_quick = quick_sort(times_com_empates)
    assert [t.chave() for t in res_quick] == esperado_chaves

    res_heap = heap_sort(times_com_empates)
    assert [t.chave() for t in res_heap] == esperado_chaves



# Testes com Empates Totais e Desempate por Nome


def test_empates_totais_chaves():
    """Times com exatamente as mesmas estatísticas."""
    times = [
        Time("Zeta FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
        Time("Alfa FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
        Time("Beta FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
    ]

    # Para quick e heap, as chaves devem ser iguais
    for alg in ["insertion", "merge", "quick", "heap", "radix"]:
        res = ordenar_tabela(times, algoritmo=alg)
        assert len(res) == 3
        assert all(t.chave() == (10, 3, 4, 8) for t in res)


def test_radix_desempate_deterministico_por_nome():
    """Valida que o Radix LSD com desempate_nome=True coloca empates totais em ordem A-Z."""
    times = [
        Time("Zeta FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
        Time("Alfa FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
        Time("Beta FC", pontos=10, vitorias=3, gols_pro=8, gols_contra=4),
    ]
    res = radix_lsd_multicriterio(times, desempate_nome=True)
    nomes_ordenados = [t.nome for t in res]
    assert nomes_ordenados == ["Alfa FC", "Beta FC", "Zeta FC"]



# Testes com Listas Já Ordenadas e Invertidas


def test_lista_ja_ordenada(times_amostra, gabarito):
    """Verifica comportamento em listas previamente ordenadas."""
    ordenada = gabarito(times_amostra)
    esperado_chaves = [t.chave() for t in ordenada]

    assert insertion_sort(ordenada) == ordenada
    assert merge_sort(ordenada) == ordenada
    assert [t.chave() for t in quick_sort(ordenada)] == esperado_chaves
    assert [t.chave() for t in heap_sort(ordenada)] == esperado_chaves
    assert radix_lsd_multicriterio(ordenada, desempate_nome=False) == ordenada


def test_lista_invertida(times_amostra, gabarito):
    """Verifica ordenação de lista em ordem estritamente crescente."""
    invertida = sorted(times_amostra, key=lambda t: t.chave(), reverse=False)
    esperado = gabarito(times_amostra)
    esperado_chaves = [t.chave() for t in esperado]

    assert [t.chave() for t in insertion_sort(invertida)] == esperado_chaves
    assert [t.chave() for t in merge_sort(invertida)] == esperado_chaves
    assert [t.chave() for t in quick_sort(invertida)] == esperado_chaves
    assert [t.chave() for t in heap_sort(invertida)] == esperado_chaves
    assert [t.chave() for t in radix_lsd_multicriterio(invertida, desempate_nome=False)] == esperado_chaves



# Teste de Robustez com Massa de Dados Aleatória


def test_massa_aleatoria_50_times(gabarito):
    """Gera 50 times fictícios com valores aleatórios e testa todos os algoritmos."""
    rng = random.Random(42)
    times: list[Time] = []
    for i in range(50):
        gp = rng.randint(0, 30)
        gc = rng.randint(0, 30)
        times.append(
            Time(
                nome=f"Time_{i:02d}",
                pontos=rng.randint(0, 45),
                vitorias=rng.randint(0, 15),
                gols_pro=gp,
                gols_contra=gc,
            )
        )

    esperado = gabarito(times)
    esperado_chaves = [t.chave() for t in esperado]

    # Validações estáveis
    assert [t.chave() for t in insertion_sort(times)] == esperado_chaves
    assert [t.chave() for t in merge_sort(times)] == esperado_chaves
    assert [t.chave() for t in radix_lsd_multicriterio(times, desempate_nome=False)] == esperado_chaves

    # Validações instáveis
    assert [t.chave() for t in quick_sort(times)] == esperado_chaves
    assert [t.chave() for t in heap_sort(times)] == esperado_chaves


def test_algoritmo_invalido():
    """Garante erro explicativo para algoritmo não suportado."""
    with pytest.raises(ValueError, match="Algoritmo desconhecido"):
        ordenar_tabela([], algoritmo="inexistente")
