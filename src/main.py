from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Garante importações a partir da raiz do repositório
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.modelos import carregar_classificacao, carregar_jogos
from src.montecarlo import executar_monte_carlo
from src.ordenacao import ALGORITMOS


def formatar_tabela_probabilidades(resultado) -> str:
    """Gera uma tabela formatada em texto para exibição no terminal."""
    linhas: list[str] = []
    cabecalho = (
        f"{'Pos. Média':>10} | {'Time':<16} | {'Pts Iniciais':>12} | "
        f"{'Título (%)':>10} | {'Continental (%)':>15} | {'Rebaixamento (%)':>16}"
    )
    separador = "-" * len(cabecalho)

    linhas.append("\n" + separador)
    linhas.append(" TABELA DE PROBABILIDADES ESTIMADAS VIA MONTE CARLO")
    linhas.append(separador)
    linhas.append(cabecalho)
    linhas.append(separador)

    for est in resultado.estatisticas:
        linha = (
            f"{est.posicao_media:10.2f} | "
            f"{est.nome:<16} | "
            f"{est.pontos_iniciais:12d} | "
            f"{est.prob_titulo:9.2f}% | "
            f"{est.prob_continental:14.2f}% | "
            f"{est.prob_rebaixamento:15.2f}%"
        )
        linhas.append(linha)

    linhas.append(separador)
    linhas.append(
        f"Algoritmo: {resultado.algoritmo.upper()} | "
        f"Simulações: {resultado.num_simulacoes:,} | "
        f"Tempo: {resultado.tempo_execucao:.4f}s | "
        f"Taxa: {resultado.num_simulacoes / max(1e-6, resultado.tempo_execucao):,.0f} sim/s"
    )
    linhas.append(
        f"Critérios das faixas: Título (1º), Vaga Continental (Top {resultado.top_continental}), "
        f"Rebaixamento (Últimos {resultado.rebaixamento_n})"
    )
    linhas.append(separador + "\n")

    return "\n".join(linhas)


def construir_parser() -> argparse.ArgumentParser:
    """Constrói o parser de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Estima probabilidades no campeonato de futebol via Monte Carlo.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--algoritmo",
        type=str,
        default="merge",
        choices=list(ALGORITMOS.keys()),
        help="Algoritmo de ordenação utilizado na tabela a cada simulação.",
    )
    parser.add_argument(
        "--simulacoes",
        type=int,
        default=1000,
        help="Quantidade de simulações de Monte Carlo a executar.",
    )
    parser.add_argument(
        "--dados",
        type=str,
        default="data",
        help="Diretório onde se encontram 'classificacao.csv' e 'jogos_restantes.csv'.",
    )
    parser.add_argument(
        "--top-continental",
        type=int,
        default=2,
        help="Quantidade de equipes que se classificam para vagas continentais (Top K).",
    )
    parser.add_argument(
        "--rebaixamento",
        type=int,
        default=2,
        help="Quantidade de equipes que são rebaixadas (Últimos R).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente do gerador de números aleatórios para reprodutibilidade.",
    )
    return parser


def main() -> None:
    """Ponto de entrada principal da CLI."""
    parser = construir_parser()
    args = parser.parse_args()

    diretorio_dados = Path(args.dados)
    caminho_classificacao = diretorio_dados / "classificacao.csv"
    caminho_jogos = diretorio_dados / "jogos_restantes.csv"

    if not caminho_classificacao.exists():
        print(f"Erro: Arquivo '{caminho_classificacao}' não encontrado.", file=sys.stderr)
        sys.exit(1)
    if not caminho_jogos.exists():
        print(f"Erro: Arquivo '{caminho_jogos}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    times = carregar_classificacao(caminho_classificacao)
    jogos = carregar_jogos(caminho_jogos)

    print(
        f"Iniciando simulação com {len(times)} times e {len(jogos)} jogos restantes..."
    )

    resultado = executar_monte_carlo(
        tabela_inicial=times,
        jogos_restantes=jogos,
        num_simulacoes=args.simulacoes,
        algoritmo=args.algoritmo,
        top_continental=args.top_continental,
        rebaixamento_n=args.rebaixamento,
        seed=args.seed,
    )

    tabela_texto = formatar_tabela_probabilidades(resultado)
    print(tabela_texto)


if __name__ == "__main__":
    main()