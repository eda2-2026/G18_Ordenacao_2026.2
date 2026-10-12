from __future__ import annotations

from pathlib import Path
import pytest
from src.modelos import Time, Jogo, carregar_classificacao, carregar_jogos
from src.montecarlo import executar_monte_carlo
from src.main import formatar_tabela_probabilidades, construir_parser


@pytest.fixture
def dados_reais():
    base = Path(__file__).resolve().parent.parent / "data"
    times = carregar_classificacao(base / "classificacao.csv")
    jogos = carregar_jogos(base / "jogos_restantes.csv")
    return times, jogos


def test_monte_carlo_soma_probabilidades_titulo(dados_reais):
    times, jogos = dados_reais
    resultado = executar_monte_carlo(
        tabela_inicial=times,
        jogos_restantes=jogos,
        num_simulacoes=500,
        algoritmo="merge",
        seed=42,
    )

    # A probabilidade de exatamente um campeão por simulação implica soma = 100%
    soma_titulo = sum(e.prob_titulo for e in resultado.estatisticas)
    assert pytest.approx(soma_titulo, 0.01) == 100.0


def test_monte_carlo_reprodutibilidade(dados_reais):
    times, jogos = dados_reais
    r1 = executar_monte_carlo(times, jogos, num_simulacoes=200, seed=123)
    r2 = executar_monte_carlo(times, jogos, num_simulacoes=200, seed=123)

    for e1, e2 in zip(r1.estatisticas, r2.estatisticas):
        assert e1.nome == e2.nome
        assert e1.prob_titulo == e2.prob_titulo
        assert e1.prob_continental == e2.prob_continental
        assert e1.prob_rebaixamento == e2.prob_rebaixamento
        assert e1.posicao_media == e2.posicao_media


def test_monte_carlo_faixas_configuraveis(dados_reais):
    times, jogos = dados_reais
    # Apenas 1 vaga continental e 1 rebaixado
    resultado = executar_monte_carlo(
        times,
        jogos,
        num_simulacoes=200,
        top_continental=1,
        rebaixamento_n=1,
        seed=10,
    )
    # Com top_continental=1, prob_continental deve ser idêntica à prob_titulo
    for est in resultado.estatisticas:
        assert pytest.approx(est.prob_continental, 0.001) == est.prob_titulo


def test_monte_carlo_tabela_vazia():
    resultado = executar_monte_carlo(
        tabela_inicial=[],
        jogos_restantes=[],
        num_simulacoes=100,
    )
    assert resultado.estatisticas == []
    assert resultado.num_simulacoes == 100


def test_monte_carlo_simulacoes_invalidas(dados_reais):
    times, jogos = dados_reais
    with pytest.raises(ValueError, match="maior que zero"):
        executar_monte_carlo(times, jogos, num_simulacoes=0)


def test_formatacao_tabela(dados_reais):
    times, jogos = dados_reais
    resultado = executar_monte_carlo(times, jogos, num_simulacoes=50, seed=42)
    texto = formatar_tabela_probabilidades(resultado)
    assert "TABELA DE PROBABILIDADES ESTIMADAS VIA MONTE CARLO" in texto
    assert "Palmeiras" in texto
    assert "MERGE" in texto


def test_cli_parser():
    parser = construir_parser()
    args = parser.parse_args(["--algoritmo", "radix", "--simulacoes", "500"])
    assert args.algoritmo == "radix"
    assert args.simulacoes == 500
    assert args.top_continental == 6
    assert args.rebaixamento == 4


def test_monte_carlo_mesmo_resultado_entre_algoritmos(dados_reais):
    """Garante que com a mesma semente, todos os 5 algoritmos geram exatamente as mesmas probabilidades."""
    times, jogos = dados_reais
    resultados = {}
    for alg in ["insertion", "merge", "quick", "heap", "radix"]:
        res = executar_monte_carlo(
            tabela_inicial=times,
            jogos_restantes=jogos,
            num_simulacoes=200,
            algoritmo=alg,
            seed=7,
        )
        resultados[alg] = [
            (
                e.nome,
                e.prob_titulo,
                e.prob_continental,
                e.prob_rebaixamento,
                round(e.posicao_media, 4),
            )
            for e in res.estatisticas
        ]

    gabarito = resultados["merge"]
    for alg in ["insertion", "quick", "heap", "radix"]:
        assert resultados[alg] == gabarito


def test_monte_carlo_nao_altera_tabela_original(dados_reais):
    """Garante que a tabela inicial passada não sofre mutações durante o Monte Carlo."""
    times, jogos = dados_reais
    estado_anterior = [
        (t.nome, t.pontos, t.vitorias, t.gols_pro, t.gols_contra, t.saldo)
        for t in times
    ]
    executar_monte_carlo(times, jogos, num_simulacoes=100, seed=42)
    estado_posterior = [
        (t.nome, t.pontos, t.vitorias, t.gols_pro, t.gols_contra, t.saldo)
        for t in times
    ]
    assert estado_anterior == estado_posterior

