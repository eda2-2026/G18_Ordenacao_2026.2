"""Testes unitários para o módulo modelos.py."""

from pathlib import Path
import pytest
from src.modelos import (
    Time,
    Jogo,
    configurar_criterios,
    obter_criterios,
    carregar_classificacao,
    carregar_jogos,
)


def test_time_propriedades_e_saldo():
    t = Time(
        nome="Alpha FC",
        pontos=12,
        vitorias=4,
        gols_pro=10,
        gols_contra=15,
        ataque=1.2,
        defesa=0.9,
    )
    assert t.saldo == -5
    assert t.chave() == (12, 4, -5, 10)


def test_time_copia():
    t1 = Time("Beta FC", pontos=9, vitorias=3, gols_pro=8, gols_contra=4)
    t2 = t1.copiar()
    assert t1 == t2
    assert t1 is not t2
    t2.pontos += 3
    assert t1.pontos == 9
    assert t2.pontos == 12


def test_criterios_configuraveis():
    t = Time("Gamma FC", pontos=10, vitorias=2, gols_pro=20, gols_contra=5)
    # Padrão: (pontos, vitorias, saldo, gols_pro)
    assert t.chave() == (10, 2, 15, 20)

    # Reconfigura globalmente para saldo antes de vitórias
    configurar_criterios(("pontos", "saldo", "vitorias", "gols_pro"))
    assert obter_criterios() == ("pontos", "saldo", "vitorias", "gols_pro")
    assert t.chave() == (10, 15, 2, 20)

    # Passa critérios pontuais no método
    assert t.chave(criterios=("gols_pro", "pontos")) == (20, 10)


def test_criterio_invalido():
    t = Time("Delta FC", pontos=5)
    with pytest.raises(AttributeError):
        t.chave(criterios=("inexistente",))


def test_carregar_dados_csv():
    base_dir = Path(__file__).resolve().parent.parent / "data"
    times = carregar_classificacao(base_dir / "classificacao.csv")
    assert len(times) == 6
    assert times[0].nome == "Aurora FC"
    assert times[0].pontos == 10
    assert times[0].saldo == 5

    jogos = carregar_jogos(base_dir / "jogos_restantes.csv")
    assert len(jogos) == 6
    assert isinstance(jogos[0], Jogo)
    assert jogos[0].mandante == "Aurora FC"
    assert jogos[0].visitante == "Dragao AC"
